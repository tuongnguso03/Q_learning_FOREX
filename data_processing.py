import pandas as pd
from sklearn.cluster import KMeans

df = pd.read_csv('forex_data.csv')
#ema200s = df['200EMA']

def run_kmeans(data, num_clusters):
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit([[x] for x in data])
    k_centers = [round(center[0],8) for center in kmeans.cluster_centers_]
    return k_centers


# 1st feature: price
def bin_price(df, n_bins):
    highest = df.loc[df['High'].idxmax()]['High']
    lowest = df.loc[df['Low'].idxmin()]['Low']
    diff = highest - lowest
    bin_size = round(diff / n_bins, 2)
    return bin_size, highest, lowest


def build_bin_price(n_bins):
    bins = [df.loc[df['Low'].idxmin()]['Low']]
    bin_size = bin_price(df, n_bins)[0]
    for i in range(n_bins):
        bins.append(round((bins[-1] + bin_size), 4))
    return bins


def get_price_group(price: float):
    bins = build_bin_price(10)
    for b in bins:
        if price < b:
            return b # or bins.index(b)?


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
def trend(lastema200, ema200):
    trend = (ema200 - lastema200) / lastema200
    return trend + 1 #values range from 0 to 2


def kangaroo_tail(price, open, high, low, ema200: float, lastema200: float):
    if price >= open:
        up, down = price, open
    else:
        up, down = open, price
    if high - up >= down - low:
        score = (high - low) / (up - low)
    else:
        score = (high - low) / (high - down)
    
    return 1000 * (high - low) * score * trend(lastema200, ema200) 
    # 1000 multiplier is to convert to pips.

def calculate_kt_score(df):
    kt_score = []
    for i in range(len(df)):
        if i == len(df) - 2:
            kt_score.extend([0,0])
            break
        score = kangaroo_tail(df.loc[i+1, 'Price'], df.loc[i+1, 'Open'], df.loc[i+1, 'High'],
                              df.loc[i+1, 'Low'], df.loc[i+1, '200EMA'], df.loc[i+2, '200EMA'])
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
            score = (price1 - open1) / (open2 - price2)
        else:
            score = (open1 - price1) / (price2 - open2)

        return 1000 * abs(price1 - open1) * score * trend(lastema200, ema200)


def calculate_bs_score(df):
    bs_score = []
    for i in range(len(df)):
        if i == len(df) - 2:
            bs_score.extend([0,0])
            break
        score = big_shadow(df.loc[i+1, 'Price'], df.loc[i+1, 'Open'], df.loc[i+1, '200EMA'],
                            df.loc[i+2, 'Price'], df.loc[i+2, 'Open'], df.loc[i+2, '200EMA'])
        bs_score.append(score)
    return bs_score


def dataset_with_indicators(df):
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


def get_toZone_group(price: float):
    strong_zones = [1.22176, 1.19554, 1.17464, 1.16199, 1.14506, 1.1297, 1.11691, 
                  1.10246, 1.08274, 1.05433, 1.03592, 1.01287, 1.00216, 0.96357]
    closest_zone = strong_zones[0]
    min_distance = abs(price - closest_zone)
    for zone in strong_zones:
        distance = abs(price - zone)
        if distance < min_distance:
            min_distance = distance
            closest_zone = zone
    bins = build_bin_toZone(5)
    for b in bins:
        if min_distance < b:
            return b  
        

def build_bin_kt_score(n_bins):
    values = df2['kt_score'].tolist()
    k = n_bins
    k_centers = run_kmeans(values, k)
    return sorted(k_centers)


def get_kt_score_group(kt_score: float):
    bins = build_bin_kt_score(5)
    for b in bins:
        if kt_score < b:
            return b 


def build_bin_bs_score(n_bins):
    values = df2['bs_score'].tolist()
    k = n_bins
    k_centers = run_kmeans(values, k)
    return sorted(k_centers)


def get_bs_score_group(bs_score: float):
    bins = build_bin_bs_score(5)
    for b in bins:
        if bs_score < b:
            return b 


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

    price_gr = get_price_group(price)
    to_zone_gr = get_toZone_group(price)
    kt_score_gr = get_kt_score_group(kt_score)
    bs_score_gr = get_bs_score_group(bs_score)

    return (price_gr, to_zone_gr, kt_score_gr, bs_score_gr)
