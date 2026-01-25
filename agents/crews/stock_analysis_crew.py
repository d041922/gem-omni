"""
Stock Analysis Crew
Multi-agent collaboration system for comprehensive stock analysis
"""
from crewai import Crew, Task
from agents.crewai_agents.stock_agents import (
    create_fundamental_analyst,
    create_sentiment_analyst,
    create_valuation_analyst,
    create_moderator
)
from typing import Dict, Any
import json


def create_stock_analysis_crew() -> Crew:
    """
    Create a crew of 4 agents for stock analysis

    Agents:
    1. Fundamental Analyst
    2. Sentiment Analyst
    3. Valuation & Technical Analyst
    4. Moderator (Chairman)
    """
    # Create agents
    fundamental_analyst = create_fundamental_analyst()
    sentiment_analyst = create_sentiment_analyst()
    valuation_analyst = create_valuation_analyst()
    moderator = create_moderator()

    # Create crew
    crew = Crew(
        agents=[
            fundamental_analyst,
            sentiment_analyst,
            valuation_analyst,
            moderator
        ],
        verbose=True
    )

    return crew


def run_stock_analysis(
    ticker: str,
    analysis_data: Dict[str, Any],
    data_file_path: str
) -> str:
    """
    Run multi-agent stock analysis with debate mechanism

    Args:
        ticker: Stock ticker symbol
        analysis_data: Summary data from analyze_stock()
        data_file_path: Path to full data JSON file

    Returns:
        Final investment opinion as markdown text
    """
    crew = create_stock_analysis_crew()

    # Extract data for agents
    tech = analysis_data.get("technical_indicators", {})
    fund = analysis_data.get("fundamentals", {})
    news = analysis_data.get("news_sentiment", {})

    # Shared context for all agents
    shared_context = f"""
# 종목 분석 데이터

## 기본 정보
- 종목: {ticker} ({analysis_data.get('name', ticker)})
- 현재가: ${analysis_data.get('current_price', 0):.2f}
- 52주 범위: ${analysis_data.get('52week_low', 0):.2f} - ${analysis_data.get('52week_high', 0):.2f}
- 현재 위치: {analysis_data.get('position_52w_pct', 0):.1f}%

## 기술적 지표
- RSI: {tech.get('rsi', 0):.1f}
- MACD: {tech.get('macd', 0):.2f}
- ADX: {tech.get('adx', 0):.1f} (추세 강도)
- MFI: {tech.get('mfi', 0):.1f} (자금 흐름)
- MA20: ${tech.get('ma20', 0):.2f}, MA60: ${tech.get('ma60', 0):.2f}
- 파라볼릭 SAR: ${tech.get('psar', 0):.2f}

## 펀더멘털
- 섹터: {fund.get('sector', 'N/A')}
- PER: {fund.get('pe_ratio', 0):.1f}, PBR: {fund.get('price_to_book', 0):.2f}
- ROE: {fund.get('roe', 0):.1f}%, 영업이익률: {fund.get('operating_margin', 0):.1f}%
- 부채비율: {fund.get('debt_to_equity', 0):.1f}, 유동비율: {fund.get('current_ratio', 0):.2f}
- EPS 성장률: {fund.get('eps_growth', 0):+.1f}%

## 뉴스 심리
- 뉴스 개수: {news.get('news_count', 0)}개
- 감성: 긍정 {news.get('positive', 0):.0f}% / 중립 {news.get('neutral', 0):.0f}% / 부정 {news.get('negative', 0):.0f}%
- 종합: {news.get('overall', '중립')}
- 요약: {news.get('summary', '')}

## 상세 데이터 파일
{data_file_path}
"""

    # Task 1: Fundamental Analysis
    task_fundamental = Task(
        description=f"""
{shared_context}

당신의 역할: 펀더멘털 애널리스트

임무:
1. ROE {fund.get('roe', 0):.1f}%, 영업이익률 {fund.get('operating_margin', 0):.1f}%를 평가하세요
2. 부채비율 {fund.get('debt_to_equity', 0):.1f}, 유동비율 {fund.get('current_ratio', 0):.2f}의 안전성을 판단하세요
3. EPS 성장률 {fund.get('eps_growth', 0):+.1f}%의 지속 가능성을 분석하세요
4. PER {fund.get('pe_ratio', 0):.1f}, EV/EBITDA {fund.get('ev_to_ebitda', 0):.1f}의 적정성을 평가하세요
5. 목표가와 매수/보유/매도 의견을 제시하세요

출력 형식:
## 펀더멘털 분석 의견
- 등급: [매수/보유/매도]
- 목표가: $XXX (근거 포함)
- 핵심 논거: (3가지)
""",
        agent=crew.agents[0],  # Fundamental Analyst
        expected_output="펀더멘털 분석 의견 (등급, 목표가, 근거)"
    )

    # Task 2: Sentiment Analysis
    task_sentiment = Task(
        description=f"""
{shared_context}

당신의 역할: 심리 분석가

임무:
1. 뉴스 감성 (긍정 {news.get('positive', 0):.0f}%, 부정 {news.get('negative', 0):.0f}%)을 해석하세요
2. 시장 심리가 과열/과냉인지 판단하세요
3. 군중 심리(FOMO, 공포)에 따른 리스크를 진단하세요
4. 단기 모멘텀 관점에서 매수/보유/매도 의견을 제시하세요

출력 형식:
## 심리 분석 의견
- 등급: [매수/보유/매도]
- 시장 심리: [과열/정상/과냉]
- 핵심 논거: (3가지)
""",
        agent=crew.agents[1],  # Sentiment Analyst
        expected_output="심리 분석 의견 (등급, 시장 심리, 근거)"
    )

    # Task 3: Technical & Valuation Analysis
    task_valuation = Task(
        description=f"""
{shared_context}

당신의 역할: 밸류에이션 및 기술적 분석가

임무:
1. RSI {tech.get('rsi', 0):.1f}, ADX {tech.get('adx', 0):.1f}, MFI {tech.get('mfi', 0):.1f}를 종합 평가하세요
2. 추세 강도와 모멘텀을 분석하세요
3. 최적 진입가, 익절가, 손절가를 제시하세요
4. 기술적 관점에서 매수/보유/매도 의견을 제시하세요

출력 형식:
## 기술적 분석 의견
- 등급: [매수/보유/매도]
- 진입가: $XXX
- 익절가: $XXX, 손절가: $XXX
- 핵심 논거: (3가지)
""",
        agent=crew.agents[2],  # Valuation Analyst
        expected_output="기술적 분석 의견 (등급, 진입/익절/손절가, 근거)"
    )

    # Task 4: Final Decision (Moderator)
    task_decision = Task(
        description=f"""
{shared_context}

당신의 역할: 투자위원회 의장

앞선 3명의 전문가 의견:
1. 펀더멘털 애널리스트 의견
2. 심리 분석가 의견
3. 기술적 분석가 의견

임무:
1. 3명의 의견을 종합하여 합의를 도출하세요
2. 의견 충돌 시 다수 의견을 채택하되, 소수 의견도 리스크에 반영하세요
3. 최종 투자 의견서를 작성하세요

출력 형식:
# {ticker} 투자 의견서

## 1️⃣ 최종 투자 등급
**등급**: [매수/보유/매도]
**목표가**: $XXX (현재가 대비 +XX%)
**투자 기간**: [단기/중기/장기]

## 2️⃣ 종합 의견
(3명 전문가 의견 요약 및 합의점)

## 3️⃣ 실행 전략
### 진입 전략
- 최적 진입가: $XXX
- 분할 매수 시나리오

### 익절 전략
- 1차 목표: $XXX
- 2차 목표: $XXX

### 손절 전략
- 손절가: $XXX
- 손절 조건

## 4️⃣ 주요 리스크
1. 리스크 1
2. 리스크 2
3. 리스크 3

## 5️⃣ 반대 의견 (Devil's Advocate)
**만약 이 분석이 틀렸다면?**
- 간과한 리스크 1
- 간과한 리스크 2
- 대안 시나리오

## 6️⃣ 모니터링 포인트
- 주의 깊게 볼 지표
- 재평가 시점
""",
        agent=crew.agents[3],  # Moderator
        expected_output="최종 투자 의견서 (구조화된 마크다운)",
        context=[task_fundamental, task_sentiment, task_valuation]
    )

    # Create tasks list
    tasks = [
        task_fundamental,
        task_sentiment,
        task_valuation,
        task_decision
    ]

    # Execute crew with tasks
    try:
        result = crew.kickoff(tasks=tasks)
        return str(result)
    except Exception as e:
        return f"""# 분석 오류

멀티에이전트 분석 중 오류가 발생했습니다.

오류 메시지: {str(e)}

단일 AI 분석을 시도하세요."""
