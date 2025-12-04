import time
print("Importing ETFDataFetcher...")
t0 = time.time()
from data.etf_data import ETFDataFetcher
print(f"Import took {time.time() - t0:.4f} seconds")


def verify_listing_date():
    fetcher = ETFDataFetcher()
    ticker = "069500" # KODEX 200
    
    print(f"Fetching listing date for {ticker}...")
    start_time = time.time()
    date = fetcher.get_listing_date(ticker)
    end_time = time.time()
    
    print(f"Listing Date: {date}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    if date:
        print("SUCCESS: Listing date fetched.")
    else:
        print("FAILURE: Listing date not fetched.")

if __name__ == "__main__":
    verify_listing_date()
