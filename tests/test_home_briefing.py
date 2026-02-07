import pytest
from unittest.mock import MagicMock

def get_top_pick_logic(state: dict):
    """app.py에 구현될 원픽 추출 로직 (테스트용)"""
    try:
        results = state.get("data", {}).get("intelligence", {}).get("screener_results", [])
        if not results:
            return None
        # 이미 점수순으로 정렬되어 있다고 가정 (MarketScreener 스펙)
        return results[0]
    except Exception:
        return None

def test_extract_top_pick_success():
    """정상 데이터가 있을 때 상위 1위 종목을 추출하는지 확인"""
    mock_state = {
        "data": {
            "intelligence": {
                "screener_results": [
                    {"ticker": "NVDA", "score": 95.0, "signals": ["Oversold"]},
                    {"ticker": "AAPL", "score": 80.0, "signals": ["Neutral"]}
                ]
            }
        }
    }
    
    top_pick = get_top_pick_logic(mock_state)
    assert top_pick is not None
    assert top_pick["ticker"] == "NVDA"
    assert top_pick["score"] == 95.0

def test_extract_top_pick_empty():
    """데이터가 없을 때 None을 반환하여 방어하는지 확인"""
    mock_state_empty = {"data": {"intelligence": {"screener_results": []}}}
    
    top_pick = get_top_pick_logic(mock_state_empty)
    assert top_pick is None
