"""
Stock Analysis Crew (High-Intelligence Mode)
Multi-agent system with Deep Domain Knowledge & Portfolio Awareness.
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
import os

# Configure Gemini LLM (High Temp for Creativity, Low for Precision)
gemini_llm = LLM(
    model="gemini/gemini-2.0-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.4
)

def create_agents():
    # Re-define agents with stronger personas here if needed, 
    # but for now we rely on the imported functions and upgrade their TASKS.
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
    Run multi-agent debate analysis with Enhanced Context.
    """
    agents = create_agents()
    
    # Extract Data
    tech = analysis_data.get("technical_indicators", {})
    fund = analysis_data.get("fundamentals", {})
    news = analysis_data.get("news_sentiment", {})
    
    # --- 1. Portfolio Context (Crucial) ---
    try:
        from skills.portfolio_utils import get_portfolio_context_for_ai
        port_ctx = get_portfolio_context_for_ai(ticker)
    except Exception:
        port_ctx = "포트폴리오 데이터 로드 실패. 일반적인 주가 분석을 수행합니다."

    # --- 2. Data Contexts (Structured for Logic) ---
    common_data = f"""
[Target Asset]
- Ticker: {ticker}
- Current Price: ${analysis_data.get('current_price', 0):.2f}
- Market Cap: ${fund.get('market_cap', 0)/1e9:.1f}B (Large Cap > 10B, Small Cap < 2B)
"""

    fund_context = f"""
[Fundamental Reality]
- Valuation: PER {fund.get('pe_ratio', 0):.1f} (Sector Avg approx 20-30)
- Growth Power: Revenue Growth {fund.get('revenue_growth', 0):.1f}% | PEG {fund.get('peg_ratio', 0):.2f} (PEG < 1 is Undervalued Growth)
- Profit Quality: ROE {fund.get('roe', 0):.1f}% (Outstanding if > 20%)
- Financial Safety: Debt/Equity {fund.get('debt_to_equity', 0):.2f}% (**{fund.get('debt_status', 'N/A')}**)
  > Note: Debt < 100% is safe. Don't panic unless > 200%.
"""

    tech_context = f"""
[Technical Battlefield]
- Trend (ADX 14): {tech.get('adx', 0):.1f} (If < 20: Range, > 25: Trend)
- Momentum (RSI 14): {tech.get('rsi', 0):.1f} (Overbought > 70, Oversold < 30)
- Smart Money (MFI 14): {tech.get('mfi', 0):.1f}
- Structure: Price vs MA200 is {'Bullish' if analysis_data.get('current_price', 0) > tech.get('ma200', 0) else 'Bearish'}
- Risk Line: PSAR ${tech.get('psar', 0):.2f}
"""

    news_context = f"""
[Market Sentiment]
- Mood: {news.get('overall', 'Neutral')}
- Key Narrative: {news.get('summary', 'No specific news')}
"""

    # --- 3. Prompt Definitions (Expert Level) ---
    
    prompt_fund = f"""
{common_data}
{fund_context}

당신은 월가 20년 경력의 **Fundamental Fund Manager**입니다.
단순히 숫자를 읽지 말고, **"이 회사의 비즈니스 퀄리티와 가격의 괴리"**를 찾아내십시오.

**Thinking Process:**
1. **이익의 질**: ROE가 {fund.get('roe', 0):.1f}%라는 것은 이 회사가 자본을 얼마나 효율적으로 굴리는지 보여줍니다. 경쟁사 대비 우월한가요?
2. **성장 정당성**: PER가 높다면, PEG 비율({fund.get('peg_ratio', 0):.2f})을 볼 때 그만한 고성장이 정당화됩니까?
3. **재무 리스크 팩트체크**: 부채비율 평가('{fund.get('debt_status', 'N/A')}')를 신뢰하고, 정말로 돈이 말라서 망할 회사인지 아닌지 판단하십시오.

**Output:**
- **기업 등급**: [S/A/B/C/F] (비즈니스 모델과 실적 기준)
- **밸류에이션**: [저평가/적정/버블] (근거: PEG, PER)
- **매수 근거**: (숫자로 증명된 가장 매력적인 포인트 1가지)
"""

    prompt_tech = f"""
{common_data}
{tech_context}

당신은 차트의 신(God of Charts)이라 불리는 **Technical Trader**입니다.
펀더멘털은 무시하고, 오직 **"가격의 흐름과 심리"**만 꿰뚫어 보십시오.

**Thinking Process:**
1. **추세의 진실**: ADX가 {tech.get('adx', 0):.1f}입니다. 지금이 추세장입니까, 아니면 지루한 박스권입니까? 추세에 역행하지 마십시오.
2. **과열/침체**: RSI가 {tech.get('rsi', 0):.1f}입니다. 지금 사는 건 떨어지는 칼날을 잡는 겁니까, 아니면 달리는 말에 올라타는 겁니까?
3. **손익비 계산**: 지금 진입하면 먹을 구간(Upside)과 잃을 구간(Downside)의 비율이 2:1 이상 나옵니까?

**Output:**
- **추세 판단**: [상승장/하락장/횡보장] (근거: ADX, MA)
- **타이밍**: [지금 당장 매수/눌림목 대기/매도]
- **전술**: 진입가 $XXX | 손절가 $XXX
"""

    prompt_sent = f"""
{common_data}
{news_context}

당신은 시장의 **Behavioral Economist(행동경제학자)**입니다.
뉴스의 팩트보다 **"시장 참여자들이 뉴스에 어떻게 반응하고 있는지"**를 분석하십시오.

**Thinking Process:**
1. **선반영 여부**: 호재가 떴는데 주가가 안 오릅니까? (Sell on news 가능성)
2. **공포 지수**: 지금 사람들이 이 종목을 무서워합니까, 아니면 환장하고 달려듭니까? 남들과 반대로 갈 용기가 필요합니다.

**Output:**
- **군중 심리**: [공포/중립/탐욕]
- **대응 전략**: (군중과 같이 갈 것인가, 역발상으로 갈 것인가)
"""

    prompt_risk = f"""
당신은 냉철한 **Risk Officer(CRO)**입니다.
당신의 임무는 돈을 버는 게 아니라, **"마스터의 계좌를 파산으로부터 지키는 것"**입니다.

**[마스터의 포트폴리오 (현실)]**
{port_ctx}

**Thinking Process:**
1. **포트폴리오 맥락**: 마스터가 이미 이 종목을 많이 가지고 있다면, 아무리 좋아도 "비중 축소"를 외쳐야 합니다. (집중투자 리스크)
2. **손실 한도**: 마스터가 이 종목을 샀다가 -20%가 나면 계좌 전체에 어떤 타격이 옵니까?
3. **팩트 검증**: 앞선 펀더멘털 분석가가 부채비율 같은 걸 잘못 해석했다면 즉시 바로잡으십시오.

**Output:**
- **보유자 조언**: (이미 가진 사람에게: 홀딩/물타기/손절)
- **신규 조언**: (없는 사람에게: 진입금지/분할매수)
- **최대 경고**: (이것만은 조심해라)
"""

    prompt_decision = f"""
당신은 **투자 위원회 의장(Chairman)**입니다.
앞선 4명의 전문가들이 떠든 내용을 종합하여, **마스터에게 "돈이 되는 결론"**을 내려주십시오.

**[의사결정 알고리즘]**
1. **보유 여부 최우선**: {port_ctx}를 보고, 보유자에게는 '관리 전략'을, 미보유자에게는 '진입 전략'을 분리해서 말하십시오. (섞어서 말하지 마세요)
2. **조건부 결론**: "상황 봐서요" 같은 말 금지. **"가격이 $XXX를 뚫으면 산다"**라고 명확한 트리거(Trigger)를 주십시오.
3. **팩트 중심**: 감정적인 형용사 대신, PER, RSI, 평단가 등 **'숫자'**로 설득하십시오.

**최종 리포트 포맷 (Markdown):**

# 🏛️ 투자 위원회 최종 결결: [매수/보유/매도]
> "(결론을 한 문장으로 요약 - 예: 성장성은 좋으나 기술적 과열이므로 조정 시 매수)"

---

## 💼 내 포트폴리오 맞춤 전략
**(이 섹션이 핵심입니다. {port_ctx} 내용을 바탕으로 작성하세요)**
- **나의 상황**: (예: 현재 100주 보유 중, 수익률 -5%)
- **행동 지침**: **[물타기 / 존버 / 익절 / 손절]**
- **이유**: (평단가와 현재 주가 위치를 고려한 논리)

---

## 📉 트레이딩 시나리오 (가격 기준)
- **1차 진입가**: **$XXX** (이 가격 안 오면 사지 마세요)
- **목표가**: **$XXX** (적정 가치)
- **손절가**: **$XXX** (생명선)

---

## 📊 위원회 주요 논의 요약
- **👍 Bullish (찬성)**: (펀더멘털, 기술적 호재)
- **👎 Bearish (반대)**: (리스크 관리자의 경고)
"""

    # --- Tasks Definition ---
    task_fund = Task(description=prompt_fund, agent=agents['fundamental'], expected_output="펀더멘털 전문 보고서")
    task_tech = Task(description=prompt_tech, agent=agents['valuation'], expected_output="기술적 매매 전략 보고서")
    task_sent = Task(description=prompt_sent, agent=agents['sentiment'], expected_output="시장 심리 보고서")
    
    task_risk = Task(
        description=prompt_risk, 
        agent=agents['risk_control'], 
        expected_output="포트폴리오 리스크 관리 보고서",
        context=[task_fund, task_tech, task_sent]
    )
    
    task_decision = Task(
        description=prompt_decision, 
        agent=agents['moderator'], 
        expected_output="최종 투자 의사결정문",
        context=[task_fund, task_tech, task_sent, task_risk]
    )

    # --- Run Crew ---
    try:
        crew = Crew(
            agents=list(agents.values()),
            tasks=[task_fund, task_tech, task_sent, task_risk, task_decision],
            process=Process.sequential,
            verbose=True
        )
        
        # Monkeypatch signal
        import signal
        original_signal = signal.signal
        try:
            signal.signal = lambda *args, **kwargs: None
            result = crew.kickoff()
        finally:
            signal.signal = original_signal
            
        return str(result)
        
    except Exception as e:
        return f"# ⚠️ 분석 중 오류 발생\n\n상세 내용: {str(e)}"