import pandas as pd
import numpy as np
from scipy.stats import norm



# Implementation of Black-Scholes formula in Python
# Define variables 
# r is the risk-free rate
# S is the current stock price
# K is the option strike price
# T is the time to maturity
# sigma is the volatility of the stock

def blackScholes(r, S, K, T, sigma, type="c"):
    "Calculate BS price of call/put"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    try:
        if type == "c":
            price = S*norm.cdf(d1, 0, 1) - K*np.exp(-r*T)*norm.cdf(d2, 0, 1)
        elif type == "p":
            price = K*np.exp(-r*T)*norm.cdf(-d2, 0, 1) - S*norm.cdf(-d1, 0, 1)
        return price
    except:
        print("Please confirm option type, either 'c' for Call or 'p' for Put!")

def delta_calc(r, S, K, T, sigma, type="c"):
    "Calculate delta of an option"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    try:
        if type == "c":
            delta_calc = norm.cdf(d1, 0, 1)
        elif type == "p":
            delta_calc = -norm.cdf(-d1, 0, 1)
        return delta_calc
    except:
        print("Please confirm option type, either 'c' for Call or 'p' for Put!")

def theta_calc(r, S, K, T, sigma, type="c"):
    "Calculate BS price of call/put"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    try:
        if type == "c":
            theta_calc = -S*norm.pdf(d1, 0, 1)*sigma/(2*np.sqrt(T)) - r*K*np.exp(-r*T)*norm.cdf(d2, 0, 1)
        elif type == "p":
            theta_calc = -S*norm.pdf(d1, 0, 1)*sigma/(2*np.sqrt(T)) + r*K*np.exp(-r*T)*norm.cdf(-d2, 0, 1)
        return theta_calc/365
    except:
        print("Please confirm option type, either 'c' for Call or 'p' for Put!")

def calculate_prob_profit_bs(S, K, T, r, sigma, type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if type == 'c':
        prob_profit = norm.cdf(d2)
    else:  # for put option
        prob_profit = norm.cdf(-d2)
    
    return prob_profit

def add_columns_stock_data(price_data):
    price_data['Daily_Returns'] = (price_data['Close'] / price_data['Close'].shift(1)) - 1
    return price_data

def add_columns_option_data(options_data, price_data, type='call'):
    daily_std = price_data['Daily_Returns'].std()
    sigma = daily_std * np.sqrt(252)
    r = 0.0425
    s = price_data['Close'].iloc[-1]
    
    for chain in options_data:
        t = (pd.to_datetime(chain['date'][0]) - pd.to_datetime('today')).days/365
        t = 1/365 if t <= 0 else t
        chain['t'] = t
        if type == 'call':
            chain['Option Income'] = chain['lastPrice'] * 100
            chain['Break Even'] = chain['strike'] + chain['lastPrice']
            chain['BS Price'] = chain.apply(lambda row: blackScholes(r=r, S=s, K=row['strike'], T=row['t'], sigma=sigma, type='c'), axis=1)
            chain['Delta'] = chain.apply(lambda row: delta_calc(r=r, S=s, K=row['strike'], T=row['t'], sigma=sigma, type='c'), axis=1)
            chain['Theta'] = chain.apply(lambda row: theta_calc(r=r, S=s, K=row['strike'], T=row['t'], sigma=sigma, type='c'), axis=1)
            chain['Prob Profit'] = chain.apply(lambda row: calculate_prob_profit_bs(r=r, S=s, K=row['strike'], T=row['t'], sigma=sigma, type='call'), axis=1)
            chain['Expected Option-Income Return'] = chain.apply(lambda row: row['Prob Profit'] * row['Option Income'], axis=1)
        else:        
            chain['Option Income'] = chain['lastPrice'] * 100
            chain['Break Even'] = chain['strike'] - chain['lastPrice']
            chain['BS Price'] = chain.apply(lambda row: blackScholes(r=r, S=s, K=row['strike'], T=row['t'], sigma=sigma, type='p'), axis=1)
            chain['Delta'] = chain.apply(lambda row: delta_calc(r=r, S=s, K=row['strike'], T=row['t'], sigma=sigma, type='p'), axis=1)
            chain['Theta'] = chain.apply(lambda row: theta_calc(r=r, S=s, K=row['strike'], T=row['t'], sigma=sigma, type='p'), axis=1)
            chain['Prob Profit'] = chain.apply(lambda row: calculate_prob_profit_bs(r=r, S=s, K=row['strike'], T=row['t'], sigma=sigma, type='put'), axis=1)
            chain['Expected Option-Income Return'] = chain.apply(lambda row: (1 - row['Prob Profit']) * row['Option Income'], axis=1)
    return options_data

def sma_calculator(price_data, window=20):
    sma = price_data['Close'].rolling(window=window).mean()
    return sma

def bollinger_bands(price_data, window=20):
    sma = sma_calculator(price_data, window=window)
    std = price_data['Close'].rolling(window=window).std()
    upper_band = sma + (2*std)
    lower_band = sma - (2*std)
    return upper_band, lower_band

