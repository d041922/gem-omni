# [OMNI Research Report] {{ name | default(ticker) }} ({{ ticker }})
> 분석 섹터: {{ sector | default('Unclassified') }} | 발행 시각: {{ timestamp }}

---

## 0. 핵심 요약 (Executive Summary)
**OMNI 종합 점수: {{ score | default('N/A') }}점**

> {{ ai_summary | default("현재 종목은 퀀트 지표와 시장 심리가 혼조세를 보이고 있습니다. 아래 세부 분석을 참조하십시오.") }}

**🔥 핵심 논쟁점 (Battle Ground):** {{ battle_ground | default("분석 데이터 부족으로 논쟁점이 도출되지 않았습니다.") }}

---

## 1. 기술적 맥락 (Technical Pulse)
| 지표 (Factor) | 수치 (Value) | 상태 및 시그널 |
|:---|:---:|:---|
| **RSI (14)** | {{ details.rsi | default('N/A') }} | {{ '🔵 과매도' if details.rsi and details.rsi <= 35 else '🔴 과매수' if details.rsi and details.rsi >= 70 else '⚪ 중립' }} |
| **거래량 급증** | {{ details.vol_surge_ratio | default(1.0) }}x | {{ '🔥 수급폭발' if details.vol_surge_ratio and details.vol_surge_ratio >= 2 else '정상' }} |
| **52주 고점 대비** | {{ details.fifty_two_week_high_dist | default(0.0) }}% | {{ '📉 저점매수 매력' if details.fifty_two_week_high_dist and details.fifty_two_week_high_dist >= 20 else '⛰️ 고점 근접' if details.fifty_two_week_high_dist and details.fifty_two_week_high_dist <= 5 else '평이' }} |
| **손익비 (RR)** | {{ details.rr_ratio | default('N/A') }} | {{ '🟢 진입유리' if details.rr_ratio and details.rr_ratio|float >= 1.5 else '🟡 관망' }} |
| **추세 정렬** | - | {{ '📈 상승 정배열' if details.is_up_trend else '⚪ 횡보/하락' }} |

---

## 2. 비즈니스 활력 (Business Vitality)
- **시가총액 (Market Cap)**: ₩{{ details.market_cap | default('정보없음') }}
- **배당 수익률 (Div. Yield)**: {{ (details.dividend_yield * 100) | round(2) if details.dividend_yield else '0.00' }}%
- **주식보상비용 (SBC)**: {{ details.sbc_ratio | default('N/A') }}% (매출 대비 비중)
- **기본적 의견**: {{ fundamental_insight | default("현재 시가총액과 수익성 지표를 고려할 때, 섹터 내에서 안정적인 위치를 점하고 있습니다.") }}

---

## 3. 시장 심리 (Market Context)
{% if market_news %}
| 주요 헤드라인 | 감성 (Sentiment) | 연관성 (Impact) |
|:---|:---:|:---|
{% for news in market_news %}
| {{ news.headline }} | {{ news.sentiment }} | {{ news.impact | default('일반') }} |
{% endfor %}
{% else %}
> 현재 해당 종목에 대한 특이 시장 뉴스 시그널이 포착되지 않았습니다.
{% endif %}

---

## 4. 최종 투자 전략 (Strategic Verdict)
** Rating: {{ verdict | default('WATCH') }} **

> **판단 근거**: {{ reason | default("데이터 정밀 분석 결과, 현재는 적극적인 진입보다는 관망하며 추세를 지켜볼 필요가 있습니다.") }}
> 
> **행동 지침 (Action Plan)**: {{ action_plan | default("포트폴리오 비중을 유지하며, 다음 실적 발표 시점까지 모니터링을 강화하십시오.") }}

---
*본 보고서는 OMNI Intelligence Engine v5.0에 의해 자동 생성되었습니다.*