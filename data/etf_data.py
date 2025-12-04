from pykrx import stock
import pandas as pd
import time

class ETFDataFetcher:
    def __init__(self):
        pass
        
    def get_etf_price_history(self, ticker, start_date, end_date):
        """
        Fetches daily OHLCV for the given ETF ticker.
        """
        try:
            # pykrx expects dates in YYYYMMDD format
            df = stock.get_etf_ohlcv_by_date(start_date, end_date, ticker)
            return df
        except Exception as e:
            print(f"Error fetching ETF history: {e}")
            return pd.DataFrame()
            
    def get_etf_pdf(self, ticker, date):
        """
        Fetches Portfolio Deposit File (PDF) for the ETF on a specific date.
        """
        try:
            df = stock.get_etf_portfolio_deposit_file(ticker, date)
            return df
        except Exception as e:
            print(f"Error fetching PDF: {e}")
            return pd.DataFrame()

    def get_ticker_name(self, ticker):
        try:
            return stock.get_etf_ticker_name(ticker)
        except:
            return ticker

    def get_stock_name(self, ticker):
        try:
            # Try stock name first
            name = stock.get_market_ticker_name(ticker)
            if not name:
                # If empty, maybe it's an ETF?
                name = stock.get_etf_ticker_name(ticker)
            return name if name else ticker
        except:
            return ticker

    def get_benchmark_data(self, start_date, end_date, ticker="1001"):
        """
        Fetches benchmark data (default: KOSPI).
        Ticker 1001 is KOSPI in pykrx.
        """
        try:
            df = stock.get_index_ohlcv_by_date(start_date, end_date, ticker)
            return df
        except Exception as e:
            print(f"Error fetching benchmark: {e}")
            return pd.DataFrame()

    def get_stock_price_history(self, ticker, start_date, end_date):
        """
        Fetches price history for a specific stock (constituent).
        """
        try:
            # Add a small delay to avoid rate limiting if called in a loop
            time.sleep(0.1) 
            df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
            return df
        except Exception as e:
            print(f"Error fetching stock history for {ticker}: {e}")
            return pd.DataFrame()

    def get_listing_date(self, ticker):
        """
        Returns the listing date (first trading date) of the ETF.
        """
        try:
            # Fetch from a sufficiently early date. First ETFs in Korea were listed in 2002.
            # We fetch just the index (dates) to be faster if possible, but pykrx returns full DF.
            df = stock.get_etf_ohlcv_by_date("20020101", "20251231", ticker)
            if not df.empty:
                return df.index[0].strftime("%Y-%m-%d")
            return None
        except Exception as e:
            print(f"Error fetching listing date: {e}")
            return None

    def get_all_etf_list(self):
        """
        Returns a list of all ETFs in format "Ticker | Name".
        """
        try:
            # Get all tickers (defaults to today)
            tickers = stock.get_etf_ticker_list()
            
            # This might be slow if we fetch name for each one individually
            # pykrx doesn't have a bulk name fetcher for ETFs easily exposed?
            # stock.get_etf_ticker_name(ticker) is fast enough usually?
            # Let's try to optimize or just loop. There are ~800 ETFs.
            
            etf_list = []
            for ticker in tickers:
                name = stock.get_etf_ticker_name(ticker)
                etf_list.append(f"{ticker} | {name}")
            return etf_list
        except Exception as e:
            print(f"Error fetching ETF list: {e}")
            return []

if __name__ == "__main__":
    fetcher = ETFDataFetcher()
    # Example: KODEX 200 (069500)
    print(fetcher.get_etf_price_history("069500", "20240101", "20240110"))
