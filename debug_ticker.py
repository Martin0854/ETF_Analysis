from pykrx import stock
import pandas as pd

def check_ticker(ticker):
    print(f"Checking {ticker}...")
    try:
        name = stock.get_market_ticker_name(ticker)
        print(f"Market Name: {name}")
    except Exception as e:
        print(f"Market Name Error: {e}")

    try:
        name = stock.get_etf_ticker_name(ticker)
        print(f"ETF Name: {name}")
    except Exception as e:
        print(f"ETF Name Error: {e}")

    # Try to see if it's an ISIN or something
    # pykrx doesn't have direct ISIN lookup from ticker easily exposed in all versions
    
if __name__ == "__main__":
    check_ticker("028241")
    check_ticker("8579Y1")
    check_ticker("360750")
