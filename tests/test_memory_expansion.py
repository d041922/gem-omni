import pytest
from unittest.mock import MagicMock
from skills.evolution_engine import EvolutionEngine
from core.memory import UserMemoryManager

@pytest.fixture
def mock_memory():
    # 실제 DB 대신 메모리 DB를 사용하는 매니저 제공
    return UserMemoryManager(db_path=":memory:")

@pytest.fixture
def evolution_engine(mock_memory):
    return EvolutionEngine(memory_manager=mock_memory)

def test_evolution_engine_contract(evolution_engine):
    """EvolutionEngine의 필수 메서드 보유 확인"""
    assert hasattr(evolution_engine, 'extract_principles'), "extract_principles 메서드가 없습니다."
    assert hasattr(evolution_engine, 'update_intuitions_from_history'), "update_intuitions_from_history 메서드가 없습니다."

def test_journal_clustering_logic(evolution_engine, mock_memory):
    """일지를 수익률 기준으로 성공/실패 그룹으로 분류하는지 확인"""
    # 가상의 일지 데이터 생성
    mock_memory.add_journal(ticker="AAPL", trigger_type="RSI", confidence_score=80)
    # 실제로는 사후에 profit_rate가 업데이트되어야 함
    # (여기서는 구현부에서 이 데이터를 어떻게 처리할지 로직 테스트용)
    
    # 임시 데이터 주입 (Manual DB insertion for test)
    with mock_memory._get_connection() as conn:
        conn.execute("UPDATE trading_journal SET profit_rate = 15.5, tracking_status = 'completed' WHERE ticker = 'AAPL'")
        conn.execute("INSERT INTO trading_journal (ticker, profit_rate, tracking_status, created_at) VALUES ('TSLA', -5.0, 'completed', '2026-01-01')")
    
    success_group, failure_group = evolution_engine._cluster_journals()
    
    assert len(success_group) == 1
    assert success_group[0]['ticker'] == "AAPL"
    assert len(failure_group) == 1
    assert failure_group[0]['ticker'] == "TSLA"

def test_principle_generation_flow(evolution_engine, mock_memory):
    """분석된 결과가 원칙 테이블에 저장되는 흐름 확인"""
    # 1. 원칙 추출 시뮬레이션
    principle_text = "RSI 과매도 상태에서의 진입은 15% 이상의 수익을 낼 확률이 높음"
    source_ids = "1,2"
    
    # 2. 저장 메서드 호출
    principle_id = evolution_engine._save_extracted_principle(principle_text, source_ids)
    
    assert principle_id > 0
    
    # 3. DB 실제 저장 여부 확인
    with mock_memory._get_connection() as conn:
        cursor = conn.execute("SELECT principle_text FROM investment_principles WHERE id = ?", (principle_id,))
        row = cursor.fetchone()
        assert row[0] == principle_text