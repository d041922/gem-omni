import os
import json
import pytest
import time
from unittest.mock import patch, MagicMock
from skills.data_orchestrator import DataOrchestrator

# 테스트용 경로 설정
TEST_DATA_DIR = "data"
TEST_STATE_FILE = os.path.join(TEST_DATA_DIR, "world_state.json")

@pytest.fixture
def orchestrator():
    """테스트용 오케스트레이터 인스턴스 제공"""
    # 테스트 전 기존 파일 정리 (격리)
    if os.path.exists(TEST_STATE_FILE):
        os.remove(TEST_STATE_FILE)
    
    return DataOrchestrator(state_path=TEST_STATE_FILE)

def test_initialization(orchestrator):
    """UT-01: 초기화 시 기본 스켈레톤 파일이 생성되는지 확인"""
    orchestrator.initialize()
    assert os.path.exists(TEST_STATE_FILE)
    
    with open(TEST_STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["metadata"]["version"] == "2.5"
        assert "market" in data["data"]
        assert "portfolio" in data["data"]

def test_atomic_write(orchestrator):
    """UT-03: 데이터 쓰기 시 원자적 교체가 일어나는지 확인"""
    orchestrator.initialize()
    
    new_data = {"test_key": "test_value"}
    success = orchestrator.update_state("market", new_data)
    
    assert success is True
    with open(TEST_STATE_FILE, "r", encoding="utf-8") as f:
        content = json.load(f)
        # 병합 로직을 고려하여 해당 키가 존재하는지 확인
        assert content["data"]["market"]["test_key"] == "test_value"
    
    # 임시 파일이 남아있지 않아야 함
    assert not os.path.exists(TEST_STATE_FILE + ".tmp")

def test_ttl_logic(orchestrator):
    """UT-02: TTL 만료 여부 판단 로직 확인"""
    orchestrator.initialize()
    
    # 1. 초기화 직후 1970년 데이터는 만료된 것으로 판단해야 함
    assert orchestrator.is_expired("market", ttl_seconds=60) is True
    
    # 2. 현재 시간으로 업데이트
    orchestrator.update_state("market", {"price": 100})
    
    # 3. 업데이트 직후는 신선해야 함
    assert orchestrator.is_expired("market", ttl_seconds=60) is False

def test_schema_validation(orchestrator):
    """UT-04: 잘못된 데이터 스키마 유입 시 거부 확인"""
    orchestrator.initialize()
    
    # 문자열이 와야 할 곳에 리스트가 오는 등 잘못된 데이터 (간단한 예시)
    invalid_data = None 
    
    success = orchestrator.update_state("metadata", invalid_data)
    assert success is False # 구현부에서 validation 로직에 따라 결과 달라짐
