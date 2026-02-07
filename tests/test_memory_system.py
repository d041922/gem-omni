import pytest
import os
import sqlite3
from core.memory import UserMemoryManager

# 테스트용 고유 DB 경로
TEST_DB_PATH = "data/test_memory_system.db"

@pytest.fixture
def memory_manager():
    """테스트용 메모리 매니저 (파일 기반 DB 사용하되 테스트 전후로 정리)"""
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass # 윈도우 잠금 무시
            
    manager = UserMemoryManager(db_path=TEST_DB_PATH)
    return manager

def test_memory_db_initialization(memory_manager):
    """테이블이 정상적으로 생성되었는지 확인"""
    # 매니저 내부 메서드가 아닌 직접 연결로 확인 (독립성)
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_memories'")
    assert cursor.fetchone() is not None
    conn.close()

def test_add_and_recall_memory(memory_manager):
    """기억 저장 후 정확히 다시 불러오는지 확인"""
    memory_manager.add_memory(
        memory_type="journal",
        content="엔비디아 핵심 기술력 확인",
        ticker="NVDA"
    )
    
    results = memory_manager.recall(ticker="NVDA")
    assert len(results) > 0
    assert "핵심" in results[0]["content"]

def test_preference_management(memory_manager):
    """선호도 저장 및 조회 확인"""
    memory_manager.update_preferences(style="Momentum")
    prefs = memory_manager.get_preferences()
    assert prefs["style"] == "Momentum"
