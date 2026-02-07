import pytest
from unittest.mock import MagicMock
from skills.market_screener import MarketScreener
from skills.analysis_manager import AnalysisManager

@pytest.fixture
def mock_orch():
    return MagicMock()

@pytest.fixture
def mock_memory():
    m = MagicMock()
    m.get_preferences.return_value = {"banned_sectors": "Bio"}
    m.recall.return_value = []
    return m

def test_screener_to_analysis_flow(mock_orch, mock_memory):
    """스크리너 결과가 분석 매니저를 거쳐 지능형 결과로 변환되는지 확인"""
    screener = MarketScreener(mock_orch)
    analyzer = AnalysisManager(mock_orch, mock_memory)
    
    # 1. 스크리너 결과 시뮬레이션
    raw_results = [
        {"ticker": "NVDA", "score": 80.0, "details": {"rsi": 70}, "signals": ["Momentum"], "sector": "Tech"}
    ]
    
    # 2. 분석 매니저 처리
    intelligent_results = []
    for res in raw_results:
        analyzed = analyzer.analyze_candidate(res)
        intelligent_results.append(analyzed)
    
    # 3. 규격 검증
    assert len(intelligent_results) == 1
    assert "final_score" in intelligent_results[0]
    assert "verdict" in intelligent_results[0]
    assert intelligent_results[0]["ticker"] == "NVDA"
    assert intelligent_results[0]["status"] == "active"
