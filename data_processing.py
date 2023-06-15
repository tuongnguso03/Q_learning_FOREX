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


def kangaroo_tail(price, open, high, low):
    if price >= open:
        up, down = price, open
    else:
        up, down = open, price
    if high - up >= down - low:
        score = (up - low) / (high - low)
    else:
        score = (high - down) / (high - low)
    
    return 1000 * (high - low) / score # The lower the score, the better. Hence the higher 1 / score is, the better, should we use this?
    # 1000 multiplier is to convert to pips.

def big_shadow():
    # Need input of previous data
    pass

