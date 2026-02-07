import pytest
from unittest.mock import MagicMock
from skills.market_screener import MarketScreener

@pytest.fixture
def screener():
    return MarketScreener(MagicMock())

def test_financial_data_structure(screener):
    """UT-FUND-01: 재무 데이터 추출 메서드 계약 검증"""
    # 실제 구현 전이므로 메서드 존재 여부만 먼저 확인
    if not hasattr(screener, 'get_financial_data'):
        pytest.fail("get_financial_data 메서드가 구현되지 않았습니다.")
        
    # 실제 yfinance 호출 대신 Mocking을 해야 하지만, 
    # 여기서는 메서드 시그니처와 반환 타입(Dict or DataFrame)을 검증하는 것이 목표
    # (구현 후 상세 로직 검증)

def test_consensus_data_structure(screener):
    """UT-FUND-02: 컨센서스 데이터 추출 메서드 계약 검증"""
    if not hasattr(screener, 'get_consensus_data'):
        pytest.fail("get_consensus_data 메서드가 구현되지 않았습니다.")
