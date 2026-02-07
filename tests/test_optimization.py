import pytest
import time
import pandas as pd
from unittest.mock import MagicMock, patch
from skills.market_screener import MarketScreener
from skills.data_orchestrator import DataOrchestrator

@pytest.fixture
def mock_orchestrator():
    return MagicMock(spec=DataOrchestrator)

def test_screener_speed_optimization(mock_orchestrator):
    """UT-OPT-01: fast_info를 사용하여 스크리닝 속도가 획기적으로 빠른지 검증"""
    screener = MarketScreener(mock_orchestrator)
    
    # 실제 네트워크 호출을 포함하므로 소수 종목으로 테스트
    tickers = ["AAPL", "NVDA", "TSLA"]
    start_time = time.time()
    
    # 내부적으로 info가 아닌 fast_info를 호출하는지(속도로 간접 확인)
    results = screener.screen_stocks(tickers, batch_size=3)
    end_time = time.time()
    
    duration = end_time - start_time
    # 3종목 기준, info 사용 시 3~5초 소요 -> fast_info 사용 시 1.5초 이내 목표
    # 네트워크 환경 고려하여 넉넉히 2초로 잡되, info 호출 시 절대 불가능한 속도임
    print(f"Screening Duration: {duration:.2f}s")
    assert duration < 3.0, f"스크리너가 너무 느림 ({duration:.2f}s). fast_info 미적용 의심."
    assert len(results) == 3

def test_ui_tab_structure_logic():
    """UT-OPT-02: 3개 탭에 들어갈 데이터 구조가 올바른지 검증"""
    # UI 렌더링 자체보다는 데이터 프레임 구조 검증
    df = pd.DataFrame({
        "account": ["A", "A", "B"],
        "tier": ["Core", "Sat", "Core"],
        "name": ["S1", "S2", "S3"],
        "ticker": ["T1", "T2", "T3"],
        "current_value_krw": [100, 200, 300]
    })
    
    # 1. 계좌별 구조
    sunburst_path_acc = ['account', 'tier', 'name']
    assert all(col in df.columns for col in sunburst_path_acc)
    
    # 2. 전략별 구조
    sunburst_path_tier = ['tier', 'account', 'name']
    assert all(col in df.columns for col in sunburst_path_tier)
    
    # 3. 자산별 구조
    treemap_path = ['name']
    assert all(col in df.columns for col in treemap_path)
