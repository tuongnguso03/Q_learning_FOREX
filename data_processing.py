import pandas as pd
from sklearn.cluster import KMeans


df = pd.read_csv('forex_data_train_1987-2017.csv')
#ema200s = df['200EMA']


def run_kmeans(data, num_clusters):
    df = pd.read_csv('forex_data_train_1987-2017.csv')
    dataset_with_indicators()
    i = 1
    kmeans = KMeans(n_clusters=num_clusters)
    for x in data:
        print(i, x)
        i += 1
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


def kangaroo_tail(price, open, high, low, ema200: float, lastema200: float):
    if price >= open:
        up, down = price, open
    else:
        up, down = open, price
    if high - up >= down - low:
        if up - low == 0:
            score = (high - low) * (1 + trend200(lastema200, ema200))
        else:
            score = (high - low) / (up - low) * (1 + trend200(lastema200, ema200))
    else:
        if high - down == 0:
            score = (high - low) * (1 + trend200(lastema200, ema200))
        else:
            score = (high - low) / (high - down) * (1 - trend200(lastema200, ema200))
    
    score = 1000 * (high - low) * score
    if score > 200:
        score = 200

    return score

    # 1000 multiplier is to convert to pips.

def calculate_kt_score(df):
    kt_score = []
    for i in range(len(df)):
        if i == len(df) - 2:
            kt_score.extend([0,0])
            break
        score = kangaroo_tail(df.loc[i + 1, 'Price'], df.loc[i + 1, 'Open'], df.loc[i + 1, 'High'],
                              df.loc[i + 1, 'Low'], df.loc[i + 1, '200EMA'], df.loc[i, '200EMA'])
        kt_score.append(score)
    
    return kt_score


# 4th feature: big shadow score
def big_shadow(price1, open1, ema200, price2, open2, lastema200) -> float:
    # Need input of previous day's data:
    direction = None
    score = 0
    

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
        
        score = 1000 * abs(price1 - open1) * score
        if score > 200:
            score = 200

        return score

def calculate_bs_score(df):
    bs_score = []
    for i in range(len(df)):
        if i == len(df) - 2:
            bs_score.extend([0,0])
            break
        score = big_shadow(df.loc[i+1, 'Price'], df.loc[i+1, 'Open'], df.loc[i+1, '200EMA'],
                            df.loc[i, 'Price'], df.loc[i, 'Open'], df.loc[i, '200EMA'])
        bs_score.append(score)
    return bs_score


def dataset_with_indicators():
    processed_df = df.copy()
    #processed_df['toZone'] = calculate_toZone(df)
    processed_df['kt_score'] = calculate_kt_score(df)
    processed_df['bs_score'] = calculate_bs_score(df)
    processed_df['max'] = processed_df[['kt_score', 'bs_score']].max(axis=1)

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


def build_bin_max_score(n_bins):
    #dataset_with_indicators()
    values = df2['max'].tolist()
    k = n_bins
    k_centers = run_kmeans(values, k)
    return sorted(k_centers)


def get_max_score_group(max_score: float, bins):
    closest_center = min(bins, key=lambda c: abs(max_score - c))
    return closest_center



#bins_price = build_bin_price(100)
#bins_to_zone = build_bin_toZone(10)
#bins_kt_score = build_bin_kt_score(5)
#bins_bs_score = build_bin_bs_score(5)
bins_max_score = build_bin_max_score(7)
#chay lan 1 xong thi comment out doan tren va thay bang doan nay

bins_price = [0.8227, 0.8305, 0.8383, 0.8461, 0.8539, 0.8617, 0.8695, 0.8773, 0.8851, 0.8929, 0.9007, 0.9085, 0.9163, 0.9241, 0.9319, 0.9397, 0.9475, 0.9553, 0.9631, 0.9709, 0.9787, 0.9865, 0.9943, 1.0021, 1.0099, 1.0177, 1.0255, 1.0333, 1.0411, 1.0489, 1.0567, 1.0645, 1.0723, 1.0801, 1.0879, 1.0957, 1.1035, 1.1113, 1.1191, 1.1269, 1.1347, 1.1425, 1.1503, 1.1581, 1.1659, 1.1737, 1.1815, 1.1893, 1.1971, 1.2049, 1.2127, 1.2205, 1.2283, 1.2361, 1.2439, 1.2517, 1.2595, 1.2673, 1.2751, 1.2829, 1.2907, 1.2985, 1.3063, 1.3141, 1.3219, 1.3297, 1.3375, 1.3453, 1.3531, 1.3609, 1.3687, 1.3765, 1.3843, 1.3921, 1.3999, 1.4077, 1.4155, 1.4233, 1.4311, 1.4389, 1.4467, 1.4545, 1.4623, 1.4701, 1.4779, 1.4857, 1.4935, 1.5013, 1.5091, 1.5169, 1.5247, 1.5325, 1.5403, 1.5481, 1.5559, 1.5637, 1.5715, 1.5793, 1.5871, 1.5949, 1.6027]
#bins_to_zone = [0.0069, 0.0345, 0.059, 0.0823, 0.1079, 0.136, 0.1639, 0.2052, 0.2524, 0.3411]
bins_kt_score = [13.4589, 28.4006, 57.9765, 111.9654, 192.6741]
bins_bs_score = [0.8891, 20.8994, 53.7304, 103.8988, 190.8977]
#bins_max_score = [10.7373, 20.6193, 33.9805, 54.5179, 82.9422, 117.8789, 157.9964, 198.8483]

def print_bins():
    dataset_with_indicators()
    print('price:', bins_price)
    #print('toZone:', bins_to_zone)
    print('kt_score:', bins_kt_score)
    print('bs_score:', bins_bs_score)
    print('max_score:', bins_max_score)


def day_to_state(data) -> tuple:
    #feature-based states go here
    days = []
    for index, row in data.iterrows():
        days.append(row)
    
    price = days[2]['Open']
    price1, open1, high1, low1, ema200 = days[1]['Price'], days[1]['Open'], days[1]['High'], days[1]['Low'], days[1]['200EMA']
    price2, open2, high2, low2, lastema200 = days[0]['Price'], days[0]['Open'], days[0]['High'], days[0]['Low'], days[0]['200EMA']
    kt_score = kangaroo_tail(price1, open1, high1, low1, ema200, lastema200)
    bs_score = big_shadow(price1, open1, ema200, price2, open2, lastema200)
    max_score = max(kt_score, bs_score)

    price_gr = get_price_group(price, bins_price)
    #to_zone_gr = get_toZone_group(price, bins_to_zone)
    kt_score_gr = get_kt_score_group(kt_score, bins_kt_score)
    bs_score_gr = get_bs_score_group(bs_score, bins_bs_score)
    max_score_gr = get_max_score_group(max_score, bins_max_score)

    return (price_gr, max_score_gr)# kt_score_gr, bs_score_gr)

