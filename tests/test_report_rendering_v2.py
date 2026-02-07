import pytest
from skills.reporting_engine import ReportingEngine

@pytest.fixture
def reporting_engine():
    return ReportingEngine()

def test_report_v2_template_rendering(reporting_engine):
    """v2.0 템플릿의 필수 섹션 및 신규 지표 렌더링 검증"""
    mock_data = {
        "name": "엔비디아",
        "ticker": "NVDA",
        "sector": "Tech",
        "score": 85.5,
        "details": {
            "rsi": 32.5,
            "vol_surge_ratio": 2.1,
            "is_up_trend": True,
            "fifty_two_week_high_dist": 15.2,
            "market_cap": 3000000000000,
            "dividend_yield": 0.02
        },
        "signals": ["Oversold", "Volume Surge"],
        "market_news": [
            {"headline": "AI 수요 폭증", "sentiment": "Greed", "summary": "엔비디아 칩 품귀 현상..."}
        ],
        "verdict": "STRONG BUY",
        "reason": "강력한 기술적 반등 시그널 확인",
        "action_plan": "현재가에서 50% 분할 매수 진입"
    }
    
    # 템플릿 렌더링
    rendered_md = reporting_engine.generate_markdown(mock_data)
    
    # 필수 키워드 검증 (신규 지표 중심)
    assert "52주 고점 대비" in rendered_md, "52주 고점 이격도 섹션이 누락되었습니다."
    assert "시가총액" in rendered_md, "시가총액 정보가 누락되었습니다."
    assert "투자 전략" in rendered_md, "투자 전략 섹션이 누락되었습니다."
    assert "엔비디아 (NVDA)" in rendered_md, "헤더 정보가 올바르지 않습니다."
