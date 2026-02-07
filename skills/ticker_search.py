"""
OMNI Ticker Search Engine (v1.0)
Fuzzy matching for company names and symbols.
Maps results to TradingView Widget format.
"""
import yfinance as yf
from typing import List, Dict

class TickerSearchEngine:
    """
    마스터의 모호한 검색어를 정확한 시장 티커 및 TradingView 포맷으로 변환함.
    """

    # 기본 매핑 (자주 쓰는 종목 및 수동 보정)
    BASE_MAP = {
        "삼성전자": "005930.KS",
        "삼성": "005930.KS",
        "SK하이닉스": "000660.KS",
        "하이닉스": "000660.KS",
        "엔비디아": "NVDA",
        "애플": "AAPL",
        "테슬라": "TSLA",
        "마이크로소프트": "MSFT",
        "구글": "GOOGL",
        "팔란티어": "PLTR"
    }

    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """
        검색어를 입력받아 관련 있는 종목 리스트(Top 5)를 반환함.
        """
        if not query:
            return []

        results = []
        
        # 1. Base Map (Fast Path) 체크
        query_clean = query.strip()
        if query_clean in self.BASE_MAP:
            symbol = self.BASE_MAP[query_clean]
            results.append({
                "symbol": symbol,
                "name": query_clean,
                "exchange": "KRX" if symbol.endswith(".KS") or symbol.endswith(".KQ") else "NASDAQ"
            })

        # 2. yfinance Search (Deep Path)
        try:
            search_results = yf.Search(query_clean, max_results=5).quotes
            for res in search_results:
                symbol = res.get("symbol")
                name = res.get("longname", res.get("shortname", symbol))
                exchange = res.get("exchange", "UNKNOWN")
                
                if not any(r["symbol"] == symbol for r in results):
                    results.append({
                        "symbol": symbol,
                        "name": name,
                        "exchange": self._normalize_exchange(exchange, symbol)
                    })
        except Exception as e:
            print(f"Ticker Search API Error: {e}")

        return results[:5]

    def _normalize_exchange(self, exchange: str, symbol: str) -> str:
        """yfinance 거래소 코드를 TradingView 규격으로 변환"""
        ex = exchange.upper()
        if "KSC" in ex or "KOE" in ex or symbol.endswith(".KS"):
            return "KRX"
        if "KOS" in ex or symbol.endswith(".KQ"):
            return "KRX"
        if "NMS" in ex or "NAS" in ex:
            return "NASDAQ"
        if "NYQ" in ex or "NYS" in ex:
            return "NYSE"
        if "BNC" in ex or "-" in symbol:
            return "BINANCE"
        return ex

    def to_tradingview_format(self, symbol: str, exchange: str = "UNKNOWN") -> str:
        """최종 TradingView 위젯용 문자열 생성 (EXCHANGE:SYMBOL)"""
        clean_symbol = symbol.replace("-USD", "USD").replace("-KRW", "KRW")
        
        if ".KS" in clean_symbol or ".KQ" in clean_symbol:
            clean_symbol = clean_symbol.split(".")[0]
            return f"KRX:{clean_symbol}"
            
        if exchange == "UNKNOWN":
            exchange = "NASDAQ" if len(clean_symbol) <= 4 else "KRX"
            
        return f"{exchange.upper()}:{clean_symbol}"