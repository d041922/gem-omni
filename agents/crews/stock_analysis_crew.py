"""
Stock Analysis Crew
Multi-agent collaboration system for comprehensive stock analysis
"""
from crewai import Crew, Task, LLM, Process
from agents.crewai_agents.stock_agents import (
    create_fundamental_analyst,
    create_sentiment_analyst,
    create_valuation_analyst,
    create_risk_control_agent,
    create_moderator
)
from typing import Dict, Any
import json
import os

# Configure Gemini LLM
gemini_llm = LLM(
    model="gemini/gemini-2.0-flash-exp",
    api_key=os.getenv("GOOGLE_API_KEY")
)


def create_agents():
    """Create all 5 agents for stock analysis"""
    return {
        'fundamental': create_fundamental_analyst(),
        'sentiment': create_sentiment_analyst(),
        'valuation': create_valuation_analyst(),
        'risk_control': create_risk_control_agent(),
        'moderator': create_moderator()
    }


def run_stock_analysis(
    ticker: str,
    analysis_data: Dict[str, Any],
    data_file_path: str,
    portfolio_data: Dict[str, Any] = None
) -> str:
    """
    Run multi-agent stock analysis with debate mechanism

    Args:
        ticker: Stock ticker symbol
        analysis_data: Summary data from analyze_stock()
        data_file_path: Path to full data JSON file
        portfolio_data: Current portfolio holdings for risk analysis (optional)

    Returns:
        Final investment opinion as markdown text
    """
    # Create agents
    agents = create_agents()

    # Extract data for agents
    tech = analysis_data.get("technical_indicators", {})
    fund = analysis_data.get("fundamentals", {})
    news = analysis_data.get("news_sentiment", {})

    # Load user investment profile
    user_profile_path = os.path.join(os.path.dirname(__file__), '..', '..', 'USER_PROFILE.md')
    user_profile_context = ""
    try:
        with open(user_profile_path, 'r', encoding='utf-8') as f:
            user_profile_context = f.read()
    except Exception:
        user_profile_context = """
## 투자 전략 (기본값)
- Core 50-60%: S&P 500, NASDAQ 100, 배당 성장주
- Satellite 40-50%: AI/반도체 25%, 바이오 10%, 한국 성장주 10%
- 단일 종목 최대 15%, 섹터 최대 40%
- ADX 25 이상 진입, PSAR 손절
"""

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
- **ADX: {tech.get('adx', 0):.1f}** (추세 강도 - 25 이상 진입 기준)
- MFI: {tech.get('mfi', 0):.1f} (자금 흐름)
- MA20: ${tech.get('ma20', 0):.2f}, MA60: ${tech.get('ma60', 0):.2f}
- **파라볼릭 SAR: ${tech.get('psar', 0):.2f}** (손절 기준)
- ATR: {tech.get('atr', 0):.2f} (변동성 - 포지션 사이징)

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

---

# 📋 사용자 투자 프로필 (반드시 준수)

{user_profile_context}
"""

    # Add portfolio context for Risk Control Agent (unified utility)
    try:
        from skills.portfolio_utils import get_portfolio_context_for_ai
        portfolio_context = get_portfolio_context_for_ai(ticker)
    except Exception as e:
        print(f"Warning: Could not load portfolio context: {e}")
        portfolio_context = "\n## 📊 현재 포트폴리오 정보\n- 포트폴리오 데이터 로드 실패\n"

    shared_context += portfolio_context

    # Task 1: Fundamental Analysis
    task_fundamental = Task(
        description=f"""
{shared_context}

당신의 역할: 펀더멘털 애널리스트

임무:
1. **Core/Satellite 분류**: {ticker}가 Core 자산(안정적 성장)인지 Satellite 자산(공격적 성장)인지 판단하세요
   - Core 기준: S&P 500, NASDAQ 100 ETF, 대형 배당 성장주 (MSFT, AAPL, JNJ 등)
   - Satellite 기준: AI/반도체, 바이오, 한국 성장주 등 고성장 섹터
2. ROE {fund.get('roe', 0):.1f}%, 영업이익률 {fund.get('operating_margin', 0):.1f}%를 평가하세요
3. 부채비율 {fund.get('debt_to_equity', 0):.1f}, 유동비율 {fund.get('current_ratio', 0):.2f}의 안전성을 판단하세요
4. EPS 성장률 {fund.get('eps_growth', 0):+.1f}%의 지속 가능성을 분석하세요
5. PER {fund.get('pe_ratio', 0):.1f}의 적정성을 평가하세요
6. 목표가와 매수/보유/매도 의견을 제시하세요

출력 형식:
## 펀더멘털 분석 의견
- **자산 분류**: [Core/Satellite]
- 등급: [매수/보유/매도]
- 목표가: $XXX (근거 포함)
- 핵심 논거: (3가지)
""",
        agent=agents['fundamental'],
        expected_output="펀더멘털 분석 의견 (Core/Satellite 분류, 등급, 목표가, 근거)"
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
        agent=agents['sentiment'],
        expected_output="심리 분석 의견 (등급, 시장 심리, 근거)"
    )

    # Task 3: Technical & Valuation Analysis
    task_valuation = Task(
        description=f"""
{shared_context}

당신의 역할: 밸류에이션 및 기술적 분석가

임무:
1. **ADX {tech.get('adx', 0):.1f} 추세 강도 평가** (중요!)
   - ADX < 20: 추세 없음 → 매매 금지 (박스권)
   - ADX 20-25: 약한 추세 → 진입 대기
   - ADX > 25: 강한 추세 → 진입 가능
2. **PSAR ${tech.get('psar', 0):.2f} 기반 손절가 설정** (필수!)
   - 현재 PSAR이 손절 기준선
   - 추세 전환 시 즉시 청산 원칙
3. RSI {tech.get('rsi', 0):.1f}, MFI {tech.get('mfi', 0):.1f}로 과매수/과매도 판단
4. ATR {tech.get('atr', 0):.2f} 기반 변동성 평가 → 포지션 사이징 제안
5. 최적 진입가, 익절가 (1차 50%, 2차 추적), 손절가를 제시하세요

**중요**: ADX < 25이면 "진입 대기" 권장

출력 형식:
## 기술적 분석 의견
- 등급: [매수/보유/매도/진입대기]
- **ADX 평가**: [추세 강함/보통/약함/없음]
- 진입가: $XXX
- **1차 익절가**: $XXX (50% 청산)
- **2차 목표가**: $XXX (추적 손절)
- **손절가 (PSAR)**: ${tech.get('psar', 0):.2f}
- 핵심 논거: (3가지)
""",
        agent=agents['valuation'],
        expected_output="기술적 분석 의견 (ADX 평가, 등급, 진입/익절/손절가, 근거)"
    )

    # Task 4: Risk Control Analysis
    task_risk_control = Task(
        description=f"""
{shared_context}

당신의 역할: 리스크 관리 전문가

임무:
1. **Core/Satellite 균형 체크**
   - 현재 포트폴리오가 Core 50-60%, Satellite 40-50% 범위를 유지하는지 확인
   - {ticker}가 Satellite 종목이라면, 현재 Satellite 비중이 50%를 초과하지 않는지 점검
2. **단일 종목 집중도**: {ticker} 비중이 전체의 15%를 초과하지 않도록 제한
3. **섹터 집중도**: {fund.get('sector', 'N/A')} 섹터가 40%를 초과하지 않도록 점검
   - AI/반도체 섹터는 예외적으로 40%까지 허용
4. **손실 한도**: 이 종목에서 발생 가능한 최대 손실이 전체 포트폴리오의 1-2% 이내인지 확인
5. 적정 포트폴리오 비중을 제안하세요 (예: "Satellite 내 최대 10%, 전체의 5%")

**중요**:
- 앞선 분석가들이 "매수" 의견을 냈더라도, 집중도 리스크가 크다면 반드시 경고하세요
- Satellite > 50% 이면 "Core 비중 부족, 방어력 약화" 경고 필수
- ADX < 25이면 "추세 약함, 진입 대기 권장" 경고

출력 형식:
## 리스크 관리 의견
- 등급: [매수/보유/매도/비중조절/진입대기]
- **Core/Satellite 균형**: [양호/주의/위험]
- **적정 비중**: 전체 포트폴리오의 X% (Satellite 내 Y%)
- **단일 종목 집중도**: [안전/보통/위험]
- **섹터 집중도**: [안전/보통/위험] ({fund.get('sector', 'N/A')} 섹터)
- 핵심 논거: (3가지)
- ⚠️ **경고 사항**: (있다면)
""",
        agent=agents['risk_control'],
        expected_output="리스크 관리 의견 (등급, Core/Satellite 균형, 적정 비중, 집중도 리스크, 경고)"
    )

    # Task 5: Final Decision (Moderator)
    task_decision = Task(
        description=f"""
{shared_context}

당신의 역할: 투자위원회 의장

앞선 4명의 전문가 의견:
1. 펀더멘털 애널리스트 의견 (Core/Satellite 분류 포함)
2. 심리 분석가 의견
3. 기술적 분석가 의견 (ADX, PSAR 평가 포함)
4. 리스크 관리 전문가 의견 (집중도 체크 포함)

임무:
1. 4명의 의견을 종합하여 합의를 도출하세요
2. **ADX < 25이면 "진입 대기" 등급으로 조정하세요** (추세 불충분)
3. **리스크 관리자의 집중도 경고는 최종 의견에 반드시 반영하세요**
4. Core/Satellite 분류를 명확히 하고, 적정 비중을 제안하세요
5. PSAR 기반 손절가를 반드시 포함하세요
6. 익절 전략은 "1차 50% 익절 → Core 이동, 2차 추적" 구조로 작성하세요

출력 형식:
# {ticker} 투자 의견서

## 1️⃣ 최종 투자 등급
**등급**: [매수/보유/매도/진입대기]
**자산 분류**: [Core 자산/Satellite 자산]
**목표가**: $XXX (현재가 ${analysis_data.get('current_price', 0):.2f} 대비 +XX%)
**권장 비중**: 전체 포트폴리오의 X% (Satellite 내 Y%)
**투자 기간**: [단기 (<6개월)/중기 (6개월-2년)/장기 (2년+)]
**ADX 추세 강도**: {tech.get('adx', 0):.1f} ([강함 >25/보통 20-25/약함 <20])

## 2️⃣ 종합 의견
(4명 전문가 의견 요약 및 합의점)

**사용자 전략 부합도**:
- Core 50-60%, Satellite 40-50% 균형 유지: [✅/⚠️]
- 섹터 집중도 40% 이하: [✅/⚠️]
- 단일 종목 15% 이하: [✅/⚠️]

## 3️⃣ 실행 전략
### 진입 전략
- **최적 진입가**: $XXX
- **ADX 조건**: ADX {tech.get('adx', 0):.1f} → [진입 가능/대기 필요]
- **분할 매수**: 1차 매수 50%, 2차 매수 50% (시나리오)
- **최대 투자 비중**: X%

### 익절 전략 (2단계)
- **1차 익절**: $XXX 도달 시 50% 청산 → **Core 자산으로 이동** (복리 강화)
- **2차 목표**: $XXX (나머지 50% 추적 손절로 추세 따라가기)

### 손절 전략 (기계적 실행)
- **손절가 (PSAR)**: ${tech.get('psar', 0):.2f}
- **손절 조건**: PSAR 돌파 시 즉시 청산 (감정 배제)
- **최대 손실 한도**: 전체 포트폴리오의 1-2%

## 4️⃣ 주요 리스크
1. 펀더멘털 리스크:
2. 기술적 리스크:
3. 시장 심리 리스크:
4. **⚠️ 집중도 리스크**: (리스크 관리자 의견)

## 5️⃣ 반대 의견 (Devil's Advocate)
**만약 이 분석이 틀렸다면?**
- 간과한 리스크 1:
- 간과한 리스크 2:
- 대안 시나리오:

## 6️⃣ 모니터링 포인트
### 재평가 필요 시점
- PSAR ${tech.get('psar', 0):.2f} 돌파 (손절)
- ADX {tech.get('adx', 0):.1f} → 20 이하 하락 (추세 소멸)
- 섹터 비중 40% 초과 (리밸런싱)
- Satellite 비중 50% 초과 (익절 → Core 이동)

### 주의 지표
- 기술적: RSI, MACD, 볼린저 밴드
- 펀더멘털: 실적 발표, 가이던스 변경
""",
        agent=agents['moderator'],
        expected_output="최종 투자 의견서 (Core/Satellite 분류, ADX 평가, PSAR 손절가, 2단계 익절 전략 포함)",
        context=[task_fundamental, task_sentiment, task_valuation, task_risk_control]
    )

    # Create crew with tasks
    try:
        crew = Crew(
            agents=[
                agents['fundamental'],
                agents['sentiment'],
                agents['valuation'],
                agents['risk_control'],
                agents['moderator']
            ],
            tasks=[
                task_fundamental,
                task_sentiment,
                task_valuation,
                task_risk_control,
                task_decision
            ],
            process=Process.sequential,
            verbose=True
        )

        # Execute
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"""# 분석 오류

멀티에이전트 분석 중 오류가 발생했습니다.

오류 메시지: {str(e)}

단일 AI 분석을 시도하세요."""
