# %%

import numpy as np
import pandas as pd
import requests

ALPHA_VANTAGE_API_KEY = os.environ['ALPHA_VANTAGE_API_KEY']
# %%

symbol='IBM'

api_url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&time_from=20220310T0000&time_to=20220310T2359&apikey={ALPHA_VANTAGE_API_KEY}'
data = requests.get(api_url).json()
print(data)
# %%
