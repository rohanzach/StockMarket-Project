import yfinance as yf
import pandas as pd

def get_stock_data(stock_symbol='JPM'):
    # Load data
    stock = yf.Ticker(stock_symbol)
    # Get stock option information
    call_data = []
    put_data = []
    option_dates = stock.options
    for date in option_dates:
        option_data = stock.option_chain(date)
        call_data.append(option_data.calls)
        put_data.append(option_data.puts)

    print(call_data[0])
    
    return 'Rohan'

if __name__ == '__main__':
    print(get_stock_data())