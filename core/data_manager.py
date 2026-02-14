"""
Central Data Manager [GEM: OMNI] - Strategic Edition
Handles global macro, portfolio mapping, and master profile integration.
"""
import streamlit as st
import pandas as pd
import yfinance as yf
from typing import Dict, List, Any, Optional
from core.models import Portfolio, MacroIndicators
from skills.data_orchestrator import DataOrchestrator

class DataManager:
    @staticmethod
    def _get_orchestrator() -> DataOrchestrator:
        return DataOrchestrator()

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_macro_indicators() -> MacroIndicators:
        """글로벌 거시 지표 수집 (Orchestrator SSOT 사용)"""
        orchestrator = DataManager._get_orchestrator()
        state = orchestrator.read_state()
        market = state.get("data", {}).get("market", {})
        
        # 매크로 지표 갱신 시도 (만료 시)
        if orchestrator.is_expired("market", ttl_seconds=3600):
            # 매크로 데이터 수집 로직은 Orchestrator 내부로 위임 필요 (향후 리팩토링)
            pass

        return MacroIndicators(
            usd_krw=float(market.get("exchange_rate", 1450.0)),
            us_10y_yield=4.2, # Placeholder or fetch via Orchestrator
            vix=15.0,
            nasdaq_change=0.0,
            kospi_change=0.0,
            btc_price=95000.0
        )

    @staticmethod
    def get_portfolio_data(force_refresh: bool = False) -> Portfolio:
        """마스터 프로필 및 매크로가 통합된 포트폴리오 로드 (Orchestrator 연동)"""
        orchestrator = DataManager._get_orchestrator()
        
        if force_refresh:
            orchestrator.sync_portfolio()

        state = orchestrator.read_state()
        portfolio_data = state.get("data", {}).get("portfolio", {})
        summary = portfolio_data.get("summary", {})
        holdings = portfolio_data.get("holdings", [])
        market = state.get("data", {}).get("market", {})
        
        macro = DataManager.get_macro_indicators()
        
        # 하이레벨 통찰 (LLM Reasoning 영역 - 향후 BriefingEngine으로 분리 가능)
        insight = f"🔍 **AI Insight**: 환율 {macro.usd_krw:,.1f}원 기준, 포트폴리오 자산 가치는 ₩{summary.get('total_krw', 0):,.0f}입니다."

        return Portfolio(
            total_net_worth_krw=float(summary.get("total_krw", 0.0)),
            stock_value_krw=float(summary.get("stock_krw", 0.0)),
            cash_krw=float(summary.get("cash_krw", 0.0)),
            profit_krw=0.0, # 계산 로직 필요
            return_pct=0.0,
            goal_amount_krw=100000000.0, # Placeholder
            daily_insight=insight,
            macro=macro,
            holdings=holdings
        )

    @staticmethod
    def get_market_indices() -> Dict[str, Any]:
        """Compatibility API for legacy tests."""
        orchestrator = DataManager._get_orchestrator()
        state = orchestrator.read_state()
        market = state.get("data", {}).get("market", {})
        return {
            "usd_krw": float(market.get("exchange_rate", 1450.0)),
            "nasdaq_change": float(market.get("nasdaq_change", 0.0)),
            "kospi_change": float(market.get("kospi_change", 0.0)),
            "vix": float(market.get("vix", 15.0)),
        }

    @staticmethod
    @st.cache_data(ttl=600)
    def get_stock_snapshot(ticker: str) -> Dict[str, Any]:
        orchestrator = DataManager._get_orchestrator()
        data = orchestrator.get_full_ticker_data(ticker)
        return {
            "ticker": data.get("ticker", ticker),
            "name": data.get("name", ticker),
            "last_price": data.get("last_price", 0.0),
            "is_ready": data.get("is_ready", False),
        }

    @staticmethod
    @st.cache_data(ttl=600)
    def get_stock_data(ticker: str, period: str = "1y") -> Dict[str, Any]:
        """Legacy compatibility API used by stock_analyzer tests."""
        symbol = ticker.upper().strip()
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period=period)
            info = getattr(t, "info", {}) or {}
            if hist is None or hist.empty:
                return {"success": False, "error": f"No price data for {symbol}"}
            return {"success": True, "history": hist, "info": info}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

def get_data_manager(): return DataManager()
