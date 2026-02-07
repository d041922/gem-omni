"""
GEM: OMNI Market Screener (v3.1 - Standard Alignment)
Integrated with FactorEngine from quant_engine.py.
Resolved bare except warnings and import conflicts.
"""

import pandas as pd
import yfinance as yf
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from skills.quant_engine import FactorEngine  # SSOT 기반 엔진 임포트


class MarketScreener:
    """
    시장 전반의 종목을 스캔하고 필터링하는 전문가급 스크리너.
    계산 로직은 FactorEngine으로 위임함.
    """

    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator

    def get_financial_data(self, ticker: str) -> pd.DataFrame:
        try:
            t = yf.Ticker(ticker)
            return t.quarterly_financials.T
        except Exception:
            return pd.DataFrame()

    def get_consensus_data(self, ticker: str) -> Dict[str, Any]:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return {
                "target_mean": info.get("targetMeanPrice"),
                "peg_ratio": info.get("pegRatio"),
            }
        except Exception:
            return {}

    def _fetch_single_ticker(self, ticker: str) -> Dict[str, Any]:
        """개별 종목 정밀 스캔"""
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1y")
            if hist.empty:
                return None

            # [SSOT] FactorEngine 위임
            rsi = FactorEngine.calculate_rsi(hist)
            vol_res = FactorEngine.calculate_volume_analysis(hist)
            vol_ratio = vol_res.get("ratio_pct", 100.0)

            return {
                "ticker": ticker,
                "score": round(100 - abs(rsi - 50) - (100 - min(vol_ratio, 100)), 1),
                "signals": ["Buy" if rsi < 40 else "Neutral"],
                "details": {
                    "rsi": round(rsi, 2),
                    "vol_surge": round(vol_ratio / 100, 2),
                },
            }
        except Exception:
            return None

    def screen_stocks(self, tickers: List[str]) -> List[Dict[str, Any]]:
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ticker = {
                executor.submit(self._fetch_single_ticker, t): t for t in tickers
            }
            for future in as_completed(future_to_ticker):
                res = future.result()
                if res:
                    results.append(res)
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def save_results(self, results: List[Dict[str, Any]]) -> bool:
        if not self.orchestrator:
            return False
        return self.orchestrator.update_state(
            "intelligence", {"screener_results": results}
        )
