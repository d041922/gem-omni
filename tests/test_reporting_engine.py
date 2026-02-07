import pytest
import io
from skills.reporting_engine import ReportingEngine

def test_reporting_engine_contract():
    """ReportingEngine이 필수 메서드들을 보유하고 있는지 확인"""
    engine = ReportingEngine()
    assert hasattr(engine, 'generate_markdown'), "generate_markdown 메서드가 없습니다."
    assert hasattr(engine, 'render_pdf'), "render_pdf 메서드가 없습니다."

def test_pdf_generation_binary():
    """Markdown이 유효한 PDF로 변환되는지 확인"""
    engine = ReportingEngine()
    sample_md = "# OMNI Report\n\n- Asset: NVDA\n- Verdict: Strong Buy"
    
    pdf_bytes = engine.render_pdf(sample_md)
    
    assert isinstance(pdf_bytes, bytes), "결과값이 bytes 형식이 아닙니다."
    assert pdf_bytes.startswith(b'%PDF-'), "유효한 PDF 헤더가 아닙니다."