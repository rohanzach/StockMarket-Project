from fasthtml.common import *
from FH_financial_logic import *
from FH_finance_api_logic import call_api

# headers = (Script(src="https://cdn.tailwindcss.com"),
#            Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"))


app,rt = fast_app(live=True)

def create_option_table(data, i, band):
    open_value = True if i == 0 else False
    # print(band)
    # style_value='background-color: #d4edda;' if row['strike'] > band else 'background-color: #f8d7da;'
    return Details(
            Summary(data['date'].iloc[0]),
            Table(cls='striped overflow-auto')(
            Tr(
            Th('Date'),
            Th('Strike'), 
            Th('Option Income'), 
            Th('BS Price'), 
            Th('Delta'), 
            Th('Theta'), 
            Th('Prob Profit'), 
            Th('Expected Option-Income'),
            ),
            *[Tr()(
                Td(row['date']),
                Td(f'${row['strike']}'),
                Td(f'${round(row["Option Income"], 2)}'),
                Td(f'${round(row["BS Price"]*100, 4)}'),
                Td(round(row['Delta'], 4)),
                Td(round(row['Theta'], 4)),
                Td(round(row['Prob Profit'], 4)),
                Td(f'${round(row['Expected Option-Income Return'], 2)}'),
            ) for index, row in data.iterrows()]
            ),
            open=open_value
        )

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
    # Calculate the SMA and Bollinger Bands
    sma = price_data['Close'].rolling(window=30).mean()
    std = price_data['Close'].rolling(window=30).std()
    lower_band = sma - (2 * std)

    ui_tables = []
    for i in range(len(options_put_data)):
        data = options_put_data[i][options_put_data[i]['strike'] <= price]
        # data = data[data['strike'] >= lower_band.iloc[-1]]
        if data.empty:
            continue
        else:
            ui_table = create_option_table(data, i, lower_band.iloc[-1])
            ui_tables.append(ui_table)    
    
    # Display
    return Titled('Interesting Put Options',
        H1(f'Ticker: {ticker}'),
        P(f'Current Price: ${round(price,2)}'),
        P(f'SMA: ${round(sma.iloc[-1], 2)}, Bollinger Band: {round(lower_band.iloc[-1], 2)}'),
        # P(f'Bollinger Band: {lower_band.iloc[-1]}')
        *ui_tables 
    )

serve()