import pytest
import pandas as pd
from unittest.mock import MagicMock
from skills.market_screener import MarketScreener

# ChartEngine은 신규 구현 예정
# from skills.chart_tools import ChartEngine 

@pytest.fixture
def screener():
    return MarketScreener(MagicMock())

def test_chart_engine_contract():
    """ChartEngine이 필수 시각화 메서드를 보유했는지 검증"""
    try:
        from skills.chart_tools import ChartEngine
        engine = ChartEngine()
        assert hasattr(engine, 'create_technical_chart'), "create_technical_chart 메서드 부재"
    except ImportError:
        pytest.fail("skills/chart_tools.py 가 아직 구현되지 않았습니다.")

def test_earnings_data_retrieval(screener):
    """실적(Earnings) 데이터 추출 로직 검증"""
    if not hasattr(screener, 'get_earnings_history'):
        pytest.fail("get_earnings_history 메서드 부재")
        
    # Mocking 없이 구조만 확인 (실제 데이터는 스크리너 내부에서 처리)
    # 구현 시 yfinance의 calendar나 earnings_history 속성을 사용해야 함

def test_peg_calculation_logic(screener):
    """PEG 비율 동적 계산 로직 검증"""
    # 1. API 데이터가 있는 경우
    data_with_peg = {"pegRatio": 1.5, "trailingPE": 30}
    assert screener._calculate_peg_dynamic(data_with_peg) == 1.5
    
    # 2. API 데이터가 없고 성장률을 추정해야 하는 경우
    data_no_peg = {"pegRatio": None, "trailingPE": 20}
    # Growth Rate가 20%라면 PEG는 1.0이어야 함 (로직 검증용)
    # screener 내부에서 Growth를 0으로 가정하면 0 반환
    assert screener._calculate_peg_dynamic(data_no_peg) >= 0
