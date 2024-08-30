from fasthtml.common import *
from FH_financial_logic import *
from FH_finance_api_logic import call_api


app,rt = fast_app(live=True)

@rt('/')
def get(): 
    ticker_form = Form(
        Input(type='text', name='ticker', placeholder='Enter Ticker'),
        Input(type='submit', value='Submit'),
        method='post',
        action='/get-ticker'
    )
    return Div(
        H1('Enter Ticker'),
        ticker_form
    )

@rt('/get-ticker', methods=['POST'])
def post(ticker: str):
    try:
        ticker = ticker.upper()
        price_data, options_call_data, options_put_data = call_api(ticker)
        price_data = add_columns_stock_data(price_data)
        # options_call_data = add_columns_option_data(options_call_data, price_data, type='call')
        options_put_data = add_columns_option_data(options_put_data, price_data, type='put')
    except:
        return H1('Error')
    
    price_data['Daily_Returns'] = (price_data['Close'] / price_data['Close'].shift(1)) - 1
    daily_std = price_data['Daily_Returns'].std()
    sigma = daily_std * np.sqrt(252)
    r = 0.0425
    s = price_data['Close'].iloc[-1]
    for i in range(1, len(options_put_data)):
        # Need to deal with the date minus due to -1 answer when subtracting dates during overlaps (Close date = current date)
        t = (pd.to_datetime(options_put_data[i]['date'][0]) - pd.to_datetime('today')).days/365
        options_put_data[i]['BS Price'] = blackScholes(r=r, S=s, K = options_put_data[i]['strike'], T=t, sigma=sigma, type='p')
        options_put_data[i]['Delta'] = delta_calc(r=r, S=s, K = options_put_data[i]['strike'], T=t, sigma=sigma, type='p')
        options_put_data[i]['Theta'] = theta_calc(r=r, S=s, K = options_put_data[i]['strike'], T=t, sigma=sigma, type='p')
        options_put_data[i]['Prob Profit'] = calculate_prob_profit_bs(r=r, S=s, K = options_put_data[i]['strike'], T=t, sigma=sigma, type='p')
        options_put_data[i]['Expected Option-Income Return'] = (1 - options_put_data[i]['Prob Profit']) * options_put_data[i]['Option Income']
    
    price = price_data.iloc[-1]['Close']
    filtered_data = options_put_data[6][(options_put_data[6]['strike'] < price)]
    # Calculate the days to expiration
    # exp_day = (pd.to_datetime(filtered_data['date'].iloc[0]) - pd.to_datetime('today')).days

    # Calculate the SMA and Bollinger Bands
    sma = price_data['Close'].rolling(window=30).mean()
    std = price_data['Close'].rolling(window=30).std()
    # upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    answer_data = filtered_data[(filtered_data['strike'] < lower_band.iloc[-1])]
    max_row = answer_data.loc[answer_data['Expected Option-Income Return'].idxmax()]
    # Display
    return Div(
        H1(f'Ticker: {ticker}'),
        P(max_row)
    )

serve()