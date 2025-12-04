from data.etf_data import ETFDataFetcher
import pandas as pd

def inspect_foreign_etf():
    fetcher = ETFDataFetcher()
    ticker = "360750" # TIGER US S&P500
    date = "20241101"
    
    print(f"Fetching PDF for {ticker} on {date}...")
    pdf = fetcher.get_etf_pdf(ticker, date)
    
    if pdf.empty:
        print("PDF is empty.")
        return
        
    print(f"PDF Columns: {pdf.columns.tolist()}")
    print(f"First 5 rows:\n{pdf.head(5)}")
    
    # Check first constituent
    first_ticker = pdf.index[0]
    print(f"\nChecking first constituent: {first_ticker}")
    
    # Try to fetch name
    name = fetcher.get_stock_name(str(first_ticker))
    print(f"Name: {name}")
    
    # Try to fetch price history
    print("Fetching price history...")
    df = fetcher.get_stock_price_history(str(first_ticker), "20241101", "20241110")
    if df.empty:
        print("Price history is EMPTY. This confirms pykrx cannot fetch this ticker.")
    else:
        print(f"Price history found: {len(df)} rows.")

if __name__ == "__main__":
    inspect_foreign_etf()
