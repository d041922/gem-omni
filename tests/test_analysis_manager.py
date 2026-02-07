import pytest
from unittest.mock import MagicMock
from skills.analysis_manager import AnalysisManager

@pytest.fixture
def mock_orch():
    return MagicMock()

@pytest.fixture
def mock_memory():
    manager = MagicMock()
    # 과거 승률 데이터 시뮬레이션
    manager.recall.return_value = [{"content": "Past success", "importance": 0.9}]
    # 금지 원칙 시뮬레이션
    manager.get_preferences.return_value = {"banned_sectors": "Bio, Gambling"}
    return manager

@pytest.fixture
def analysis_manager(mock_orch, mock_memory):
    return AnalysisManager(orchestrator=mock_orch, memory_manager=mock_memory)

def test_analysis_manager_contract(analysis_manager):
    """AnalysisManager의 필수 인터페이스 확인"""
    assert hasattr(analysis_manager, 'analyze_candidate'), "analyze_candidate 메서드가 없습니다."

def test_principle_filtering_logic(analysis_manager, mock_memory):
    """금지된 섹터(Bio) 종목 분석 시 필터링되는지 확인"""
    # 퀀트 점수는 높지만 섹터가 'Bio'인 상황 시뮬레이션
    candidate_data = {
        "ticker": "HLB",
        "score": 90.0,
        "sector": "Bio",
        "signals": ["RSI_Oversold"]
    }
    
    # 실제 구현 시 이 데이터를 처리하여 filtered 상태를 반환해야 함
    # (현재는 구현 전이므로 실패 예상)
    result = analysis_manager.analyze_candidate(candidate_data)
    
    assert result["status"] == "filtered"
    assert "원칙 위반" in result["reason"]

def test_integrated_scoring(analysis_manager):
    """퀀트 + 기억 점수가 통합되어 산출되는지 확인"""
    candidate_data = {
        "ticker": "NVDA",
        "score": 80.0,
        "sector": "Tech",
        "signals": ["Volume_Surge"]
    }
    
    result = analysis_manager.analyze_candidate(candidate_data)
    
    assert "final_score" in result
    assert result["final_score"] > 0
