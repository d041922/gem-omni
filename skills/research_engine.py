"""
OMNI Research Engine (v2.3)
Stable Council Debate Engine with Robust Type Guarding.
"""
import os
import json
import re
import streamlit as st
import google.generativeai as genai
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from skills.reporting_engine import ReportingEngine

class ResearchEngine:
    def __init__(self, cache_dir: str = "data/reports/cache"):
        self.reporter = ReportingEngine()
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self.gemini_available = False
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                # 검증된 최신 모델 사용
                self.model = genai.GenerativeModel('gemini-flash-latest')
                self.gemini_available = True
        except Exception:
            self.gemini_available = False

    def _get_cache_path(self, ticker: str) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        return os.path.join(self.cache_dir, f"{ticker}_{date_str}.pdf")

    def get_report_with_cache(self, ticker: str, force_refresh: bool = False) -> bytes:
        """
        [Cognitive Domain] 전문가 토론 리포트 생성 및 캐싱.
        UI는 오직 티커만 전달하며, 데이터 수집은 내부 기계적 로직(Orchestrator)에 위임한다.
        """
        cache_path = self._get_cache_path(ticker)
        
        # 1. 캐시 체크 (Machine Execution)
        if not force_refresh and os.path.exists(cache_path):
            mtime = datetime.fromtimestamp(os.path.getmtime(cache_path), tz=timezone.utc)
            if datetime.now(timezone.utc) - mtime < timedelta(hours=24):
                try:
                    with open(cache_path, "rb") as f:
                        return f.read()
                except Exception:
                    pass
        
        # 2. 분석용 데이터 확보 (Machine Action)
        from skills.data_orchestrator import DataOrchestrator
        from skills.news_manager import NewsManager
        
        orchestrator = DataOrchestrator()
        ticker_info = orchestrator.get_full_ticker_data(ticker)
        news_manager = NewsManager(orchestrator)
        market_news = news_manager.fetch_ticker_news(ticker)

        # 3. 데이터 가공 및 리포트 생성 (Reasoning)
        return self.create_unified_report(ticker_info, market_news or [])

    def _run_council_debate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini 기반 토론 실행 및 결과 타입 검증"""
        default_res = {
            "verdict": "HOLD",
            "ai_summary": "AI 토론을 수행할 수 없습니다. 데이터를 확인하세요.",
            "reason": "AI 연동 오류 또는 데이터 부족",
            "action_plan": "보수적인 관점에서 시장을 관망하십시오."
        }
        
        if not self.gemini_available:
            return default_res

        prompt = f"""
        당신은 4인의 금융 전문가로 구성된 OMNI 투자 위원회입니다.
        대상 종목: {context.get('ticker')}
        데이터: {context}
        
        반드시 다음 JSON 형식으로만 답변하십시오. (모든 필드 한글 작성)
        {{
            "verdict": "STRONG BUY | BUY | HOLD | SELL",
            "ai_summary": "토론 요약 3문장",
            "reason": "결정적 근거 2가지",
            "action_plan": "구체적 매매 전략"
        }}
        """
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```json|^```|```$", "", text).strip()
            
            result = json.loads(text)
            # [Type Guard] 리턴값이 딕셔너리인지 엄격히 검증
            if isinstance(result, dict) and "verdict" in result:
                return result
            return default_res
        except Exception:
            return default_res

    def create_unified_report(self, ticker_data: Dict[str, Any], market_news: List[Dict[str, Any]]) -> bytes:
        # 데이터 사본 생성 (원본 오염 방지)
        report_data = ticker_data.copy()
        report_data["market_news"] = market_news
        
        # 1. 전문가 토론 실행
        debate_result = self._run_council_debate(report_data)
        
        # 2. 결과 병합 (Type-safe Update)
        if isinstance(debate_result, dict):
            report_data.update(debate_result)
            # 원본 info에도 결과를 갱신하여 UI 미리보기에 반영
            ticker_data.update(debate_result)
        
        # 3. PDF 생성
        md_content = self.reporter.generate_markdown(report_data)
        pdf_bytes = self.reporter.render_pdf(md_content)
        
        # 4. 캐시 저장
        cache_path = self._get_cache_path(ticker_data.get('ticker', 'TEMP'))
        try:
            with open(cache_path, "wb") as f:
                f.write(pdf_bytes)
        except Exception:
            pass
            
        return pdf_bytes