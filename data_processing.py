import pandas as pd
import random

df = pd.read_csv('forex_data.csv')
#ema200s = df['200EMA']

def bin_price(df, n_bins):
    highest = df.loc[df['High'].idxmax()]['High']
    lowest = df.loc[df['Low'].idxmin()]['Low']
    diff = highest - lowest
    bin_size = round(diff / n_bins, 2)
    return bin_size, highest, lowest


def build_bin_price():
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


def trend(lastema200, ema200):
    trend = (ema200 - lastema200) / lastema200
    return trend


def kangaroo_tail(price, open, high, low, lastema200: float, ema200: float):
    if price >= open:
        up, down = price, open
    else:
        up, down = open, price
    if high - up >= down - low:
        score = (high - low) / (up - low) * (1 + trend(lastema200, ema200))
    else:
        score = (high - low) / (high - down) * (1 - trend(lastema200, ema200))
    
    return 1000 * (high - low) * score
    # 1000 multiplier is to convert to pips.


def big_shadow(last_1_day: tuple, last_2_day: tuple, lastema200: float, ema200: float) -> float:
    # Need input of previous day's data:
    direction = None
    score = 0
    price1, open1, high1, low1 = last_1_day
    price2, open2, high2, low2 = last_2_day


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
        if mainDirection == "up":
            score = (price1 - open1) / (open2 - price2) * (1 - trend(lastema200, ema200))
        else:
            score = (open1 - price1) / (price2 - open2) * (1 + trend(lastema200, ema200))

        return 1000 * abs(price1 - open1) * score


def wammies():
    pass



