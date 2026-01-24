from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class Asset(BaseModel):
    ticker: str
    name: str
    amount: float = 0.0
    avg_price: float = 0.0
    current_price: float = 0.0
    currency: str = "KRW"
    category: str = "기타"
    source: str = "Unknown"
    last_updated: datetime = Field(default_factory=datetime.now)
    # 계산된 필드들 (UI/저장용)
    total_purchase_value: float = 0.0
    total_evaluation_value: float = 0.0
    profit_amount: float = 0.0
    profit_pct: float = 0.0

class Portfolio(BaseModel):
    assets: List[Asset] = []
    total_asset_value: float = 0.0

class ActionItem(BaseModel):
    """실행 가능한 전략 지시사항"""
    action: str  # 매수, 매도, 리밸런싱 등
    ticker: str
    amount: str  # "5%", "10주" 등
    reason: str

class StrategyReport(BaseModel):
    """AI 헤지펀드 팀의 최종 전략 보고서 규격"""
    headline: str
    ai_verdict: str # Bullish, Bearish, Neutral
    summary: str
    risk_analysis: str
    action_plan: List[ActionItem]
    macro_alerts: List[str]
    generated_at: datetime = Field(default_factory=datetime.now)