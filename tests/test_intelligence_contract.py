import pytest
from skills.research_engine import ResearchEngine

@pytest.fixture
def engine():
    return ResearchEngine()

def test_intelligence_augmentation_narrative(engine):
    """기술 분석 데이터가 포함될 때 AI 요약 문구가 풍성해지는지 검증"""
    mock_data = {
        "ticker": "AAPL",
        "score": 85,
        "details": {
            "market_cap": 3000000000000,
            "rsi": 30.0,
            "fifty_two_week_high_dist": 25.0
        },
        "tech_analysis": {
            "pivots": {"P": 150, "S1": 145, "R1": 160},
            "ribbon": {"MA5": "Bullish", "MA10": "Bullish", "MA20": "Bullish", "MA50": "Bullish", "MA100": "Bullish", "MA200": "Bullish"}
        },
        "current_price": 146  # S1(145) 근처
    }
    
    # 구현 시 _enrich_report_data 가 tech_analysis 필드를 인식해야 함
    enriched = engine._enrich_report_data(mock_data)
    
    summary = enriched.get("ai_summary", "")
    # 기술적 상황(지지선 근접, 정배열 등)에 대한 언급이 포함되어야 함
    # (현재는 미구현이므로 실패 예상)
    assert "지지선" in summary or "정배열" in summary or "추세" in summary