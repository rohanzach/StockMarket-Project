import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
import requests_cache

# Function to get stock option data
def get_option_data(stock_symbol='JPM', session=None):
    # Load data
    stock = yf.Ticker(stock_symbol, session=session)
    # Get stock option information
    all_call_data = []
    all_put_data = []
    option_dates = stock.options
    for date in option_dates:
        option_data = stock.option_chain(date)        
        call_data = option_data.calls
        put_data = option_data.puts
        
        # Add date and stock symbol to data
        call_data['date'] = date
        put_data['date'] = date
        call_data['stock_symbol'] = stock_symbol
        put_data['stock_symbol'] = stock_symbol

        all_call_data.append(option_data.calls)
        all_put_data.append(option_data.puts)


    # print(all_call_data[0])

    return all_call_data, all_put_data

# Function to get stock price history
def get_stock_price_history(stock_symbol='JPM', session=None):
    # Load data
    stock = yf.Ticker(stock_symbol, session=session) 
    # Get stock price history
    stock_data = stock.history(period='3mo')
    return stock_data

def call_api(tic):
    session = requests_cache.CachedSession('./cache.sqlite3', backend='sqlite', expire_after=900)
    session.headers['User-agent'] = 'my-program/1.0'
    price_data = get_stock_price_history(tic, session=session)
    options_call_data, options_put_data = get_option_data(tic, session=session)
    return price_data, options_call_data, options_put_data