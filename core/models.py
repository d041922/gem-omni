"""
Data Models [GEM: OMNI]
Standardized objects for cross-domain communication and data integrity.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


class _FallbackLLM:
    """Minimal callable LLM shim for compatibility in legacy tests."""

    def __init__(self, model_name: str = "gemini/gemini-2.0-flash", temperature: float = 0.2):
        self.model_name = model_name
        self.temperature = temperature

    def call(self, messages: List[Dict]) -> str:
        if not messages:
            return ""
        last = messages[-1].get("content", "")
        return f"[fallback:{self.model_name}] {str(last)[:200]}"


def get_gemini_llm(model_name: str = "gemini/gemini-2.0-flash", temperature: float = 0.2):
    """Return a lightweight LLM-compatible object used by strategy engine."""
    return _FallbackLLM(model_name=model_name, temperature=temperature)

@dataclass
class Price:
    value: float
    currency: str = "USD"
    unit: str = "$"
    timestamp: datetime = field(default_factory=datetime.now)

    def to_krw(self, rate: float) -> float:
        return self.value * rate if self.currency == "USD" else self.value

@dataclass
class MacroIndicators:
    usd_krw: float
    us_10y_yield: float
    vix: float
    nasdaq_change: float
    kospi_change: float
    btc_price: float
    market_status: str = "Neutral"
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Portfolio:
    total_net_worth_krw: float
    stock_value_krw: float
    cash_krw: float
    profit_krw: float
    return_pct: float
    goal_amount_krw: float = 1000000000.0
    daily_insight: str = ""
    macro: Optional[MacroIndicators] = None
    holdings: List[Dict] = field(default_factory=list)
    recommendations: List[Dict] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
