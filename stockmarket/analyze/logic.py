import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
import requests_cache


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



def get_option_data(stock_symbol='JPM', session=None):
    # Load data
    stock = yf.Ticker(stock_symbol, session=session)
    # Get stock option information
    all_call_data = []
    all_put_data = []
    option_dates = stock.options
    for date in option_dates:
        option_data = stock.option_chain(date)
        # print(type(option_data.calls))
        
        call_data = option_data.calls
        put_data = option_data.puts
        
        call_data['date'] = date
        put_data['date'] = date
        call_data['stock_symbol'] = stock_symbol
        put_data['stock_symbol'] = stock_symbol

        call_data['Option Income'] = call_data['lastPrice'] * 100
        call_data['Break Even'] = call_data['strike'] + call_data['lastPrice']
        call_data['Total Income'] = call_data['Option Income'] + (call_data['strike'] * 100)

        all_call_data.append(option_data.calls)
        all_put_data.append(option_data.puts)


    # print(all_call_data[0])

    return all_call_data, all_put_data


def get_stock_price_history(stock_symbol='JPM', session=None):
    # Load data
    stock = yf.Ticker(stock_symbol, session=session) 
    # Get stock price history
    stock_data = stock.history(period='3mo')
    return stock_data




if __name__ == '__main__':
    session = requests_cache.CachedSession('yfinance.cache')
    session.headers['User-agent'] = 'my-program/1.0'

    price_data = get_stock_price_history('JPM', session=session)
    options_call_data, options_put_data = get_option_data('JPM', session=session)

    price_data['Daily_Returns'] = (price_data['Close'] / price_data['Close'].shift(1)) - 1
    daily_std = price_data['Daily_Returns'].std()
    sigma = daily_std * np.sqrt(252)
    r = 0.01
    s = price_data['Close'][-1]
    
    # print(options_put_data[0])

    for i in range(len(options_put_data)):
        t = (pd.to_datetime(options_put_data[i]['date'][0]) - pd.to_datetime('today')).days/365
        options_put_data[i]['BS Price'] = blackScholes(r=r, S=s, K = options_put_data[i]['strike'], T=t, sigma=sigma, type='p')
        options_put_data[i]['Delta'] = delta_calc(r=r, S=s, K = options_put_data[i]['strike'], T=t, sigma=sigma, type='p')
        options_put_data[i]['Theta'] = theta_calc(r=r, S=s, K = options_put_data[i]['strike'], T=t, sigma=sigma, type='p')
    
    for i in range(len(options_call_data)):
        t = (pd.to_datetime(options_call_data[i]['date'][0]) - pd.to_datetime('today')).days/365
        options_call_data[i]['BS Price'] = blackScholes(r=r, S=s, K = options_call_data[i]['strike'], T=t, sigma=sigma, type='c')
        options_call_data[i]['Delta'] = delta_calc(r=r, S=s, K = options_call_data[i]['strike'], T=t, sigma=sigma, type='c')
        options_call_data[i]['Theta'] = theta_calc(r=r, S=s, K = options_call_data[i]['strike'], T=t, sigma=sigma, type='c')

    print(options_put_data[0])