"""
Collaborative Finance Crew [GEM: OMNI] - Master Profile Integrated
Orchestrates multi-expert diagnosis based on the Master's Investment Charter.
"""
from crewai import Crew, Task, Agent, Process, LLM
import os
import pandas as pd
import numpy as np
from typing import Dict

# Suppress telemetry
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

# Pro model for strategic reasoning
gemini_pro = LLM(model="gemini/gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY"))

def convert_to_serializable(obj):
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj

def run_portfolio_audit(portfolio_df: pd.DataFrame, cash_balance: float, market_context: Dict) -> str:
    """
    마스터 투자 헌장(USER_PROFILE)이 반영된 심층 포트폴리오 진단
    """
    # 1. 데이터 정제
    holdings = portfolio_df.to_dict(orient='records')
    holdings_clean = [{k: convert_to_serializable(v) for k, v in item.items()} for item in holdings]
    
    macro = market_context.get("macro", {})
    
    # 2. 마스터 프로필 로드 (간략화)
    profile_summary = "공격적 투자 성향, 빠르게 많이 버는 것이 목표. 반도체 외 전력, 로봇, 바이오 등 섹터 변화에 유연함."

    # 3. 에이전트 정의 (전문성 강화)
    macro_analyst = Agent(
        role="Global Macro Strategist",
        goal="시장의 거대 담론과 정치/경제 상황이 자산에 미치는 영향 분석",
        backstory="Wall Street 베테랑 경제학자. 환율, 금리, 지정학적 리스크 전문가.",
        llm=gemini_pro,
        verbose=True
    )

    tactical_trader = Agent(
        role="Tactical Action Commander",
        goal="마스터의 성향과 시장 상황을 조합하여 최적의 매수/매도 우선순위 도출",
        backstory="헤지펀드 출신 트레이더. 마스터의 투자 헌장(USER_PROFILE)을 수호하며 속도감 있는 수익 추구.",
        llm=gemini_pro,
        verbose=True
    )

    # 4. 태스크 정의
    task_macro = Task(
        description=f"""
        현재 매크로 상황: {macro}
        포트폴리오 현황: {holdings_clean}
        
        임무:
        1. 환율 및 금리 변화가 현재 보유 종목에 미치는 긍정/부정적 요인 도출.
        2. 현재 돈의 흐름이 반도체에서 어느 섹터로 이동 중인지 진단.
        """,
        agent=macro_analyst,
        expected_output="매크로 영향 분석 보고서"
    )

    task_strategy = Task(
        description=f"""
        마스터 투자 프로필: {profile_summary}
        
        임무:
        1. 거시 지표와 포트폴리오 성과를 조합하여 '오늘 당장 취해야 할 우선순위 액션' 3가지를 도출하십시오.
        2. '빠르게 많이 번다'는 원칙에 충실한 공격적 리밸런싱 안을 제안하십시오.
        3. 단순 티커가 아닌 한글 종목명으로 설명하십시오.
        """,
        agent=tactical_trader,
        expected_output="최종 통합 전략 보고서 (한국어)",
        context=[task_macro]
    )

    crew = Crew(
        agents=[macro_analyst, tactical_trader],
        tasks=[task_macro, task_strategy],
        process=Process.sequential
    )
    
    try:
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"❌ AI 진단 중 오류 발생: {str(e)}"
