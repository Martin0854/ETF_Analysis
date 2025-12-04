import yfinance as yf
import time

def check_fast_info(ticker_symbol):
    print(f"\nChecking fast_info for {ticker_symbol}...")
    start = time.time()
    try:
        yf_ticker = yf.Ticker(ticker_symbol)
        fast_info = yf_ticker.fast_info
        # Accessing a property triggers the fetch
        print("fast_info keys:", fast_info.keys())
        
        # Check for listing date related keys
        # fast_info is a LazyLoader, keys() might not show everything until accessed? 
        # Actually fast_info is a dictionary-like object in recent versions.
        
        # Common keys: 'year_high', 'year_low', 'last_price', etc.
        # Let's see if there is a date.
        
        # Also check metadata
        # print("Metadata:", yf_ticker.get_history_metadata()) 
        # metadata might have firstTradeDate
        
    except Exception as e:
        print(f"Error: {e}")
    print(f"Time: {time.time() - start:.4f}s")

if __name__ == "__main__":
    check_fast_info("069500.KS")
