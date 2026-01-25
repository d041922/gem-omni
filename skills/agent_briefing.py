"""
Agent Briefing Skill - 시스템의 지능형 요약 및 전략 제안 엔진
마스터의 자산, 현금, 시장 상황을 종합하여 '오늘의 행동'을 제안함
.claude/agents/strategy-agent.md의 규약을 따름
"""
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from crewai import LLM
from pathlib import Path

class AgentBriefing:
    def __init__(self, portfolio_df: pd.DataFrame, cash_df: pd.DataFrame, market_data: Dict):
        self.portfolio = portfolio_df
        self.cash = cash_df
        self.market = market_data
        
        # Initialize LLM using the same standard as other agents
        self.llm = LLM(
            model="gemini/gemini-2.0-flash-exp",
            temperature=0.3
        )
        
    def _load_agent_prompt(self) -> str:
        """전략 에이전트 규약 로드"""
        prompt_path = Path(__file__).parent.parent / ".claude" / "agents" / "strategy-agent.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding='utf-8')
        return "You are a strategic investment advisor."

    def generate_briefing(self) -> Dict[str, Any]:
        """마스터를 위한 종합 브리핑 생성 (LLM 기반)"""
        
        # 1. 포트폴리오 요약 정보 생성 (컨텍스트 최소화)
        portfolio_summary = ""
        if not self.portfolio.empty:
            total_v = self.portfolio['평가금액(KRW)'].sum()
            total_p = self.portfolio['손익(KRW)'].sum()
            avg_r = self.portfolio['수익률(%)'].mean()
            
            # 주요 종목 (비중 순)
            top_holdings = self.portfolio.nlargest(5, '평가금액(KRW)')
            holdings_list = []
            for _, row in top_holdings.iterrows():
                holdings_list.append(f"- {row['종목명']}({row.get('티커코드', row.get('종목코드', ''))}): 수익률 {row['수익률(%)']:.1f}%, 비중 {(row['평가금액(KRW)']/total_v*100):.1f}%")
            
            portfolio_summary = f"""
            총 평가금액: ₩{total_v/1e8:.2f}억
            총 손익: ₩{total_p/1e4:.0f}만원
            평균 수익률: {avg_r:.1f}%
            주요 보유 종목:
            {chr(10).join(holdings_list)}
            """
        else:
            portfolio_summary = "포트폴리오 데이터가 비어 있습니다."

        # 2. 시장 상황 요약
        market_summary = json.dumps(self.market, ensure_ascii=False, indent=2)

        # 3. LLM 호출 (전략 수립 원칙 준수 요청)
        system_prompt = self._load_agent_prompt()
        user_prompt = f"""
        [현재 데이터]
        {portfolio_summary}
        
        [시장 상황]
        {market_summary}
        
        [현금 잔고]
        ₩{self.cash['금액'].sum() if not self.cash.empty and '금액' in self.cash.columns else 0:,}
        
        위 데이터를 바탕으로 마스터에게 보고할 '오늘의 요약'과 '3가지 핵심 액션(Nudges)'을 생성해라.
        - 요약은 1-2문장으로 매우 날카롭고 직설적으로 작성할 것 (안정적이라는 상투적 표현 금지).
        - 액션은 'title'과 'content'를 포함한 JSON 형식으로 출력할 것.
        - 출력 형식: {{\"summary\": \"...\", \"nudges\": [{{\"title\": \"...\", \"content\": \"...\"}}, ...]}}
        """

        try:
            response = self.llm.call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # response 처리 (문자열에서 JSON 추출)
            res_content = response if isinstance(response, str) else (response.content if hasattr(response, 'content') else str(response))
            
            # 마크다운 코드 블록 제거 로직 추가
            if "```json" in res_content:
                res_content = res_content.split("```json")[1].split("```")[0]
            elif "```" in res_content:
                res_content = res_content.split("```")[1].split("```")[0]
            
            result = json.loads(res_content.strip())
            
            return {
                "summary": result.get("summary", "분석 결과를 가져오지 못했습니다."),
                "nudges": result.get("nudges", []),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        except Exception as e:
            # Fallback (Error handling)
            return {
                "summary": f"전략 분석 중 오류가 발생했습니다: {str(e)[:50]}",
                "nudges": [{"title": "⚠️ 시스템 점검", "content": "데이터 연동 상태를 확인해 주세요."}],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
