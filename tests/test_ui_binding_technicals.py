import pytest
from skills.chart_tools import ChartInterpreter

def test_interpreter_ui_mapping():
    """해석기 결과가 UI 렌더링에 필요한 모든 키를 보유하고 있는지 확인"""
    interpreter = ChartInterpreter()
    ribbon = {"MA5": "Bullish", "MA20": "Bullish", "MA200": "Bullish"}
    
    result = interpreter.interpret_trend(ribbon)
    
    # UI 바인딩 필수 필드 검증
    assert "title" in result
    assert "description" in result
    # 색상 추출 로직이 결과에 포함되어야 함 (v1.1 보강 필요)
    assert any(c in result["title"] for c in ["🟢", "📈", "🔴", "⚪"])
