import pytest
from skills.chart_tools import ChartInterpreter # 구현 예정

@pytest.fixture
def interpreter():
    return ChartInterpreter()

def test_trend_interpretation_bullish(interpreter):
    """모든 이평선이 Bullish일 때 강세장 진단이 나오는지 확인"""
    ribbon = {
        "MA5": "Bullish", "MA10": "Bullish", "MA20": "Bullish",
        "MA50": "Bullish", "MA100": "Bullish", "MA200": "Bullish"
    }
    result = interpreter.interpret_trend(ribbon)
    assert "초강력 상승" in result["title"]
    assert "정배열" in result["description"]

def test_momentum_interpretation_overbought(interpreter):
    """가격이 볼린저 상단을 뚫었을 때 과매수 경고가 나오는지 확인"""
    # 현재가(110) > 상단(105)
    tech_data = {
        "current_price": 110,
        "bollinger": {"upper": 105, "lower": 95},
        "rsi": 75
    }
    result = interpreter.interpret_momentum(tech_data)
    assert "과매수" in result["title"]
    assert "차익 실현" in result["description"]
