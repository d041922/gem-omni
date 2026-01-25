"""
Popular stock tickers database for autocomplete
"""

# US Popular Stocks
US_POPULAR_STOCKS = {
    # Tech Giants (FAANG+)
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet (Google)",
    "AMZN": "Amazon",
    "META": "Meta (Facebook)",
    "NVDA": "NVIDIA",
    "TSLA": "Tesla",

    # Other Tech
    "AMD": "AMD",
    "INTC": "Intel",
    "NFLX": "Netflix",
    "ADBE": "Adobe",
    "CRM": "Salesforce",
    "ORCL": "Oracle",
    "CSCO": "Cisco",

    # AI & Semiconductors
    "TSM": "TSMC",
    "AVGO": "Broadcom",
    "QCOM": "Qualcomm",
    "ASML": "ASML",
    "ARM": "Arm Holdings",

    # Finance
    "JPM": "JPMorgan Chase",
    "BAC": "Bank of America",
    "V": "Visa",
    "MA": "Mastercard",
    "GS": "Goldman Sachs",

    # Consumer
    "WMT": "Walmart",
    "PG": "Procter & Gamble",
    "KO": "Coca-Cola",
    "PEP": "PepsiCo",
    "NKE": "Nike",
    "SBUX": "Starbucks",

    # Healthcare & Biotech
    "JNJ": "Johnson & Johnson",
    "UNH": "UnitedHealth",
    "PFE": "Pfizer",
    "ABBV": "AbbVie",
    "LLY": "Eli Lilly",
    "MRNA": "Moderna",

    # Energy
    "XOM": "ExxonMobil",
    "CVX": "Chevron",
    "NEE": "NextEra Energy",

    # Aerospace & Defense
    "BA": "Boeing",
    "LMT": "Lockheed Martin",

    # ETFs
    "SPY": "S&P 500 ETF",
    "QQQ": "NASDAQ 100 ETF",
    "VOO": "Vanguard S&P 500",
    "VTI": "Vanguard Total Stock",
    "IWM": "Russell 2000 ETF",
    "SOXX": "Semiconductor ETF",
    "XLK": "Technology Sector ETF",
    "XLE": "Energy Sector ETF",
}

# Korean Popular Stocks (ticker.KS format)
KR_POPULAR_STOCKS = {
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "035420.KS": "NAVER",
    "035720.KS": "카카오",
    "051910.KS": "LG화학",
    "006400.KS": "삼성SDI",
    "207940.KS": "삼성바이오로직스",
    "005380.KS": "현대차",
    "000270.KS": "기아",
    "373220.KS": "LG에너지솔루션",
    "068270.KS": "셀트리온",
    "003670.KS": "포스코홀딩스",
    "105560.KS": "KB금융",
    "055550.KS": "신한지주",
    "096770.KS": "SK이노베이션",
    "017670.KS": "SK텔레콤",
    "032830.KS": "삼성생명",
    "028260.KS": "삼성물산",
}


def get_all_popular_stocks():
    """Get combined US + KR stocks dictionary"""
    combined = {}
    combined.update(US_POPULAR_STOCKS)
    combined.update(KR_POPULAR_STOCKS)
    return combined


def search_stocks(query: str, limit: int = 10):
    """
    Search stocks by ticker or name

    Args:
        query: Search query (ticker or name)
        limit: Max results to return

    Returns:
        List of (ticker, name) tuples
    """
    query = query.upper().strip()
    all_stocks = get_all_popular_stocks()

    results = []

    # Exact ticker match first
    if query in all_stocks:
        results.append((query, all_stocks[query]))

    # Partial ticker match
    for ticker, name in all_stocks.items():
        if query in ticker.upper() and (ticker, name) not in results:
            results.append((ticker, name))
            if len(results) >= limit:
                return results

    # Name match (Korean or English)
    for ticker, name in all_stocks.items():
        if query in name.upper() and (ticker, name) not in results:
            results.append((ticker, name))
            if len(results) >= limit:
                return results

    return results


def get_ticker_display_name(ticker: str) -> str:
    """Get display name for ticker (e.g., 'AAPL - Apple')"""
    all_stocks = get_all_popular_stocks()
    name = all_stocks.get(ticker, "")
    if name:
        return f"{ticker} - {name}"
    return ticker
