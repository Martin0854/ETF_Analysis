import yfinance as yf
from pykrx import stock, bond
from datetime import datetime, timedelta

class MarketDataFetcher:
    def __init__(self):
        pass
        
    def get_market_indices(self):
        """
        Fetches current value and delta for:
        KOSPI, KOSDAQ, USD/KRW, Gov Bond 3Y, Corp Bond AA-
        """
        data = {}
        
        # 1. KOSPI & KOSDAQ (using pykrx for accuracy or yfinance for speed)
        # Using yfinance for now as it's often faster for simple current price
        # KOSPI: ^KS11, KOSDAQ: ^KQ11
        
        tickers = {
            "KOSPI": "^KS11",
            "KOSDAQ": "^KQ11",
            "USD/KRW": "KRW=X"
        }
        
        for name, symbol in tickers.items():
            try:
                ticker = yf.Ticker(symbol)
                # Get 2 days of history to calculate delta
                hist = ticker.history(period="5d") # Fetch a bit more to be safe
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    delta = current - prev
                    data[name] = (round(current, 2), round(delta, 2))
                elif len(hist) == 1:
                    current = hist['Close'].iloc[-1]
                    data[name] = (round(current, 2), 0.0)
                else:
                    data[name] = ("N/A", 0.0)
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                data[name] = ("Error", 0.0)
                
        # 2. Bond Yields
        # Fetch from pykrx
        try:
            bond_df = None
            # Try up to 7 days back to find valid data (holidays/weekends)
            for i in range(7):
                target_date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
                try:
                    df = bond.get_otc_treasury_yields(target_date)
                    if not df.empty:
                        bond_df = df
                        break
                except:
                    continue
            
            if bond_df is not None:
                # Extract Gov Bond 3Y (국고채 3년)
                if "국고채 3년" in bond_df.index:
                    yld = bond_df.loc["국고채 3년", "수익률"]
                    chg = bond_df.loc["국고채 3년", "대비"]
                    data["Gov Bond 3Y"] = (float(yld), float(chg))
                else:
                    data["Gov Bond 3Y"] = ("N/A", 0.0)

                # Extract Corp Bond AA- (회사채 AA-(무보증 3년))
                if "회사채 AA-(무보증 3년)" in bond_df.index:
                    yld = bond_df.loc["회사채 AA-(무보증 3년)", "수익률"]
                    chg = bond_df.loc["회사채 AA-(무보증 3년)", "대비"]
                    data["Corp Bond AA-"] = (float(yld), float(chg))
                else:
                    data["Corp Bond AA-"] = ("N/A", 0.0)
            else:
                data["Gov Bond 3Y"] = ("N/A", 0.0)
                data["Corp Bond AA-"] = ("N/A", 0.0)

        except Exception as e:
            print(f"Error fetching bond yields: {e}")
            data["Gov Bond 3Y"] = ("Error", 0.0)
            data["Corp Bond AA-"] = ("Error", 0.0)
        
        # Determine reference date (using KOSPI's last date if available, else today)
        ref_date_str = datetime.now().strftime("%Y-%m-%d")
        try:
            # Try to get date from KOSPI history if available
            # We need to re-fetch or store it from the loop above. 
            # Let's just fetch KOSPI specifically for the date to be sure, or optimize.
            # Optimization: We already fetched it in the loop. But we didn't save the hist object.
            # Let's just fetch KOSPI one more time or just use today if it fails.
            # Better: capture it in the loop.
            pass
        except:
            pass
            
        # Actually, let's refine the loop to capture the date.
        # But since I can't easily change the whole loop structure in one go without potential errors,
        # I'll just do a quick check on KOSPI here.
        try:
            k_ticker = yf.Ticker("^KS11")
            k_hist = k_ticker.history(period="5d")
            if not k_hist.empty:
                ref_date = k_hist.index[-1]
                ref_date_str = ref_date.strftime("%Y-%m-%d")
        except:
            pass

        return data, ref_date_str

if __name__ == "__main__":
    fetcher = MarketDataFetcher()
    print(fetcher.get_market_indices())
