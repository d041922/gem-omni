"""
OMNI Reporting Engine (v1.0)
Converts data into professional Markdown and PDF reports.
Inspired by Prism Insight's template architecture.
"""
import io
from datetime import datetime, timezone
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
from markdown_pdf import MarkdownPdf, Section

class ReportingEngine:
    """
    마스터의 자산 및 종목 데이터를 바탕으로 리포트를 생성하고 PDF로 변환함.
    """

    def __init__(self, template_dir: str = "skills/templates"):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate_markdown(self, data: Dict[str, Any], template_name: str = "report_template.md") -> str:
        """
        데이터를 Jinja2 템플릿에 주입하여 Markdown 텍스트 생성.
        """
        template = self.env.get_template(template_name)
        
        # 필수 메타데이터 추가
        data["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return template.render(**data)

    def render_pdf(self, md_text: str) -> bytes:
        """
        Markdown 텍스트를 PDF 바이너리로 변환.
        """
        pdf = MarkdownPdf()
        # UTF-8 및 테이블 렌더링을 위해 Section 추가
        pdf.add_section(Section(md_text, toc=False))
        
        # 바이너리로 저장하여 메모리 상에서 처리 (Streamlit 최적화)
        out = io.BytesIO()
        pdf.save_bytes(out)
        return out.getvalue()

    def create_unified_report(self, ticker_data: Dict[str, Any], market_news: List[Dict[str, Any]] = None) -> bytes:
        """
        종목 데이터와 뉴스를 결합하여 즉시 PDF 리턴 (High-level API).
        """
        data = ticker_data.copy()
        data["market_news"] = market_news if market_news else []
        
        md_content = self.generate_markdown(data)
        return self.render_pdf(md_content)
