import pytest
import pandas as pd
from skills.market_screener import FactorEngine

@pytest.fixture
def factor_engine():
    return FactorEngine()

def test_pivot_points_calculation(factor_engine):
    """피벗 포인트(지지/저항) 계산 로직 검증"""
    # 임의의 전일 데이터
    mock_ohlc = pd.Series({"High": 150, "Low": 100, "Close": 140})
    
    if not hasattr(factor_engine, 'calculate_pivot_points'):
        pytest.fail("calculate_pivot_points 메서드가 구현되지 않았습니다.")
        
    pivots = factor_engine.calculate_pivot_points(mock_ohlc)
    
    assert "Classic" in pivots
    p = pivots["Classic"]
    assert "P" in p
    assert "R1" in p
    assert "S1" in p
    # P = (150 + 100 + 140) / 3 = 130
    assert p["P"] == 130.0

def test_ma_ribbon_logic(factor_engine):
    """MA Ribbon(6단계 추세판) 로직 검증"""
    # 우상향하는 데이터 생성
    data = {"Close": [100 + i for i in range(250)]}
    df = pd.DataFrame(data)
    
    if not hasattr(factor_engine, 'get_ma_ribbon_status'):
        pytest.fail("get_ma_ribbon_status 메서드가 구현되지 않았습니다.")
        
    ribbon = factor_engine.get_ma_ribbon_status(df)
    
    # 6개 기간 모두 포함 확인
    periods = [5, 10, 20, 50, 100, 200]
    for p in periods:
        key = f"MA{p}"
        assert key in ribbon
        assert ribbon[key] in ["Bullish", "Bearish", "N/A"]
