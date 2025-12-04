import yfinance as yf
import time
import datetime

def test_yfinance():
    ticker = "069500.KS"
    print(f"Testing yfinance for {ticker}...")
    start_time = time.time()
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        if 'firstTradeDateMilliseconds' in info:
            ts_ms = info['firstTradeDateMilliseconds']
            dt = datetime.datetime.fromtimestamp(ts_ms / 1000)
            print(f"Date: {dt.strftime('%Y-%m-%d')}")
        else:
            print("Date not found in info")
    except Exception as e:
        print(f"Error: {e}")
    
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    test_yfinance()
