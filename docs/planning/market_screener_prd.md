# PRD: OMNI Market Screener (The Hunter)

## 1. 개요 (Overview)
**Market Screener**는 방대한 시장 데이터 속에서 마스터의 투자 철학(모멘텀, 기회비용)에 부합하는 종목을 자동으로 찾아내는 '지능형 사냥꾼'이다.

## 2. 목적 (Objectives)
1. **시간 절약**: 수천 개의 종목을 일일이 확인하는 수고를 덜어줌.
2. **객관적 필터링**: 감정을 배제하고 사전에 정의된 '퀀트 팩터'에 의해서만 후보 선정.
3. **기회 포착**: 52주 신고가 근접, 거래량 급증 등 강력한 기술적 시그널 실시간 감지.

## 3. 핵심 기능 (Key Features)

### 3.1 Expanded Factor Library (지표 라이브러리)
단순 지표를 넘어, 세 가지 관점의 다각도 분석을 수행한다.

#### **A. Technical Momentum (기술적 추세)**
- **RSI & MACD**: 단기 과매수/과매도 및 추세 전환 시그널.
- **Bollinger Bands**: 가격 변동성 범위 내 위치 확인.
- **Moving Average Ribbon**: 5, 20, 60, 120일 이평선 정배열 상태(Golden Cross).

#### **B. Fundamental Value (기본적 가치)**
- **Relative Valuation**: 해당 섹터 평균 대비 PER, PBR의 저평가 정도.
- **Profitability (ROE/ROA)**: 기업의 효율적인 자본 운용 능력.
- **Growth (YoY)**: 최근 분기 매출액 및 영업이익 증가율.

#### **C. Supply & Demand (수급 및 시장)**
- **Volume Surge**: 평소 거래량 대비 비정상적 급증 (스마트 머니 유입 감지).
- **Relative Strength vs Index**: S&P 500 또는 KOSPI 대비 해당 종목의 강세 여부.

### 3.2 Actionable Signal & Scoring
- 각 지표는 **'OMNI Score'**로 수치화되어 통합된다.
- **Insight**: "왜 이 종목인가?"에 대해 "섹터 대비 저평가(PER) + 거래량 급증 + RSI 반등"과 같이 구체적 근거를 제시한다.

## 4. 유저 시나리오 (User Scenarios)
1. 마스터가 아침에 앱을 실행함.
2. `Market Screener`가 백그라운드에서 동작하여 '오늘의 유망주 5개'를 추출.
3. UI 상단에 **"🔥 현재 모멘텀이 가장 강력한 종목"** 섹션으로 노출.
4. 마스터가 클릭 시, 상세 분석 페이지로 연결.

## 5. 기술적 제약 사항 (Constraints)
- **Data Source**: `yfinance` 및 크롤러를 통해 최신 시세 확보.
- **Performance**: 500개 이상의 종목 스캔 시 API Rate Limit을 고려한 지연(Delay) 및 캐싱 필수.
- **Output**: 결과값은 반드시 Markdown Table 형식으로 AI 분석기에 전달.
