import yfinance as yf
import datetime

def debug_ticker(ticker):
    print(f"--- Debugging {ticker} ---")
    try:
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        print(f"Info keys found: {list(info.keys())}")
        
        if 'firstTradeDateMilliseconds' in info:
            ts = info['firstTradeDateMilliseconds']
            print(f"firstTradeDateMilliseconds: {ts}")
            dt = datetime.datetime.fromtimestamp(ts / 1000)
            print(f"Date: {dt.strftime('%Y-%m-%d')}")
        else:
            print("firstTradeDateMilliseconds NOT found in info.")
            
        # Check metadata as well
        meta = yf_ticker.get_history_metadata()
        print(f"Metadata keys: {list(meta.keys())}")
        if 'firstTradeDate' in meta:
            print(f"Metadata firstTradeDate: {meta['firstTradeDate']}")
        else:
            print("firstTradeDate NOT found in metadata.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_ticker("395160.KS")
    debug_ticker("395160.KQ")
