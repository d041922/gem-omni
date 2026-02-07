import pytest
import os
import time
from unittest.mock import MagicMock, patch
from skills.research_engine import ResearchEngine

@pytest.fixture
def research_engine():
    # 테스트용 캐시 경로 설정
    test_cache_dir = "data/reports/test_cache"
    if not os.path.exists(test_cache_dir):
        os.makedirs(test_cache_dir)
    
    engine = ResearchEngine()
    # 내부 경로를 테스트용으로 변경 (Monkey Patching)
    engine.cache_dir = test_cache_dir
    return engine

def test_report_cache_miss_and_hit(research_engine):
    """UT-CACHE-01, 02: 캐시 Miss 시 생성, Hit 시 재사용 검증"""
    ticker = "MOCK_TICKER"
    
    # 1. 첫 번째 호출 (Miss)
    # create_unified_report 메서드를 모킹하여 실제 연산을 시뮬레이션
    with patch.object(research_engine, 'create_unified_report', return_value=b"%PDF-mock") as mock_gen:
        # get_report_with_cache 라는 메서드가 구현될 것을 기대함
        pdf_bytes = research_engine.get_report_with_cache(ticker, {"name": "Mock"})
        
        assert pdf_bytes.startswith(b'%PDF-')
        assert mock_gen.call_count == 1 # 생성 로직 호출됨
        
        # 캐시 파일 생성 확인
        cache_files = os.listdir(research_engine.cache_dir)
        assert any(ticker in f for f in cache_files)

    # 2. 두 번째 호출 (Hit)
    with patch.object(research_engine, 'create_unified_report') as mock_gen_hit:
        pdf_bytes_hit = research_engine.get_report_with_cache(ticker, {"name": "Mock"})
        
        assert pdf_bytes_hit == pdf_bytes
        assert mock_gen_hit.call_count == 0 # 생성 로직이 호출되지 않아야 함 (캐시 히트)
