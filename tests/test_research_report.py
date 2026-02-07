import pytest
from unittest.mock import MagicMock
from skills.research_engine import ResearchEngine

@pytest.fixture
def mock_components():
    return {
        "orchestrator": MagicMock(),
        "screener": MagicMock(),
        "news_manager": MagicMock()
    }

def test_research_engine_workflow(mock_components):
    """UT-REP-01: 퀀트+뉴스 데이터를 결합하여 PDF를 생성하는 전체 흐름 검증"""
    engine = ResearchEngine()
    
    # Mock Data Injection
    ticker_data = {
        "ticker": "NVDA", "score": 85.0, "price": 120.0,
        "details": {"rsi": 30, "vol_surge_ratio": 2.5, "is_up_trend": True},
        "signals": ["Oversold"]
    }
    news_data = [
        {"headline": "NVDA Surges", "summary": "Good earnings...", "sentiment": "Greed"}
    ]
    
    # Generate Report
    pdf_bytes = engine.create_unified_report(ticker_data, news_data)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b'%PDF-')

def test_report_resilience_no_news(mock_components):
    """UT-REP-02: 뉴스가 없어도 리포트가 생성되어야 함"""
    engine = ResearchEngine()
    ticker_data = {"ticker": "UNKNOWN", "score": 50, "price": 10, "details": {}, "signals": []}
    
    pdf_bytes = engine.create_unified_report(ticker_data, market_news=[])
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
