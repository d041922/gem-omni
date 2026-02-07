# [Benchmark] Investing.com Stock Analysis Engine

NVIDIA (NVDA)를 기준으로 한 Investing.com의 핵심 정보 아키텍처 분석 리포트입니다.

---

## 1. Technical Analysis (기술적 분석)
### 📊 핵심 지표 Matrix
- **Moving Averages (MA)**: MA5, MA10, MA20, MA50, MA100, MA200의 단순/지수 값을 모두 제공하여 추세 정렬을 시각화.
- **Oscillators**: RSI(14), STOCH(9,6), MACD(12,26), ATR 등 10종 이상의 지표 수치와 'Buy/Sell' 액션을 테이블화.
- **Pivot Points**: 5가지 모델(Classic, Fibonacci 등) 기반의 지지/저항선(S1~R3)을 수치로 명시.

### 🧭 시계열 요약 (Timeframe Summary)
- 5분, 15분, 30분, 1시간, 5시간, Daily, Weekly, Monthly 단위의 'Strong Buy' 신호를 한눈에 표로 제공. (우리의 '단기/중기/장기' 판단 모델의 기초)

---

## 2. Financial Summary (재무 요약)
### 📈 수익성 및 성장성 추이 (Annual/백만 USD)
- **Revenue**: 2021년 $16B -> 2025년 $130B (기하급수적 성장 가시화 필수)
- **Net Income**: 순이익률의 변화 추이를 막대 그래프로 표현.
- **EPS (TTM)**: 현재 4.04 달러.

### ⚖️ 건전성 지표 (Balance Sheet)
- **Total Assets vs Liabilities**: 자산 대비 부채 비율을 직관적으로 배치 (현재 NVDA는 자본 $79B 대비 부채 $18B로 매우 건강).

---

## 3. Analyst Opinion (분석가 의견)
### 🎯 목표가 분포
- **Consensus**: "Strong Buy" (Buy 59, Hold 3, Sell 1)
- **Target Price**: 평균 $253.62 (현재가 대비 약 +47% Upside)
- **Visual**: 애널리스트들의 의견 분포를 원형 차트 또는 게이지로 가시화.

---

## 🚀 [OMNI Implementation Plan] 우리 터미널에 적용할 'Must-Have'
1. **[기술]**: `tab2`에 'Timeframe Matrix' 추가 (단기/장기 추세 통합 판단).
2. **[재무]**: `tab3`에 연간/분기별 매출 및 이익 성장률 차트 강화.
3. **[의견]**: `tab5` 리서치 리포트에 'Analyst Distribution' 수치 반영.
