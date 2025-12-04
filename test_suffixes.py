import yfinance as yf
import time

def test_ticker(ticker_symbol):
    print(f"\nTesting {ticker_symbol}...")
    start = time.time()
    try:
        yf_ticker = yf.Ticker(ticker_symbol)
        info = yf_ticker.info
        if 'firstTradeDateMilliseconds' in info:
            print(f"Success! Found date in {time.time() - start:.4f}s")
        else:
            print(f"Failed (No date found) in {time.time() - start:.4f}s")
    except Exception as e:
        print(f"Error: {e} in {time.time() - start:.4f}s")

if __name__ == "__main__":
    # KODEX 200 (KOSPI) -> Should work with .KS
    test_ticker("069500.KS")
    
    # KODEX KOSDAQ150 (KOSDAQ) -> Should fail with .KS, work with .KQ
    test_ticker("229200.KS") 
    test_ticker("229200.KQ")
