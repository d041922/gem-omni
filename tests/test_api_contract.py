import pytest
from skills.data_orchestrator import DataOrchestrator

def test_data_orchestrator_contract():
    """DataOrchestrator가 필수 API 메서드들을 보유하고 있는지 확인"""
    orchestrator = DataOrchestrator()
    
    # 1. 메서드 존재 여부 체크 (이 부분이 실패할 예정)
    assert hasattr(orchestrator, 'is_expired'), "DataOrchestrator에 is_expired 메서드가 없습니다."
    assert hasattr(orchestrator, 'sync_portfolio'), "DataOrchestrator에 sync_portfolio 메서드가 없습니다."
    assert hasattr(orchestrator, 'read_state'), "DataOrchestrator에 read_state 메서드가 없습니다."

def test_is_expired_logic():
    """is_expired의 논리적 작동 여부 확인"""
    orchestrator = DataOrchestrator()
    orchestrator.initialize()
    
    # 초기화 직후(1970년 데이터)는 무조건 만료 상태여야 함
    assert orchestrator.is_expired("portfolio", ttl_seconds=60) is True
