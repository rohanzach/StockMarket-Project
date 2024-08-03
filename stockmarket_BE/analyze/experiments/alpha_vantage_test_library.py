# %%
# from alpha_vantage.timeseries import TimeSeries
import alpha_vantage as av
ALPHA_VANTAGE_API_KEY = os.environ['ALPHA_VANTAGE_API_KEY']
# %%

# ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY)
ts = av.timeseries.TimeSeries(key=ALPHA_VANTAGE_API_KEY)

# Get json object with the intraday data and another with  the call's metadata
data, meta_data = ts.get_intraday('GOOGL')

# %%
