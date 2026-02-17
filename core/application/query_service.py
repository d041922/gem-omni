"""Read-side service for recomputed portfolio views."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import pandas as pd

from core.application.recompute_service import RecomputeService
from core.env_config import get_feature_flag
from core.repositories.transaction_repo_sqlite import TransactionRepositorySQLite
from skills.data_orchestrator import DataOrchestrator
from skills.market_screener import MarketScreener
from skills.quant_engine import FactorEngine


class QueryService:
    def __init__(
        self,
        repo: Optional[TransactionRepositorySQLite] = None,
        orchestrator: Optional[DataOrchestrator] = None,
    ):
        self.repo = repo or TransactionRepositorySQLite()
        self.orchestrator = orchestrator or DataOrchestrator()
        self.recompute_service = RecomputeService(self.repo)

    def get_portfolio_view(self, price_by_symbol: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Return holdings/cash/aggregate view from transaction ledger."""
        return self.recompute_service.recompute(price_by_symbol=price_by_symbol)

    def get_wealth_home_payload(self) -> Dict[str, Any]:
        """Single read API for wealth home metrics/table."""
        if get_feature_flag("USE_TX_RECOMPUTE_V1", default=False):
            return self._get_from_recompute()
        return self._get_from_legacy_state()

    def sync_wealth_portfolio(self) -> bool:
        """Write-side compatibility wrapper used by wealth_home page."""
        return bool(self.orchestrator.sync_portfolio())

    def run_wealth_scan(self, tickers: Optional[list[str]] = None) -> bool:
        """Run screener and persist results via orchestrator."""
        if tickers:
            ticker_list = [str(t).upper().strip() for t in tickers if str(t).strip()]
        else:
            state = self.orchestrator.read_state()
            holdings = state.get("data", {}).get("portfolio", {}).get("holdings", [])
            ticker_list = [
                str(h.get("ticker", "")).upper().strip()
                for h in holdings
                if str(h.get("ticker", "")).strip()
            ]
        ticker_list = list(dict.fromkeys(ticker_list))
        if not ticker_list:
            return False
        screener = MarketScreener(self.orchestrator)
        results = screener.screen_stocks(ticker_list)
        return bool(screener.save_results(results))

    def get_optimality_check(self, user_policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Decision OS PR#1: policy/risk/concentration check from portfolio SSOT."""
        from core.application.optimality_check_service import OptimalityCheckService

        return OptimalityCheckService(self).evaluate(user_policy=user_policy)

    def get_stock_analysis_payload(
        self, ticker: str, market: str = "UNKNOWN", as_of: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unified read model for stock analysis page.
        Returns normalized basics/price/technical/fundamental/ai/warnings sections.
        """
        warnings: list[str] = []
        as_of_value = as_of or datetime.now(timezone.utc).isoformat()
        ticker_norm = str(ticker or "").strip().upper()
        if not ticker_norm:
            return {
                "basics": {"name": "", "ticker": "", "currency": "USD", "sector": "N/A", "market": market, "as_of": as_of_value},
                "price_snapshot": {},
                "technical": {},
                "fundamentals": {},
                "ai_insights": {
                    "summary": "No ticker provided.",
                    "hypothesis": "Insufficient data.",
                    "evidence_links": [],
                },
                "warnings": ["ticker_missing"],
                "data_unavailable": True,
                "data_unavailable_reason": "ticker_missing",
                "as_of": as_of_value,
                "data_health": {
                    "status": "unavailable",
                    "quality_score": 0,
                    "issues": ["ticker_missing"],
                },
                "evidence_fields": {},
                "score_breakdown": {},
                "legacy_context": {},
                "consensus": {},
                "news": [],
            }

        ticker_info = self.orchestrator.get_full_ticker_data(ticker_norm)
        if ticker_info.get("data_unavailable"):
            reason = str(ticker_info.get("data_unavailable_reason") or "unknown_fetch_error")
            return {
                "basics": {
                    "name": ticker_norm,
                    "ticker": ticker_norm,
                    "currency": "KRW" if ticker_norm.endswith(".KS") or ticker_norm.endswith(".KQ") else "USD",
                    "sector": "N/A",
                    "industry": "N/A",
                    "market": market,
                    "as_of": as_of_value,
                    "website": "",
                },
                "price_snapshot": {},
                "technical": {},
                "fundamentals": {},
                "ai_insights": {
                    "summary": "Data unavailable.",
                    "hypothesis": "Upstream market data fetch failed.",
                    "evidence_links": [],
                    "disclaimer": "This is informational analysis and not investment advice.",
                },
                "warnings": ["data_unavailable"],
                "data_unavailable": True,
                "data_unavailable_reason": reason,
                "as_of": as_of_value,
                "data_health": {
                    "status": "unavailable",
                    "quality_score": 0,
                    "issues": ["data_unavailable", reason],
                },
                "evidence_fields": {},
                "score_breakdown": {},
                "legacy_context": {},
                "consensus": {},
                "news": [],
            }

        extra = ticker_info.get("extra_stats", {}) if isinstance(ticker_info, dict) else {}
        profile = extra.get("profile", {}) if isinstance(extra, dict) else {}
        financials = extra.get("financials", {}) if isinstance(extra, dict) else {}

        history_dict = ticker_info.get("history", {}) if isinstance(ticker_info, dict) else {}
        history_df = pd.DataFrame.from_dict(history_dict) if history_dict else pd.DataFrame()
        if history_df.empty or "Close" not in history_df.columns:
            warnings.append("price_history_missing")

        currency = "KRW" if ticker_norm.endswith(".KS") or ticker_norm.endswith(".KQ") else "USD"
        basics = {
            "name": ticker_info.get("name", ticker_norm),
            "ticker": ticker_norm,
            "currency": currency,
            "sector": profile.get("sector", "N/A"),
            "industry": profile.get("industry", "N/A"),
            "market": market,
            "as_of": as_of_value,
            "website": profile.get("website", ""),
        }

        price_snapshot = self._build_price_snapshot(history_df, ticker_info)
        technical = self._build_technical(history_df, warnings)
        fundamentals = self._build_fundamentals(financials, warnings)
        fundamental_axes = FactorEngine.generate_fundamental_axis_scores(extra)
        consensus = self._build_consensus(ticker=ticker_norm, price_snapshot=price_snapshot, warnings=warnings)
        news = self._build_news(ticker=ticker_norm, warnings=warnings)
        ai_insights = self._build_ai_insights(basics, price_snapshot, technical, warnings)
        data_health = self._build_data_health(warnings, technical, fundamentals, consensus, news)
        evidence_fields = self._build_evidence_fields(basics, price_snapshot, technical, fundamentals, consensus)
        score_breakdown = self._build_score_breakdown(
            technical, fundamentals, consensus, data_health, fundamental_axes=fundamental_axes
        )

        return {
            "basics": basics,
            "price_snapshot": price_snapshot,
            "technical": technical,
            "fundamentals": fundamentals,
            "consensus": consensus,
            "news": news,
            "ai_insights": ai_insights,
            "warnings": warnings,
            "data_unavailable": False,
            "data_unavailable_reason": "",
            "as_of": as_of_value,
            "data_health": data_health,
            "evidence_fields": evidence_fields,
            "score_breakdown": score_breakdown,
            "legacy_context": {"ticker_info": ticker_info},
        }

    @staticmethod
    def _f(value: Any, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except Exception:
            return default

    def _build_price_snapshot(self, history_df: pd.DataFrame, ticker_info: Dict[str, Any]) -> Dict[str, Any]:
        if history_df.empty or "Close" not in history_df.columns:
            curr = self._f(ticker_info.get("last_price", 0.0))
            return {
                "current_price": curr,
                "prev_close": curr,
                "change_pct": 0.0,
                "high_52w": curr,
                "low_52w": curr,
                "range_position_pct": 50.0 if curr > 0 else 0.0,
            }

        close = pd.to_numeric(history_df["Close"], errors="coerce").dropna()
        if close.empty:
            return {
                "current_price": 0.0,
                "prev_close": 0.0,
                "change_pct": 0.0,
                "high_52w": 0.0,
                "low_52w": 0.0,
                "range_position_pct": 0.0,
            }

        current = self._f(close.iloc[-1], 0.0)
        prev = self._f(close.iloc[-2], current) if len(close) >= 2 else current
        change_pct = ((current - prev) / prev * 100.0) if prev > 0 else 0.0
        high_52w = self._f(close.max(), current)
        low_52w = self._f(close.min(), current)
        span = high_52w - low_52w
        range_pos = ((current - low_52w) / span * 100.0) if span > 0 else 50.0
        return {
            "current_price": current,
            "prev_close": prev,
            "change_pct": change_pct,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "range_position_pct": range_pos,
        }

    def _build_technical(self, history_df: pd.DataFrame, warnings: list[str]) -> Dict[str, Any]:
        if history_df.empty or "Close" not in history_df.columns:
            warnings.append("technical_missing_history")
            return {
                "ma20": None,
                "ma50": None,
                "rsi14": None,
                "volatility_20d": None,
            }

        close = pd.to_numeric(history_df["Close"], errors="coerce")
        ma20 = self._f(close.rolling(window=20).mean().iloc[-1], 0.0) if len(close) >= 20 else None
        ma50 = self._f(close.rolling(window=50).mean().iloc[-1], 0.0) if len(close) >= 50 else None
        rsi = self._f(FactorEngine.calculate_rsi(history_df), 50.0) if len(close) >= 15 else None
        returns = close.pct_change().dropna()
        vol = self._f(returns.tail(20).std() * (252 ** 0.5), 0.0) if len(returns) >= 20 else None
        return {
            "ma20": ma20,
            "ma50": ma50,
            "rsi14": rsi,
            "volatility_20d": vol,
        }

    def _build_fundamentals(self, financials: Dict[str, Any], warnings: list[str]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        total_rev = financials.get("total_rev")
        gross_margin = financials.get("gross_margin")
        roe = financials.get("roe")
        roa = financials.get("roa")
        fcf = financials.get("fcf")

        if total_rev is not None:
            out["revenue"] = self._f(total_rev)
        if gross_margin is not None:
            out["gross_margin"] = self._f(gross_margin)
        if roe is not None:
            out["roe"] = self._f(roe)
        if roa is not None:
            out["roa"] = self._f(roa)
        if fcf is not None:
            out["fcf"] = self._f(fcf)

        if len(out) < 3:
            warnings.append("fundamentals_partial")
        return out

    def _build_ai_insights(
        self,
        basics: Dict[str, Any],
        price_snapshot: Dict[str, Any],
        technical: Dict[str, Any],
        warnings: list[str],
    ) -> Dict[str, Any]:
        ticker = basics.get("ticker", "")
        name = basics.get("name", ticker)
        change = self._f(price_snapshot.get("change_pct"), 0.0)
        rsi = technical.get("rsi14")
        trend_hint = "neutral"
        if change > 2:
            trend_hint = "short-term upside momentum"
        elif change < -2:
            trend_hint = "short-term downside momentum"
        if isinstance(rsi, (int, float)):
            if rsi >= 70:
                trend_hint += ", with overbought risk"
            elif rsi <= 30:
                trend_hint += ", with oversold rebound potential"

        summary = f"{name} ({ticker}) snapshot indicates {trend_hint}."
        hypothesis = "If macro and earnings expectations remain stable, current trend may persist; otherwise mean reversion can occur."
        if warnings:
            hypothesis = "Data gaps detected. Treat this as exploratory context, not a trading signal."

        website = basics.get("website") or ""
        evidence_links = [
            {"label": "Yahoo Finance", "url": f"https://finance.yahoo.com/quote/{ticker}"},
        ]
        if website and isinstance(website, str) and website.startswith(("http://", "https://")):
            evidence_links.append({"label": "Company Website", "url": website})

        return {
            "summary": summary,
            "hypothesis": hypothesis,
            "evidence_links": evidence_links,
            "disclaimer": "This is informational analysis and not investment advice.",
        }

    def _build_consensus(
        self,
        ticker: str,
        price_snapshot: Dict[str, Any],
        warnings: list[str],
    ) -> Dict[str, Any]:
        # Keep deterministic unit tests offline: only run live fetch on app orchestrator.
        if self.orchestrator.__class__.__name__ != "DataOrchestrator":
            return {}
        try:
            raw = MarketScreener(self.orchestrator).get_consensus_data(ticker)
            target_mean = self._f(raw.get("target_mean"), 0.0)
            current = self._f(price_snapshot.get("current_price"), 0.0)
            upside_pct = ((target_mean - current) / current * 100.0) if target_mean > 0 and current > 0 else None
            return {
                "target_mean": target_mean if target_mean > 0 else None,
                "peg_ratio": raw.get("peg_ratio"),
                "current_price": current if current > 0 else None,
                "upside_pct": upside_pct,
            }
        except Exception:
            warnings.append("consensus_unavailable")
            return {}

    def _build_news(self, ticker: str, warnings: list[str]) -> list[Dict[str, Any]]:
        # Keep deterministic unit tests offline: only run live fetch on app orchestrator.
        if self.orchestrator.__class__.__name__ != "DataOrchestrator":
            return []
        try:
            from skills.news_manager import NewsManager

            items = NewsManager(self.orchestrator).fetch_ticker_news(ticker=ticker, limit=5)
            if not items:
                warnings.append("news_unavailable")
                return []
            return items
        except Exception:
            warnings.append("news_unavailable")
            return []

    def _build_data_health(
        self,
        warnings: list[str],
        technical: Dict[str, Any],
        fundamentals: Dict[str, Any],
        consensus: Dict[str, Any],
        news: list[Dict[str, Any]],
    ) -> Dict[str, Any]:
        issues = list(dict.fromkeys(warnings))
        checks = {
            "technical_ready": technical.get("rsi14") is not None,
            "fundamentals_ready": len(fundamentals) >= 3,
            "consensus_ready": bool(consensus),
            "news_ready": len(news) > 0,
        }
        pass_count = sum(1 for v in checks.values() if v)
        quality = int(round((pass_count / len(checks)) * 100))
        status = "healthy" if quality >= 75 else "partial" if quality >= 40 else "weak"
        return {
            "status": status,
            "quality_score": quality,
            "issues": issues,
            "checks": checks,
        }

    def _build_evidence_fields(
        self,
        basics: Dict[str, Any],
        price_snapshot: Dict[str, Any],
        technical: Dict[str, Any],
        fundamentals: Dict[str, Any],
        consensus: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "identity": {
                "ticker": basics.get("ticker"),
                "name": basics.get("name"),
                "sector": basics.get("sector"),
            },
            "price_snapshot": {
                "current_price": price_snapshot.get("current_price"),
                "change_pct": price_snapshot.get("change_pct"),
                "range_position_pct": price_snapshot.get("range_position_pct"),
            },
            "technical": {
                "rsi14": technical.get("rsi14"),
                "ma20": technical.get("ma20"),
                "ma50": technical.get("ma50"),
                "volatility_20d": technical.get("volatility_20d"),
            },
            "fundamentals": {
                "roe": fundamentals.get("roe"),
                "gross_margin": fundamentals.get("gross_margin"),
                "revenue": fundamentals.get("revenue"),
                "fcf": fundamentals.get("fcf"),
            },
            "consensus": {
                "target_mean": consensus.get("target_mean"),
                "upside_pct": consensus.get("upside_pct"),
            },
        }

    def _build_score_breakdown(
        self,
        technical: Dict[str, Any],
        fundamentals: Dict[str, Any],
        consensus: Dict[str, Any],
        data_health: Dict[str, Any],
        fundamental_axes: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        rsi = technical.get("rsi14")
        ma20 = technical.get("ma20")
        ma50 = technical.get("ma50")
        vol20 = technical.get("volatility_20d")
        tech_parts: list[float] = []
        if isinstance(rsi, (int, float)):
            tech_parts.append(max(0.0, min(100.0, 100 - abs(float(rsi) - 50) * 2)))
        if isinstance(ma20, (int, float)) and isinstance(ma50, (int, float)):
            tech_parts.append(70.0 if float(ma20) >= float(ma50) else 35.0)
        if isinstance(vol20, (int, float)):
            # Reward moderate volatility; penalize extremes.
            v = float(vol20)
            vol_score = 75.0 if 0.15 <= v <= 0.45 else 55.0 if 0.08 <= v <= 0.60 else 35.0
            tech_parts.append(vol_score)
        tech_score = int(round(sum(tech_parts) / len(tech_parts))) if tech_parts else None

        axes = fundamental_axes or {}
        axis_scores = [axes.get(k) for k in ("value", "quality", "growth", "risk")]
        axis_values = [float(v) for v in axis_scores if isinstance(v, (int, float))]
        if axis_values:
            fund_score = int(round(sum(axis_values) / len(axis_values)))
        else:
            gross_margin = fundamentals.get("gross_margin")
            roe = fundamentals.get("roe")
            fund_parts = []
            if isinstance(gross_margin, (int, float)):
                fund_parts.append(max(0.0, min(1.0, float(gross_margin))) * 100)
            if isinstance(roe, (int, float)):
                fund_parts.append(max(0.0, min(1.0, float(roe))) * 100)
            fund_score = int(round(sum(fund_parts) / len(fund_parts))) if fund_parts else None

        upside = consensus.get("upside_pct")
        consensus_score = None
        if isinstance(upside, (int, float)):
            consensus_score = int(max(0, min(100, 50 + float(upside))))

        parts = [s for s in [tech_score, fund_score, consensus_score] if isinstance(s, (int, float))]
        raw_overall = int(round(sum(parts) / len(parts))) if parts else None

        health_penalty = int(max(0, 100 - int(data_health.get("quality_score", 0))) * 0.3)
        overall = max(0, raw_overall - health_penalty) if raw_overall is not None else None
        confidence = "high" if data_health.get("quality_score", 0) >= 75 else "medium" if data_health.get("quality_score", 0) >= 40 else "low"

        return {
            "technical": tech_score,
            "fundamental": fund_score,
            "fundamental_axes": {
                "value": axes.get("value"),
                "quality": axes.get("quality"),
                "growth": axes.get("growth"),
                "risk": axes.get("risk"),
                "coverage": axes.get("coverage"),
                "confidence": axes.get("confidence"),
            },
            "consensus": consensus_score,
            "overall": overall,
            "confidence": confidence,
        }

    def _get_from_recompute(self) -> Dict[str, Any]:
        state = self.orchestrator.read_state()
        data = state.get("data", {})
        price_map: Dict[str, float] = {}
        for h in data.get("portfolio", {}).get("holdings", []):
            ticker = str(h.get("ticker", "")).upper().strip()
            if not ticker:
                continue
            px = float(h.get("current_price", 0.0) or 0.0)
            if px <= 0:
                px = float(h.get("average_price", 0.0) or 0.0)
            if px > 0:
                price_map[ticker] = px

        view = self.recompute_service.recompute(price_by_symbol=price_map)
        aggregates = view.get("aggregates", {})
        txs = self.repo.list_all()
        recent = list(reversed(txs[-5:])) if txs else []

        deposit = sum(float(t.get("amount", 0.0) or 0.0) for t in txs if str(t.get("tx_type", "")).upper() == "DEPOSIT")
        withdrawal = sum(float(t.get("amount", 0.0) or 0.0) for t in txs if str(t.get("tx_type", "")).upper() == "WITHDRAWAL")
        net_deposit = deposit - withdrawal
        total_asset = float(aggregates.get("total_krw", 0.0))
        return_pct = ((total_asset - net_deposit) / net_deposit * 100.0) if net_deposit > 0 else 0.0

        return {
            "total_asset": total_asset,
            "cash": float(aggregates.get("cash_krw", 0.0)),
            "holdings_value": float(aggregates.get("stock_krw", 0.0)),
            "holdings_market_value": float(aggregates.get("stock_krw", 0.0)),
            "unrealized_pnl": float(aggregates.get("unrealized_pnl_krw", 0.0)),
            "realized_pnl": float(aggregates.get("realized_pnl_krw", 0.0)),
            "return_pct": return_pct,
            "holdings": view.get("holdings", []),
            "recent_transactions": recent,
            "top_picks": data.get("intelligence", {}).get("screener_results", []),
        }

    def _get_from_legacy_state(self) -> Dict[str, Any]:
        state = self.orchestrator.read_state()
        data = state.get("data", {})
        portfolio = data.get("portfolio", {})
        summary = portfolio.get("summary", {})
        holdings = portfolio.get("holdings", [])

        stock_krw = float(summary.get("stock_krw", 0.0) or 0.0)
        if stock_krw <= 0:
            stock_krw = sum(
                float(h.get("current_value_krw", 0.0) or 0.0)
                if float(h.get("current_value_krw", 0.0) or 0.0) > 0
                else float(h.get("quantity", 0.0) or 0.0) * float(h.get("current_price", 0.0) or 0.0)
                for h in holdings
            )

        total_krw = float(summary.get("total_krw", 0.0) or 0.0)
        cash_krw = float(summary.get("cash_krw", 0.0) or 0.0)
        if total_krw <= 0:
            total_krw = stock_krw + cash_krw

        return {
            "total_asset": total_krw,
            "cash": cash_krw,
            "holdings_value": stock_krw,
            "holdings_market_value": stock_krw,
            "unrealized_pnl": float(summary.get("unrealized_pnl_krw", 0.0) or 0.0),
            "realized_pnl": float(summary.get("realized_pnl_krw", 0.0) or 0.0),
            "return_pct": float(summary.get("return_pct", 0.0) or 0.0),
            "holdings": holdings,
            "recent_transactions": [],
            "top_picks": data.get("intelligence", {}).get("screener_results", []),
        }

    def get_stock_research_payload(
        self,
        ticker: str,
        ticker_info: Optional[Dict[str, Any]],
        news_items: Optional[list[Dict[str, Any]]] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Return cache-backed research metadata for a ticker.
        If force_refresh is True and ticker_info exists, regenerate report from
        current stock-analysis payload context.
        """
        from skills.research_engine import ResearchEngine

        ticker_norm = str(ticker or "").strip().upper()
        if not ticker_norm:
            return {"status": "error", "error": "ticker_missing", "metadata": {}}

        engine = ResearchEngine()
        cache_path = engine._get_cache_path(ticker_norm, "json")

        def _load_cached() -> Optional[Dict[str, Any]]:
            if not os.path.exists(cache_path):
                return None
            try:
                import json

                with open(cache_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                if isinstance(raw, dict):
                    return raw
            except Exception:
                return None
            return None

        cached = _load_cached()
        if not force_refresh and cached is not None:
            return {
                "status": "cache_hit",
                "cached": True,
                "cache_path": cache_path,
                "metadata": self._summarize_research_metadata(cached, cache_path),
            }

        if not isinstance(ticker_info, dict) or not ticker_info:
            return {
                "status": "cache_miss",
                "cached": False,
                "cache_path": cache_path,
                "metadata": {},
                "error": "ticker_context_missing",
            }

        payload = dict(ticker_info)
        payload["ticker"] = ticker_norm
        try:
            pdf_bytes = engine.create_unified_report(payload, market_news=news_items or [])
            cached_after = _load_cached() or {}
            return {
                "status": "generated",
                "cached": bool(cached_after),
                "cache_path": cache_path,
                "pdf_size": len(pdf_bytes) if isinstance(pdf_bytes, (bytes, bytearray)) else 0,
                "metadata": self._summarize_research_metadata(cached_after, cache_path),
            }
        except Exception as exc:
            return {
                "status": "error",
                "cached": False,
                "cache_path": cache_path,
                "metadata": {},
                "error": str(exc),
            }

    def _summarize_research_metadata(self, raw: Dict[str, Any], cache_path: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "ticker": raw.get("ticker"),
            "verdict": raw.get("verdict"),
            "confidence": raw.get("confidence_score"),
            "headline": raw.get("headline_summary"),
            "ai_summary": raw.get("ai_summary"),
            "signals_count": len(raw.get("signals", [])) if isinstance(raw.get("signals"), list) else 0,
            "clash_count": len(raw.get("clash_table", [])) if isinstance(raw.get("clash_table"), list) else 0,
        }
        if os.path.exists(cache_path):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(cache_path), tz=timezone.utc)
                out["cached_at"] = mtime.isoformat()
            except Exception:
                out["cached_at"] = None
        else:
            out["cached_at"] = None
        return out
