"""
OMNI Ticker Search Engine (v1.0)
Fuzzy matching for company names and symbols.
"""

import yfinance as yf
from typing import List, Dict


class TickerSearchEngine:
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
        "팔란티어": "PLTR",
    }
    FALLBACK_MAP = {
        "apple": "AAPL",
        "aapl": "AAPL",
        "samsung": "005930.KS",
        "samsung electronics": "005930.KS",
        "tesla": "TSLA",
        "nvidia": "NVDA",
    }

    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        if not query:
            return []

        results: List[Dict[str, str]] = []
        query_clean = query.strip()
        query_lower = query_clean.lower()

        if query_clean in self.BASE_MAP:
            symbol = self.BASE_MAP[query_clean]
            results.append(self._make_result(symbol, query_clean))
        elif query_lower in self.FALLBACK_MAP:
            symbol = self.FALLBACK_MAP[query_lower]
            results.append(self._make_result(symbol, query_clean))

        try:
            search_results = yf.Search(query_clean, max_results=5).quotes
            for res in search_results:
                symbol = res.get("symbol")
                if not symbol:
                    continue
                name = res.get("longname", res.get("shortname", symbol))
                exchange = self._normalize_exchange(res.get("exchange", "UNKNOWN"), symbol)
                if not any(r["symbol"] == symbol for r in results):
                    results.append({"symbol": symbol, "name": name, "exchange": exchange})
        except Exception as e:
            print(f"Ticker Search API Error: {e}")

        if not results:
            for key, symbol in self.FALLBACK_MAP.items():
                if key in query_lower:
                    results.append(self._make_result(symbol, query_clean))
                    break

        return results[:5]

    def _make_result(self, symbol: str, name: str) -> Dict[str, str]:
        return {
            "symbol": symbol,
            "name": name,
            "exchange": "KRX" if symbol.endswith(".KS") or symbol.endswith(".KQ") else "NASDAQ",
        }

    def _normalize_exchange(self, exchange: str, symbol: str) -> str:
        ex = str(exchange).upper()
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
        return ex if ex else "UNKNOWN"

    def to_tradingview_format(self, symbol: str, exchange: str = "UNKNOWN") -> str:
        clean_symbol = symbol.replace("-USD", "USD").replace("-KRW", "KRW")

        if ".KS" in clean_symbol or ".KQ" in clean_symbol:
            clean_symbol = clean_symbol.split(".")[0]
            return f"KRX:{clean_symbol}"

        if exchange == "UNKNOWN":
            exchange = "NASDAQ" if len(clean_symbol) <= 4 else "KRX"

        return f"{exchange.upper()}:{clean_symbol}"
