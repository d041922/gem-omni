import pytest
from unittest.mock import MagicMock
from skills.market_screener import MarketScreener

@pytest.fixture
def screener():
    mock_orch = MagicMock()
    # TICKER_MAP 모킹
    mock_orch.TICKER_MAP = {"AAPL": "애플"}
    return MarketScreener(mock_orch)

def test_expanded_metrics_collection(screener):
    """전문가급 분석을 위한 추가 지표(52주 고점, 시총 등) 수집 여부 확인"""
    # 실제 네트워크 호출 대신 특정 티커 분석 수행
    # (내부적으로 fast_info를 사용하므로 실제 AAPL 데이터를 가져옴)
    result = screener._fetch_single_ticker("AAPL")
    
    assert result is not None
    assert "details" in result
    
    # 신규 필수 필드 검증 (이 부분이 현재 실패할 예정)
    required_fields = [
        "52w_high_dist", # 52주 고점 대비 이격도
        "market_cap",    # 시가총액
        "dividend_yield" # 배당 수익률
    ]
    
    for field in required_fields:
        assert field in result["details"], f"필수 지표 '{field}'가 수집되지 않았습니다."
        assert isinstance(result["details"][field], (int, float)), f"지표 '{field}'의 데이터 타입이 올바르지 않습니다."
