"""
Stock Analysis Agents (Multi-Agent System)
Specialized agents for deep stock analysis with debate mechanism
"""
from crewai import Agent
from pathlib import Path
from core.models import default_llm as gemini_llm

def get_persona(agent_name: str) -> dict:
    """`.claude/agents/stock-analyst.md에서 특정 에이전트의 페르소나 정보를 추출합니다."""
    # 실제 프로덕션에서는 정규표현식 등으로 파싱하지만, 
    # 여기서는 구조적 규약에 따라 LLM이 전체 파일을 읽도록 가이드하거나 
    # 간단한 섹션 추출 로직을 사용합니다.
    persona_path = Path(__file__).parent.parent.parent / ".claude" / "agents" / "stock-analyst.md"
    content = persona_path.read_text(encoding='utf-8') if persona_path.exists() else ""
    return content

def create_fundamental_analyst() -> Agent:
    full_persona = get_persona("Fundamental Analyst")
    return Agent(
        role="펀더멘털 애널리스트",
        goal="재무제표와 기업 기본 가치를 분석하여 투자 적격성 판단",
        backstory=f"당신은 SAMAS 시스템의 펀더멘털 전문가입니다. 다음 규약을 따르십시오:\n{full_persona}",
        llm=gemini_llm,
        verbose=True
    )

def create_sentiment_analyst() -> Agent:
    full_persona = get_persona("Sentiment Analyst")
    return Agent(
        role="심리 분석가",
        goal="뉴스와 시장 심리를 분석하여 단기 모멘텀 진단",
        backstory=f"당신은 SAMAS 시스템의 심리 분석 전문가입니다. 다음 규약을 따르십시오:\n{full_persona}",
        llm=gemini_llm,
        verbose=True
    )

def create_valuation_analyst() -> Agent:
    full_persona = get_persona("기술적 분석가")
    return Agent(
        role="밸류에이션 및 기술적 분석가",
        goal="차트 지표와 밸류에이션을 종합하여 진입/청산 시점 제시",
        backstory=f"당신은 SAMAS 시스템의 기술적 분석 전문가입니다. 다음 규약을 따르십시오:\n{full_persona}",
        llm=gemini_llm,
        verbose=True
    )

def create_risk_control_agent() -> Agent:
    full_persona = get_persona("Risk Control Agent")
    return Agent(
        role="리스크 관리 전문가",
        goal="포트폴리오 집중도 관리 및 안정성 확보",
        backstory=f"당신은 SAMAS 시스템의 리스크 관리 전문가입니다. 다음 규약을 따르십시오:\n{full_persona}",
        llm=gemini_llm,
        verbose=True
    )

def create_moderator() -> Agent:
    full_persona = get_persona("Moderator")
    return Agent(
        role="투자위원회 의장",
        goal="전문가 의견 조율 및 최종 합의 도출",
        backstory=f"당신은 투자위원회의 의장입니다. 다음 규약을 바탕으로 결론을 내리십시오:\n{full_persona}",
        llm=gemini_llm,
        verbose=True
    )