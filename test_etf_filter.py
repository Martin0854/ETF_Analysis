from pykrx import stock

def get_etf_list():
    tickers = stock.get_etf_ticker_list()
    etf_list = []
    for ticker in tickers:
        name = stock.get_etf_ticker_name(ticker)
        etf_list.append((ticker, name))
    return etf_list

def is_target_etf(name):
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
            return False, "Foreign"

    # 2. Filter Bonds
    bond_keywords = [
        "채권", "국채", "국고채", "단기채", "회사채", "Bond", "Treasury", "KOFR", "CD금리"
    ]
    for kw in bond_keywords:
        if kw in name:
            return False, "Bond"
            
    return True, "Domestic Equity"

if __name__ == "__main__":
    print("Fetching ETF list...")
    etfs = get_etf_list()
    print(f"Total ETFs: {len(etfs)}")
    
    domestic_equity = []
    foreign = []
    bonds = []
    
    for ticker, name in etfs:
        is_target, reason = is_target_etf(name)
        if is_target:
            domestic_equity.append(name)
        elif reason == "Foreign":
            foreign.append(name)
        elif reason == "Bond":
            bonds.append(name)
            
    print(f"\nDomestic Equity ({len(domestic_equity)}):")
    print(domestic_equity[:20])
    
    print(f"\nForeign ({len(foreign)}):")
    print(foreign[:10])
    
    print(f"\nBonds ({len(bonds)}):")
    print(bonds[:10])
