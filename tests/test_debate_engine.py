import pytest
from unittest.mock import MagicMock, patch
from skills.research_engine import ResearchEngine

@pytest.fixture
def engine():
    return ResearchEngine()

def test_council_debate_parsing(engine):
    """LLM의 마크다운 포맷 JSON 응답을 정상 파싱하는지 검증"""
    mock_llm_response = """
    ```json
    {
        "verdict": "BUY",
        "ai_summary": "기술적 반등 구간.",
        "reason": "RSI 과매도 및 PEG 저평가.",
        "action_plan": "분할 매수 접근."
    }
    ```
    """
    
    with patch('google.generativeai.GenerativeModel.generate_content') as mock_gen:
        # Mock Response 객체 생성
        mock_resp = MagicMock()
        mock_resp.text = mock_llm_response
        mock_gen.return_value = mock_resp
        
        # Gemini가 사용 가능하다고 강제 설정
        engine.gemini_available = True
        engine.model = MagicMock()
        engine.model.generate_content.return_value = mock_resp
            
        result = engine._run_council_debate({})
        
        assert result["verdict"] == "BUY"
        assert "기술적 반등" in result["ai_summary"]

def test_report_integration_with_debate(engine):
    """토론 결과가 리포트 데이터에 병합되는지 확인 (Jinja2 UndefinedError 방지)"""
    debate_result = {
        "verdict": "STRONG BUY",
        "ai_summary": "만장일치 매수",
        "reason": "완벽한 정배열",
        "action_plan": "즉시 매수"
    }
    
    # 템플릿 렌더링에 필요한 필수 데이터 주입
    mock_data = {
        "ticker": "AAPL",
        "score": 90,
        "details": {
            "rsi": 30,
            "market_cap": 100000000,
            "vol_surge_ratio": 1.5,
            "is_up_trend": True
        }
    }
    
    with patch.object(engine, '_run_council_debate', return_value=debate_result):
        # create_unified_report 내부에서 _run_council_debate가 호출됨
        report_bytes = engine.create_unified_report(mock_data, [])
        assert report_bytes.startswith(b'%PDF-')