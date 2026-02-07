import pytest
from unittest.mock import MagicMock, patch

# 구현 전이므로 ImportError 발생을 위해 임시로 정의하지 않음
# from skills.ticker_search import TickerSearchEngine

def test_ticker_search_contract():
    """TickerSearchEngine이 설계된 인터페이스를 보유하고 있는지 확인"""
    try:
        from skills.ticker_search import TickerSearchEngine
        engine = TickerSearchEngine()
        assert hasattr(engine, 'search_symbols'), "search_symbols 메서드가 없습니다."
        assert hasattr(engine, 'to_tradingview_format'), "to_tradingview_format 메서드가 없습니다."
    except ImportError:
        pytest.fail("skills/ticker_search.py 파일이 아직 구현되지 않았습니다.")

def test_search_logic_mock():
    """모호한 검색어에 대해 추천 리스트를 반환하는 논리 검증"""
    from skills.ticker_search import TickerSearchEngine
    engine = TickerSearchEngine()
    
    # 1. 영문 검색 시뮬레이션
    results = engine.search_symbols("Apple")
    assert len(results) > 0
    assert any("AAPL" in r['symbol'] for r in results)
    
    # 2. 한글 검색 시뮬레이션 (TICKER_MAP 등 활용)
    results_kr = engine.search_symbols("삼성")
    assert len(results_kr) > 0
    assert any("005930" in r['symbol'] for r in results_kr)

def test_tradingview_format_conversion():
    """티커를 TradingView 위젯 규격으로 변환하는지 확인"""
    from skills.ticker_search import TickerSearchEngine
    engine = TickerSearchEngine()
    
    assert engine.to_tradingview_format("AAPL", "NASDAQ") == "NASDAQ:AAPL"
    assert engine.to_tradingview_format("005930", "KRX") == "KRX:005930"
    assert engine.to_tradingview_format("BTC-USD", "BINANCE") == "BINANCE:BTCUSD"
