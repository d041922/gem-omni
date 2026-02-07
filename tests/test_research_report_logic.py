import pytest
from skills.research_engine import ResearchEngine

@pytest.fixture
def engine():
    return ResearchEngine()

def test_korean_market_cap_formatting(engine):
    """큰 시가총액 수치를 '조/억' 단위로 변환하는 로직 검증"""
    # 3조 2천억 예시
    raw_val = 3200000000000
    formatted = engine._format_to_korean_unit(raw_val)
    assert "3.2조" in formatted
    
    # 5천억 예시
    raw_val_2 = 500000000000
    formatted_2 = engine._format_to_korean_unit(raw_val_2)
    assert "5,000억" in formatted_2

def test_automated_summary_generation(engine):
    """점수에 따른 AI 요약 생성 로직 검증"""
    # 고득점 상황
    data_high = {"score": 85}
    summary_high = engine._generate_dynamic_summary(data_high)
    assert "최우선 순위" in summary_high
    
    # 저득점 상황
    data_low = {"score": 30}
    summary_low = engine._generate_dynamic_summary(data_low)
    assert "보수적인 접근" in summary_low

def test_data_enrichment_mapping(engine):
    """원시 데이터를 템플릿용 풍성한 데이터로 변환하는지 확인"""
    raw_ticker_data = {
        "ticker": "NVDA",
        "score": 88,
        "details": {"market_cap": 3000000000000}
    }
    
    enriched = engine._enrich_report_data(raw_ticker_data)
    
    # 포맷팅된 필드가 존재해야 함
    assert "ai_summary" in enriched
    assert enriched["details"]["market_cap_str"] == "3.0조"
