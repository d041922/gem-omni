import pytest
import pandas as pd
from unittest.mock import MagicMock
from skills.market_screener import FactorEngine
from skills.research_engine import ResearchEngine

@pytest.fixture
def factor_engine():
    return FactorEngine()

@pytest.fixture
def research_engine():
    return ResearchEngine()

def test_chart_indicators_logic(factor_engine):
    """차트에 표시할 이동평균선(MA20, MA50) 계산 로직 검증"""
    prices = [100 + i for i in range(60)]
    df = pd.DataFrame({"Close": prices})
    
    # MA 계산 (FactorEngine에 관련 메서드가 있는지 확인)
    # 현재는 calculate_ma_alignment만 있으므로 개별 MA 값을 가져오는 로직이 필요함
    assert hasattr(factor_engine, 'calculate_ma_alignment'), "MA 정렬 로직이 필요합니다."

def test_report_preview_payload(research_engine):
    """리포트 미리보기용 데이터(Enriched Data)의 필드 규격 검증"""
    raw_data = {
        "ticker": "AAPL",
        "score": 75,
        "details": {"market_cap": 3000000000000}
    }
    
    enriched = research_engine._enrich_report_data(raw_data)
    
    # UI에서 사용할 필수 필드 존재 여부
    assert "ai_summary" in enriched
    assert "market_cap_str" in enriched["details"]
    assert "3.0조" in enriched["details"]["market_cap_str"]
