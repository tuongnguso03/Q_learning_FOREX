import pandas as pd
import random


def bin_price(df, n_bins):
    highest = df.loc[df['High'].idxmax()]['High']
    lowest = df.loc[df['Low'].idxmin()]['Low']
    diff = highest - lowest
    bin_size = round(diff / n_bins, 2)
    return bin_size, highest, lowest


def build_bin_price():
    df = pd.read_csv('forex_data.csv')
    n_bins = 20
    bins = [df.loc[df['Low'].idxmin()]['Low']]
    bin_size = bin_price(df, n_bins)[0]
    for i in range(n_bins):
        bins.append(round((bins[-1] + bin_size), 4))
    #print(bins)

    return bins


def get_price_group(price: float):
    bins = build_bin_price()
    for b in bins:
        if price < b:
            return b # or bins.index(b)?


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
        
        distance_to_zone.append(round(min_distance,5))

    return distance_to_zone


def dataset_with_indicators():
    """build a new dataset with indicators"""
    df = pd.read_csv('forex_data.csv')
    print(df.columns)
    processed_df = df.copy()

    # add indicator toZone
    processed_df['toZone'] = calculate_toZone(df)
    # processed_df['score'] = 

    processed_df.to_csv('forex_data_with_indicators.csv', index=False)


def bin_toZone(df, n_bins):
    """distance to the nearest Zone"""    
    highest = df.loc[df['toZone'].idxmax()]['toZone']
    lowest = df.loc[df['toZone'].idxmin()]['toZone']
    diff = highest - lowest
    bin_size = round(diff / n_bins, 2)
    return bin_size, highest, lowest


def build_bin_toZone():
    df = pd.read_csv('forex_data_with_indicators.csv')
    n_bins = 20
    bins = [df.loc[df['Low'].idxmin()]['Low']]
    bin_size = bin_price(df, n_bins)[0]
    for i in range(n_bins):
        bins.append(round((bins[-1] + bin_size), 5))

    return bins


def get_toZone_group(toZone: float):
    bins = build_bin_toZone()
    for b in bins:
        if toZone < b:
            return b 
