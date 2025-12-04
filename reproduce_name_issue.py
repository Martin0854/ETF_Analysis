from data.etf_data import ETFDataFetcher
from pykrx import stock

def check_ticker():
    ticker = "395160"
    fetcher = ETFDataFetcher()
    
    print(f"Checking ticker: {ticker}")
    
    # 1. Test wrapper method
    name = fetcher.get_ticker_name(ticker)
    print(f"fetcher.get_ticker_name('{ticker}') returned: '{name}'")
    
    # 2. Test direct pykrx call
    try:
        direct_name = stock.get_etf_ticker_name(ticker)
        print(f"stock.get_etf_ticker_name('{ticker}') returned: '{direct_name}'")
    except Exception as e:
        print(f"stock.get_etf_ticker_name error: {e}")

    # 3. Check what 010010 is
    try:
        other_name = stock.get_market_ticker_name("010010")
        print(f"stock.get_market_ticker_name('010010') returned: '{other_name}'")
    except:
        pass

if __name__ == "__main__":
    check_ticker()
