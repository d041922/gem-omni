import pytest
from unittest.mock import MagicMock
from skills.news_manager import NewsManager

def test_news_manager_init_contract():
    """NewsManager 인스턴스화 시 orchestrator 인자가 필수인지 확인"""
    orchestrator = MagicMock()
    # 정상 호출
    manager = NewsManager(orchestrator)
    assert manager.orchestrator == orchestrator
    
    # 잘못된 호출 (인자 누락) -> TypeError 발생 기대
    with pytest.raises(TypeError):
        NewsManager()
