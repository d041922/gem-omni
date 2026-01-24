import json
import google.generativeai as genai
from typing import Dict, Any, List
from core.base import BaseAgent
from core.models import Asset, StrategyReport, ActionItem

class FinanceAgent(BaseAgent):
    """전략 수립 및 마스터 브리핑 전담 에이전트"""
    def __init__(self, name: str = "FinanceAgent", memory: Any = None):
        super().__init__(name, memory)
        self.model = genai.GenerativeModel('models/gemini-3-pro-preview')

    def generate_portfolio_strategy(self, assets: List[Asset], risk_data: Dict[str, Any]) -> StrategyReport:
        """
        포트폴리오 현황과 퀀트 데이터를 분석하여 Gemini 3 Pro 기반 전략 보고서 생성
        """
        # 데이터 요약
        asset_summary = [f"{a.name}({a.ticker}): 비중 {a.total_evaluation_value:,.0f}원, 수익률 {a.profit_pct:.2f}%" for a in assets]
        summary_str = "\n".join(asset_summary)
        
        beta = risk_data.get('beta', 1.0)
        risk_score = risk_data.get('risk_score', 50)

        prompt = f"""
        당신은 월스트리트의 전설적인 헤지펀드 매니저입니다. 마스터의 포트폴리오를 진단하고 전략을 제시하십시오.
        응답은 반드시 지정된 JSON 형식으로만 출력하십시오.

        [데이터 패트]
        - 자산 현황:
        {summary_str}
        - 포트폴리오 베타: {beta:.2f}
        - 리스크 점수: {risk_score}/100

        [JSON Schema]
        {{
            "headline": "포트폴리오의 현재 상태를 관통하는 강렬한 헤드라인",
            "ai_verdict": "Bullish / Bearish / Neutral 중 택 1",
            "summary": "현재 상황에 대한 3문장 이내의 핵심 요약",
            "risk_analysis": "집중도 및 시장 민감도에 대한 정밀 분석 결과",
            "action_plan": [
                {{ "action": "매수/매도/홀딩", "ticker": "티커", "amount": "비중(%) 또는 수량", "reason": "행동의 근거" }}
            ],
            "macro_alerts": ["주의해야 할 매크로 지표 1", "2"]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            # JSON 파싱 (마크다운 태그 제거 로직 포함)
            clean_json = response.text.strip().replace('```json', '').replace('```', '')
            data = json.loads(clean_json)
            
            # ActionItem 객체 리스트 생성
            actions = [ActionItem(**item) for item in data.get('action_plan', [])]
            
            return StrategyReport(
                headline=data['headline'],
                ai_verdict=data['ai_verdict'],
                summary=data['summary'],
                risk_analysis=data['risk_analysis'],
                action_plan=actions,
                macro_alerts=data['macro_alerts']
            )
        except Exception as e:
            # Fallback (실패 시 기본 리포트 반환)
            return StrategyReport(
                headline="AI 분석 엔진 일시 오류",
                ai_verdict="Neutral",
                summary=f"분석 중 오류가 발생했습니다: {str(e)}",
                risk_analysis="N/A",
                action_plan=[],
                macro_alerts=["API 연결 상태 확인 필요"]
            )

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # 기존 개별 종목 분석 로직은 유지하거나, 추후 통합 가능
        return {"status": "success", "result": "기본 처리 완료"}
