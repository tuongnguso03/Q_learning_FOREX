import pandas as pd
from sklearn.cluster import KMeans


df = pd.read_csv('forex_data_2000.csv')
#ema200s = df['200EMA']


def run_kmeans(data, num_clusters):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit([[x] for x in data])
    k_centers = [round(center[0], 4) for center in kmeans.cluster_centers_]
    return k_centers


# 1st feature: price

def bin_price(df, n_bins):
    highest = df.loc[df['High'].idxmax()]['High']
    lowest = df.loc[df['Low'].idxmin()]['Low']
    diff = highest - lowest
    bin_size = round(diff / n_bins, 4)
    return bin_size, highest, lowest



def build_bin_price(n_bins):
    bins = [df.loc[df['Low'].idxmin()]['Low']]
    bin_size = bin_price(df, n_bins)[0]
    for i in range(n_bins):
        bins.append(round((bins[-1] + bin_size), 4))
    return bins


def get_price_group(price: float, bins):
    for b in bins:
        if price < b:
            return b 


# 2nd feature: distance to zone
def calculate_toZone(df):
    strong_zones = [1.22176, 1.19554, 1.17464, 1.16199, 1.14506, 1.1297, 1.11691, 
                  1.10246, 1.08274, 1.05433, 1.03592, 1.01287, 1.00216, 0.96357]
    
    distance_to_zone = []
    for price in df['Price']:
        closest_zone = strong_zones[0]
        min_distance = abs(price - closest_zone)
        for zone in strong_zones:
            distance = abs(price - zone)
            if distance < min_distance:
                min_distance = distance
                closest_zone = zone
        
        distance_to_zone.append(round(min_distance,9))

    return distance_to_zone
        

# 3rd feature: kangaroo tail score
def trend200(lastema200, ema200):
    trend200 = (ema200 - lastema200) / lastema200
    return trend200

def trend20(lastema20, ema20):
    trend20 = (ema20 - lastema20) / lastema20
    return trend20    


def kangaroo_tail(price, open, high, low, ema200: float, lastema200: float, ema20: float, lastema20: float):
    if price >= open:
        up, down = price, open
    else:
        up, down = open, price
    microtrend = trend20(lastema20, ema20)
    if high - up >= down - low:
        score = (high - low) / (up - low) * (1 + trend200(lastema200, ema200))
    else:
        score = (high - low) / (high - down) * (1 - trend200(lastema200, ema200))
    
    return 1000 * (high - low) * score

    # 1000 multiplier is to convert to pips.

def calculate_kt_score(df):
    kt_score = []
    for i in range(len(df)):
        if i == len(df) - 2:
            kt_score.extend([0,0])
            break
        score = kangaroo_tail(df.loc[i + 1, 'Price'], df.loc[i + 1, 'Open'], df.loc[i + 1, 'High'],
                              df.loc[i + 1, 'Low'], df.loc[i + 1, '200EMA'], df.loc[i, '200EMA'], 
                              df.loc[i + 1, '20EMA'], df.loc[i, '20EMA'])
        kt_score.append(score)
    
    return kt_score


# 4th feature: big shadow score
def big_shadow(price1, open1, ema200, ema20, price2, open2, lastema200, lastema20) -> float:
    # Need input of previous day's data:
    direction = None
    score = 0
    microtrend = trend20(lastema20, ema20)
    
    def direction(price, open) -> str:
        if price >= open:
            return "up"
        else:
            return "down"

    
    mainDirection = direction(price1, open1)
    infDirection = direction(price2, open2)
    if mainDirection == infDirection:
        return 0
    else:
        if open2 - price2 == 0:
            return 0
        if mainDirection == "up":
            score = (price1 - open1) / (open2 - price2) * (1 - trend200(lastema200, ema200))
        else:
            score = (open1 - price1) / (price2 - open2) * (1 + trend200(lastema200, ema200))

        return 1000 * abs(price1 - open1) * score


def calculate_bs_score(df):
    bs_score = []
    for i in range(len(df)):
        if i == len(df) - 2:
            bs_score.extend([0,0])
            break
        score = big_shadow(df.loc[i+1, 'Price'], df.loc[i+1, 'Open'], df.loc[i+1, '200EMA'], df.loc[i + 1, '20EMA'],
                            df.loc[i, 'Price'], df.loc[i, 'Open'], df.loc[i, '200EMA'], df.loc[i, '20EMA'])
        bs_score.append(score)
    return bs_score


def dataset_with_indicators():
    processed_df = df.copy()
    processed_df['toZone'] = calculate_toZone(df)
    processed_df['kt_score'] = calculate_kt_score(df)
    processed_df['bs_score'] = calculate_bs_score(df)

    processed_df.to_csv('forex_data_with_indicators.csv', index=False)



df2 = pd.read_csv('forex_data_with_indicators.csv')


def build_bin_toZone(n_bins):
    values = df2['toZone'].tolist()
    k = n_bins
    k_centers = run_kmeans(values, k)
    return sorted(k_centers)


def get_toZone_group(price: float, bins):
    strong_zones = [1.22176, 1.19554, 1.17464, 1.16199, 1.14506, 1.1297, 1.11691, 
                  1.10246, 1.08274, 1.05433, 1.03592, 1.01287, 1.00216, 0.96357]
    closest_zone = strong_zones[0]
    min_distance = abs(price - closest_zone)
    for zone in strong_zones:
        distance = abs(price - zone)
        if distance < min_distance:
            min_distance = distance
            closest_zone = zone
    for b in bins:
        if min_distance < b:
            return b  
        

def build_bin_kt_score(n_bins):
    values = df2['kt_score'].tolist()
    k = n_bins
    k_centers = run_kmeans(values, k)
    return sorted(k_centers)


def get_kt_score_group(kt_score: float, bins):
    closest_center = min(bins, key=lambda c: abs(kt_score - c))
    return closest_center


def build_bin_bs_score(n_bins):
    values = df2['bs_score'].tolist()
    k = n_bins
    k_centers = run_kmeans(values, k)
    return sorted(k_centers)


def get_bs_score_group(bs_score: float, bins):
    closest_center = min(bins, key=lambda c: abs(bs_score - c))
    return closest_center


#bins_price = build_bin_price(200)
#bins_to_zone = build_bin_toZone(10)
bins_kt_score = build_bin_kt_score(30)
bins_bs_score = build_bin_bs_score(30) 
#chay lan 1 xong thi comment out doan tren va thay bang doan nay

bins_price = [0.8227, 0.8266, 0.8305, 0.8344, 0.8383, 0.8422, 0.8461, 0.85, 0.8539, 0.8578, 0.8617, 0.8656, 0.8695, 0.8734, 0.8773, 0.8812, 0.8851, 0.889, 0.8929, 0.8968, 0.9007, 0.9046, 0.9085, 0.9124, 0.9163, 0.9202, 0.9241, 0.928, 0.9319, 0.9358, 0.9397, 0.9436, 0.9475, 0.9514, 0.9553, 0.9592, 0.9631, 0.967, 0.9709, 0.9748, 0.9787, 0.9826, 0.9865, 0.9904, 0.9943, 0.9982, 1.0021, 1.006, 1.0099, 1.0138, 1.0177, 1.0216, 1.0255, 1.0294, 1.0333, 1.0372, 1.0411, 1.045, 1.0489, 1.0528, 1.0567, 1.0606, 1.0645, 1.0684, 1.0723, 1.0762, 1.0801, 1.084, 1.0879, 1.0918, 1.0957, 1.0996, 1.1035, 1.1074, 1.1113, 1.1152, 1.1191, 1.123, 1.1269, 1.1308, 1.1347, 1.1386, 1.1425, 1.1464, 1.1503, 1.1542, 1.1581, 1.162, 1.1659, 1.1698, 1.1737, 1.1776, 1.1815, 1.1854, 1.1893, 1.1932, 1.1971, 1.201, 1.2049, 1.2088, 1.2127, 1.2166, 1.2205, 1.2244, 1.2283, 1.2322, 1.2361, 1.24, 1.2439, 1.2478, 1.2517, 1.2556, 1.2595, 1.2634, 1.2673, 1.2712, 1.2751, 1.279, 1.2829, 1.2868, 1.2907, 1.2946, 1.2985, 1.3024, 1.3063, 1.3102, 1.3141, 1.318, 1.3219, 1.3258, 1.3297, 1.3336, 1.3375, 1.3414, 1.3453, 1.3492, 1.3531, 1.357, 1.3609, 1.3648, 1.3687, 1.3726, 1.3765, 1.3804, 1.3843, 1.3882, 1.3921, 1.396, 1.3999, 1.4038, 1.4077, 1.4116, 1.4155, 1.4194, 1.4233, 1.4272, 1.4311, 1.435, 1.4389, 1.4428, 1.4467, 1.4506, 1.4545, 1.4584, 1.4623, 1.4662, 1.4701, 1.474, 1.4779, 1.4818, 1.4857, 1.4896, 1.4935, 1.4974, 1.5013, 1.5052, 1.5091, 1.513, 1.5169, 1.5208, 1.5247, 1.5286, 1.5325, 1.5364, 1.5403, 1.5442, 1.5481, 1.552, 1.5559, 1.5598, 1.5637, 1.5676, 1.5715, 1.5754, 1.5793, 1.5832, 1.5871, 1.591, 1.5949, 1.5988, 1.6027]
bins_to_zone = [0.0069, 0.0345, 0.059, 0.0823, 0.1079, 0.136, 0.1639, 0.2052, 0.2524, 0.3411]
bins_kt_score = [5.7015, 8.4971, 10.5743, 12.4964, 14.1776, 15.8714, 17.5226, 19.3354, 21.2215, 23.1309, 24.952, 26.8488, 28.9513, 31.4197, 33.7732, 37.0172, 40.6782, 45.0752, 48.7343, 53.9119, 60.2284, 65.1171, 72.5949, 82.6485, 92.6865, 114.3171, 135.7607, 152.2971, 167.1669, 242.0282]
bins_bs_score = [0.1762, 4.135, 9.2961, 15.7522, 23.4737, 32.3927, 45.1309, 59.1047, 76.2066, 95.293, 121.1409, 162.302, 201.0533, 245.6012, 283.5134, 311.4725, 356.2651, 405.8889, 465.185, 515.4309, 607.2788, 656.8748, 732.0883, 863.3603, 960.363, 1040.1805, 1167.0398, 1273.6709, 1347.9702, 2014.3181]

def print_bins():
    dataset_with_indicators()
    print('price:', bins_price)
    print('toZone:', bins_to_zone)
    print('kt_score:', bins_kt_score)
    print('bs_score:', bins_bs_score)


def day_to_state(data) -> tuple:
    #feature-based states go here
    days = []
    for index, row in data.iterrows():
        days.append(row)
    
    price = days[2]['Open']
    price1, open1, high1, low1, ema200, ema20 = days[1]['Price'], days[1]['Open'], days[1]['High'], days[1]['Low'], days[1]['200EMA'], days[1]['20EMA']
    price2, open2, high2, low2, lastema200, lastema20 = days[0]['Price'], days[0]['Open'], days[0]['High'], days[0]['Low'], days[0]['200EMA'], days[0]['20EMA']
    kt_score = kangaroo_tail(price1, open1, high1, low1, ema200, lastema200, ema20, lastema20)
    bs_score = big_shadow(price1, open1, ema200, ema20, price2, open2, lastema200, lastema20)

    price_gr = get_price_group(price, bins_price)
    to_zone_gr = get_toZone_group(price, bins_to_zone)
    kt_score_gr = get_kt_score_group(kt_score, bins_kt_score)
    bs_score_gr = get_bs_score_group(bs_score, bins_bs_score)

    return (price_gr, to_zone_gr, kt_score_gr, bs_score_gr)

