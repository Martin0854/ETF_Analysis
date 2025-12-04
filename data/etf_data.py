from pykrx import stock
import pandas as pd
import time
import yfinance as yf
import datetime

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
        Optimized to use yfinance metadata for speed.
        """
        try:
            # Helper to fetch date from yfinance
            def fetch_yf_date(symbol):
                yf_ticker = yf.Ticker(symbol)
                
                # 1. Try info (most accurate "First Trade Date")
                try:
                    info = yf_ticker.info
                    if 'firstTradeDateMilliseconds' in info:
                        ts_ms = info['firstTradeDateMilliseconds']
                        dt = datetime.datetime.fromtimestamp(ts_ms / 1000)
                        return dt.strftime("%Y-%m-%d")
                except Exception as e:
                    # print(f"Info fetch failed for {symbol}: {e}")
                    pass
                
                # 2. Try history metadata (backup, often faster or available when info is partial)
                try:
                    meta = yf_ticker.get_history_metadata()
                    if 'firstTradeDate' in meta:
                        ts = meta['firstTradeDate']
                        # This is usually seconds timestamp
                        dt = datetime.datetime.fromtimestamp(ts)
                        return dt.strftime("%Y-%m-%d")
                except Exception as e:
                    # print(f"Metadata fetch failed for {symbol}: {e}")
                    pass
                    
                return None

            # 1. Handle existing suffix
            if "." in ticker:
                date = fetch_yf_date(ticker)
                if date: return date
            
            # 2. Try .KS (KOSPI/KOSDAQ ETFs usually use .KS in Yahoo)
            date = fetch_yf_date(f"{ticker}.KS")
            if date: return date

            # 3. Try .KQ (Just in case some KOSDAQ ETFs use this)
            date = fetch_yf_date(f"{ticker}.KQ")
            if date: return date
            
            # Fallback to old method if yfinance fails
            print(f"yfinance failed for {ticker}, falling back to pykrx...")
            df = stock.get_etf_ohlcv_by_date("20020101", "20251231", ticker)
            if not df.empty:
                return df.index[0].strftime("%Y-%m-%d")
            return None
        except Exception as e:
            print(f"Error fetching listing date: {e}")
            return None

    def is_target_etf(self, name):
        """
        Checks if the ETF is a target for analysis (Domestic Equity).
        Excludes Foreign tracking and Bond ETFs.
        """
        # 1. Filter Foreign
        foreign_keywords = [
            "미국", "S&P", "나스닥", "NASDAQ", "China", "중국", "HongKong", "홍콩", 
            "Japan", "일본", "Vietnam", "베트남", "India", "인도", "Euro", "유로", 
            "Global", "글로벌", "MSCI", "Latin", "라틴", "Brazil", "브라질", 
            "Russia", "러시아", "Shenzhen", "심천", "CSI", "HangSeng", "항셍",
            "Bloomberg", "블룸버그", "Solactive", "STOXX", "Morningstar", "모닝스타",
            "NYSE", "FANG", "팡플러스"
        ]
        
        for kw in foreign_keywords:
            if kw in name:
                return False

        # 2. Filter Bonds
        bond_keywords = [
            "채권", "국채", "국고채", "단기채", "회사채", "Bond", "Treasury", "KOFR", "CD금리"
        ]
        for kw in bond_keywords:
            if kw in name:
                return False
                
        return True

    def get_all_etf_list(self):
        """
        Returns a list of all target ETFs in format "Ticker | Name".
        Filters out Foreign and Bond ETFs.
        """
        try:
            # Get all tickers (defaults to today)
            tickers = stock.get_etf_ticker_list()
            
            etf_list = []
            for ticker in tickers:
                name = stock.get_etf_ticker_name(ticker)
                
                if not self.is_target_etf(name):
                    continue
                        
                etf_list.append(f"{ticker} | {name}")
            return etf_list
        except Exception as e:
            print(f"Error fetching ETF list: {e}")
            return []

if __name__ == "__main__":
    fetcher = ETFDataFetcher()
    # Example: KODEX 200 (069500)
    print(fetcher.get_etf_price_history("069500", "20240101", "20240110"))
