# Spec: Stock Analysis v3.0 - Deep Visuals & Earnings

## 1. 개요 (Overview)
`Plotly` 기반의 커스텀 차트 엔진을 도입하여 기술적 지표를 시각화하고, 실적(Earnings) 데이터를 보강하여 펀더멘털 분석의 깊이를 더한다.

## 2. Chart Engine (`skills/chart_tools.py`)
### 2.1 Indicators
- **Bollinger Bands**: 20일 이동평균선 ± 2 * 표준편차.
    - 상단선(Upper), 하단선(Lower), 중심선(Mid).
- **Pivot Points**: 전일 데이터 기반 1차/2차 지지(S) 및 저항(R) 라인.
- **MA Ribbon**: 20, 50, 200일선.

### 2.2 Visualization
- **Plotly Candlestick**: 메인 차트.
- **Overlays**: 볼린저 밴드(채우기 색상 포함), Pivot 수평선(점선).
- **Subplot**: 거래량(Volume) 바 차트.

## 3. Fundamental Augmentation
### 3.1 PEG Ratio Calculation
- `API Value`가 있으면 사용.
- 없으면 `PER / Growth Rate` 로직으로 추정치 계산 (Growth는 최근 4분기 평균 성장률 사용).

### 3.2 Earnings Surprise Chart
- **Source**: `yfinance`의 `earnings_history` 등 가용 데이터.
- **Visual**: 예상치(Estimate)와 실제치(Reported)를 비교하는 Grouped Bar Chart.

## 4. UI/UX Plan (`pages/stock_analysis.py`)
- **Tab 2 (Technical)**: 왼쪽엔 `ChartEngine` 차트, 오른쪽엔 "AI 기술적 해석 요약".
- **Tab 3 (Fundamental)**: 상단엔 밸류에이션(PEG 포함), 하단엔 실적 차트.

## 5. 승인 요청
마스터, 위 설계대로 '보이는 데이터'를 구현해도 되겠습니까?
