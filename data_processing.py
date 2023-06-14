import pandas as pd
import random

df = pd.read_csv('forex_data.csv')

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

    return bins


def get_price_group(price, bins):
    for b in bins:
        if price < b:
            return b # or bins.index(b)?


