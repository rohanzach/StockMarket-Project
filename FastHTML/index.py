from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient
from FH_financial_logic import *
from FH_finance_api_logic import call_api
from dotenv import load_dotenv
import os
import json

# Header for the HTML
hdrs = (picolink, Script(src="https://cdn.tailwindcss.com"),
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"))


# Beforeware to check if the user is logged in
def before(req, session):
    # The `auth` key in the scope is automatically provided to any handler which requests it, and can not
    # be injected by the user using query params, cookies, etc, so it should be secure to use.
    auth = req.scope['auth'] = session.get('user_id', None)
    # If the session key is not there, it redirects to the login page.
    if not auth: return RedirectResponse('/login', status_code=303)
bware = Beforeware(before, skip=['/login', '/auth/callback'])

# Create the table for the options
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

# Create the app and routes
app = FastHTML(hdrs=hdrs, before=bware)
rt = app.route

# Load the environment variables
env_path = os.path.join(os.path.dirname(__file__), 'dev.env')
load_dotenv(env_path)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:5001/auth/callback"

# Create the Google App Client
oauth_client = GoogleAppClient(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI)

# Login and Logout routes
@rt('/login')
def login():
    login_ui = Div(
    Div(
        Div(
            H2('Sign in with Google', cls='mt-6 text-center text-3xl font-extrabold text-gray-900'),
            P('Use your Google account to access the application', cls='mt-2 text-center text-sm text-gray-600')
        ),
        Div(
            A(
                Div(
                    Svg(
                        Path(d='M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z'),
                        cls='w-5 h-5',
                        viewBox='0 0 24 24',
                        fill='currentColor'
                    ),
                    cls='mr-2'
                ),
                'Sign in with Google',
                href=oauth_client.login_link(),
                cls='w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
            ),
            cls='mt-8'
        ),
        cls='max-w-md w-full space-y-8'
    ),
    cls='min-h-screen bg-gray-50 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8'
)
    return login_ui

@rt('/auth/callback')
def callback(code:str, session):
    info = oauth_client.retr_info(code)
    session['user_id'] = info[oauth_client.id_key]
    return RedirectResponse('/', status_code=303)
    # return Div(cls='min-h-screen bg-gray-50 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8')(
    #                 H1("Profile info"), 
    #                 P(info[oauth_client.id_key]),
    #             )

@rt('/logout')
def logout(session):
    session.clear()
    return RedirectResponse('/login', status_code=303)


# Main route
@rt('/')
def get(auth): 
    # ticker_form = Form(
    #     Input(type='search', name='ticker', placeholder='Enter Ticker'),
    #     Input(type='submit', value='Submit'),
    #     method='post',
    #     action='/get-ticker',
    #     role = "search"
    # )
    # return  Titled('Options Income Finder',
    #     H3('Enter Ticker'),
    #     ticker_form
    # )

    ticker_form = Form(method='post', action='/get-ticker')(
        Div(
            Div(
                Input(type='text', name='ticker', placeholder='Stock Ticker (e.g., AAPL)',
                      cls = 'block w-full rounded-full border-0 px-4 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6', 
                      required='yes'),
                Input(type='submit', value='Submit', cls='px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 active:bg-indigo-900 focus:outline-none focus:border-indigo-900 focus:ring ring-indigo-300 disabled:opacity-25 transition ease-in-out duration-150'),
                ),
            cls='rounded-md shadow-sm -space-y-px'
            ),
        Fieldset(
            Legend('Option Type', cls='text-sm font-semibold leading-6 text-gray-900'),
            P('Select which option type you would like to analyze', cls='mt-1 text-sm leading-6 text-gray-600'),
            Div(cls='mt-6 space-y-6')(Div(
                    Input(id='put', name='option-type', type='radio', checked='yes', cls='h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-600'),
                    Label('Put', cls='ml-3 block text-sm font-medium leading-6 text-gray-900'),
                    cls='flex items-center'
                ),
                Div(
                    Input(id='call', name='option-type', type='radio', cls='h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-600'),
                    Label('Call', cls='ml-3 block text-sm font-medium leading-6 text-gray-900'),
                    cls='flex items-center'
                ))
        )
        )
    
    static_text = Div(
            Div(
                H2('Wheel Strategy Option Search', cls='mt-6 text-center text-3xl font-extrabold text-gray-900'),
                P('Enter a stock ticker and select an option type', cls='mt-2 text-center text-sm text-gray-600')
            ),
            cls='max-w-md w-full space-y-8'
            )


    return Div(cls='min-h-screen bg-gray-50 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8')(
        static_text,
        ticker_form
    )

@rt('/get-ticker', methods=['POST'])
def post(ticker: str, auth):
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