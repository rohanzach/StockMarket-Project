from fasthtml.common import *
from FH_financial_logic import *
from FH_finance_api_logic import call_api


app,rt = fast_app(live=True)

@rt('/')
def get(): 
    ticker_form = Form(
        Input(type='search', name='ticker', placeholder='Enter Ticker'),
        Input(type='submit', value='Submit'),
        method='post',
        action='/get-ticker',
        role = "search"
    )
    return  Titled('Options Income Finder',
        H3('Enter Ticker'),
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
    except Exception as e:
        return P(f'Error: {e}')
    
    price = price_data.iloc[-1]['Close']
    filtered_data = options_put_data[6][(options_put_data[6]['strike'] < price)]
    # Calculate the days to expiration
    # exp_day = (pd.to_datetime(filtered_data['date'].iloc[0]) - pd.to_datetime('today')).days

    # Calculate the SMA and Bollinger Bands
    sma = price_data['Close'].rolling(window=30).mean()
    std = price_data['Close'].rolling(window=30).std()
    lower_band = sma - (2 * std)
    answer_data = filtered_data[(filtered_data['strike'] < lower_band.iloc[-1])]
    max_row = answer_data.loc[answer_data['Expected Option-Income Return'].idxmax()]
    
    # Display
    return Titled('Interesting Put Options',
        H1(f'Ticker: {ticker}'),
        Details(
            Summary(answer_data['date'].iloc[0]),
            Table(
            Tr(
            Th('Date'),
            Th('Strike'), 
            Th('Option Income'), 
            Th('BS Price'), 
            Th('Delta'), 
            Th('Theta'), 
            Th('Prob Profit'), 
            Th('Expected Option-Income Return')
            ),
            *[Tr(
                Td(row['date']),
                Td(f'${row['strike']}'),
                Td(f'${round(row["Option Income"], 2)}'),
                Td(f'${round(row["BS Price"]*100, 6)}'),
                Td(round(row['Delta'], 4)),
                Td(round(row['Theta'], 4)),
                Td(round(row['Prob Profit'], 4)),
                Td(f'${round(row['Expected Option-Income Return'], 2)}')
            ) for index, row in answer_data.iterrows()]
            ),
            open=True
        ),
        P(max_row)
    )

serve()