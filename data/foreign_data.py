import yfinance as yf
import pandas as pd

class ForeignDataFetcher:
    def __init__(self):
        pass
        
    def get_price_history(self, ticker_symbol, start_date, end_date):
        """
        Fetch price history for a given ticker.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            # yfinance expects YYYY-MM-DD
            df = ticker.history(start=start_date, end=end_date)
            return df
        except Exception as e:
            print(f"Error fetching history for {ticker_symbol}: {e}")
            return pd.DataFrame()

    def get_top_holdings(self, ticker_symbol):
        """
        Fetch top holdings for an ETF.
        Returns a DataFrame with index=Symbol, columns=['Name', 'Weight']
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            if hasattr(ticker, 'funds_data'):
                fd = ticker.funds_data
                if hasattr(fd, 'top_holdings'):
                    # top_holdings is already a DataFrame usually
                    return fd.top_holdings
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching holdings for {ticker_symbol}: {e}")
            return pd.DataFrame()

    def get_stock_name(self, ticker_symbol):
        try:
            ticker = yf.Ticker(ticker_symbol)
            return ticker.info.get('shortName', ticker_symbol)
        except:
            return ticker_symbol
