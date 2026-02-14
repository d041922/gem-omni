"""
GEM: OMNI Market Screener (v3.1 - Standard Alignment)
Integrated with FactorEngine from quant_engine.py.
Resolved bare except warnings and import conflicts.
"""

import pandas as pd
import yfinance as yf
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from skills.quant_engine import FactorEngine


class MarketScreener:
    """
    Market-wide stock screener.
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

    @staticmethod
    def _calculate_peg_dynamic(info: Dict[str, Any]) -> float:
        peg = info.get("pegRatio")
        if peg is not None:
            return float(peg)
        pe = info.get("trailingPE") or 0.0
        return round(float(pe) / 20.0, 2) if pe else 0.0

    @staticmethod
    def calculate_omni_score(factors: Dict[str, Any]) -> float:
        weights = {
            "rsi": 0.20,
            "macd_hist": 0.10,
            "ma_cross": 0.10,
            "per_rel": 0.20,
            "eps_growth": 0.10,
            "vol_surge": 0.20,
            "rel_strength": 0.10,
        }

        def normalize(key: str, value: Any) -> float:
            if value is None:
                return 0.0
            v = float(value)
            if key == "rsi":
                return max(0.0, 1.0 - abs(v - 50.0) / 50.0)
            if key in {"macd_hist", "ma_cross", "eps_growth"}:
                return max(0.0, min(1.0, v))
            if key == "per_rel":
                return max(0.0, min(1.0, 1.2 - v))
            if key == "vol_surge":
                return max(0.0, min(1.0, v / 3.0))
            if key == "rel_strength":
                return max(0.0, min(1.0, v / 2.0))
            return 0.0

        active = {k: w for k, w in weights.items() if factors.get(k) is not None}
        if not active:
            return 0.0
        total_weight = sum(active.values())
        score = 0.0
        for key, w in active.items():
            score += normalize(key, factors.get(key)) * (w / total_weight)
        return round(score * 100.0, 2)

    def get_earnings_history(self, ticker: str) -> Dict[str, Any]:
        try:
            t = yf.Ticker(ticker)
            cal = getattr(t, "calendar", None)
            return cal.to_dict() if hasattr(cal, "to_dict") else {}
        except Exception:
            return {}

    def _fetch_single_ticker(self, ticker: str) -> Dict[str, Any]:
        def _safe_float(v: Any, default: float = 0.0) -> float:
            try:
                if v is None:
                    return default
                return float(v)
            except Exception:
                return default

        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1y")
            info = getattr(t, "info", {}) or {}

            if hist.empty:
                return {
                    "ticker": ticker,
                    "score": 50.0,
                    "signals": ["Neutral"],
                    "details": {
                        "rsi": 50.0,
                        "vol_surge": 1.0,
                        "52w_high_dist": 0.0,
                        "market_cap": _safe_float(info.get("marketCap"), 0.0),
                        "dividend_yield": _safe_float(info.get("dividendYield"), 0.0),
                    },
                }

            rsi = FactorEngine.calculate_rsi(hist)
            vol_res = FactorEngine.calculate_volume_analysis(hist)
            vol_ratio = vol_res.get("ratio_pct", 100.0)

            high_52w = _safe_float(info.get("fiftyTwoWeekHigh"), 0.0)
            last_close = _safe_float(hist["Close"].iloc[-1], 0.0)
            high_dist = ((high_52w - last_close) / high_52w) * 100.0 if high_52w > 0 and last_close > 0 else 0.0

            return {
                "ticker": ticker,
                "score": round(100 - abs(rsi - 50) - (100 - min(vol_ratio, 100)), 1),
                "signals": ["Buy" if rsi < 40 else "Neutral"],
                "details": {
                    "rsi": round(rsi, 2),
                    "vol_surge": round(vol_ratio / 100, 2),
                    "52w_high_dist": round(high_dist, 2),
                    "market_cap": _safe_float(info.get("marketCap"), 0.0),
                    "dividend_yield": _safe_float(info.get("dividendYield"), 0.0),
                },
            }
        except Exception:
            return {
                "ticker": ticker,
                "score": 50.0,
                "signals": ["Neutral"],
                "details": {
                    "rsi": 50.0,
                    "vol_surge": 1.0,
                    "52w_high_dist": 0.0,
                    "market_cap": 0.0,
                    "dividend_yield": 0.0,
                },
            }

    def screen_stocks(self, tickers: List[str], batch_size: int | None = None) -> List[Dict[str, Any]]:
        results = []
        max_workers = 10
        if batch_size is not None:
            try:
                max_workers = max(1, min(int(batch_size), 10))
            except Exception:
                max_workers = 10

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {executor.submit(self._fetch_single_ticker, t): t for t in tickers}
            for future in as_completed(future_to_ticker):
                res = future.result()
                if res:
                    results.append(res)
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def save_results(self, results: List[Dict[str, Any]]) -> bool:
        if not self.orchestrator:
            return False
        return self.orchestrator.update_state("intelligence", {"screener_results": results})
