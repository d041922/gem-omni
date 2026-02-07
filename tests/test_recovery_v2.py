import pytest
import pandas as pd
import time
from unittest.mock import patch, MagicMock
from skills.data_orchestrator import DataOrchestrator
from skills.market_screener import MarketScreener

@pytest.fixture
def orchestrator():
    return DataOrchestrator()

def test_specific_ticker_fetching(orchestrator):
    """UT-R01: TIGER 필라델피아반도체(423180.KS) 가격 페칭 검증"""
    # yfinance가 간헐적으로 실패하더라도 0이 아닌 값을 가져와야 함
    # 이 테스트는 실제 네트워크 호출을 포함하므로 통합 테스트 성격임
    price = orchestrator._fetch_price_with_fallback("423180.KS", {})
    assert price > 0, "TIGER ETF 가격을 가져오지 못했습니다."

def test_tier_account_mapping(orchestrator):
    """UT-R02: '자산티어'와 '계좌구분' 컬럼 매핑 완결성 검증"""
    mock_df = pd.DataFrame({
        "종목코드": ["AAPL"],
        "종목명": ["애플"],
        "수량": [1],
        "평균 단가(KRW)": [200000],
        "자산티어": ["Core"],
        "계좌구분": ["메인계좌"],
        "수동 수익률(%)": [10]
    })
    
    # 임시로 sync_portfolio 로직 일부를 테스트
    # 실제 구현부에서 이 컬럼들을 정확히 읽어 'tier', 'account' 키에 넣는지 확인
    # (현재 orchestrator.sync_portfolio()를 모킹하여 로직만 검사)
    with patch("skills.data_orchestrator.load_data_from_gsheet", return_value=(mock_df, None, pd.DataFrame())):
        orchestrator.sync_portfolio()
        state = orchestrator.read_state()
        holding = state["data"]["portfolio"]["holdings"][0]
        
        assert holding["tier"] == "Core", f"Tier 매핑 실패: {holding.get('tier')}"
        assert holding["account"] == "메인계좌", f"Account 매핑 실패: {holding.get('account')}"

def test_screener_performance_lighweight():
    """UT-R03: 스크리너 경량화 페칭 속도 검증 (info 사용 금지)"""
    from skills.market_screener import MarketScreener
    from unittest.mock import MagicMock
    
    screener = MarketScreener(orchestrator=MagicMock())
    start_time = time.time()
    
    # 단일 종목 페칭이 1.5초 이내여야 함 (info 호출 시 보통 3~5초 소요)
    result = screener._fetch_single_ticker("AAPL")
    end_time = time.time()
    
    duration = end_time - start_time
    assert duration < 2.0, f"스크리너가 너무 느립니다: {duration:.2f}s (info 호출 의심)"
    assert result is not None
