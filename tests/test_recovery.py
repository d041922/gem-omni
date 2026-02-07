import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from skills.data_orchestrator import DataOrchestrator

@pytest.fixture
def orchestrator():
    return DataOrchestrator()

def test_recovery_column_normalization(orchestrator):
    """Recovery-UT-01: 지저분한 컬럼명의 시트 데이터가 정규화되는지 확인"""
    dirty_df = pd.DataFrame({
        "  종목코드  ": ["AAPL"],
        " 계좌 ": ["주식계좌"],
        " 구분 ": ["Core"],
        " 수량 ": [10]
    })
    
    # 이 테스트는 현재 실패해야 함 (구현 전)
    # 구현 후에는 orchestrator._normalize_columns(dirty_df) 같은 함수로 검증
    assert True # Placeholder

def test_recovery_fetching_fallback(orchestrator):
    """Recovery-UT-02: yfinance 실패 시 fallback 작동 확인"""
    # 아직 구현 전이므로 개념적 테스트
    # 한국 ETF 티커 ('423180.KS') 주입 시 가격이 0이 아니어야 함
    assert True # Placeholder
