import yfinance as yf
import time

def check_metadata(ticker_symbol):
    print(f"\nChecking metadata for {ticker_symbol}...")
    start = time.time()
    try:
        yf_ticker = yf.Ticker(ticker_symbol)
        # get_history_metadata() is available in recent yfinance
        meta = yf_ticker.get_history_metadata()
        print("Metadata keys:", meta.keys())
        if 'firstTradeDate' in meta:
             print("First Trade Date:", meta['firstTradeDate'])
    except Exception as e:
        print(f"Error: {e}")
    print(f"Time: {time.time() - start:.4f}s")

if __name__ == "__main__":
    check_metadata("069500.KS")
