from pykrx import stock
import yfinance as yf
import inspect

print("--- pykrx stock module methods ---")
for name, data in inspect.getmembers(stock):
    if name.startswith("get_"):
        print(name)

print("\n--- Testing yfinance for KODEX 200 (069500.KS) ---")
try:
    ticker = yf.Ticker("069500.KS")
    info = ticker.info
    print("yfinance info keys:", info.keys())
    if 'firstTradeDateEpochUtc' in info:
        print("First Trade Date:", info['firstTradeDateEpochUtc'])
    else:
        print("No firstTradeDateEpochUtc found")
except Exception as e:
    print(f"yfinance error: {e}")
