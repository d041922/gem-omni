import pytest
from unittest.mock import MagicMock
from core.memory import UserMemoryManager

# 구현 전이므로 ImportError 발생을 위해 임시로 정의하지 않음
# from skills.evolution_engine import EvolutionEngine 

@pytest.fixture
def mock_memory():
    # 실제 DB 대신 메모리 DB를 사용하는 매니저 제공
    return UserMemoryManager(db_path=":memory:")

def test_evolution_engine_import():
    """EvolutionEngine 임포트 확인 (RED 단계 확인용)"""
    try:
        from skills.evolution_engine import EvolutionEngine
        assert True
    except ImportError:
        pytest.fail("EvolutionEngine 구현체가 아직 없습니다.")

def test_evolution_engine_contract(mock_memory):
    """EvolutionEngine의 필수 메서드 보유 확인"""
    from skills.evolution_engine import EvolutionEngine
    engine = EvolutionEngine(memory_manager=mock_memory)
    assert hasattr(engine, 'extract_principles'), "extract_principles 메서드가 없습니다."
    assert hasattr(engine, 'update_intuitions_from_history'), "update_intuitions_from_history 메서드가 없습니다."
