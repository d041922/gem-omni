# Spec: Stock Analysis Terminal v2.0 (Intelligence & Professional UI)

## 1. 개요 (Overview)
`Stock Analysis` 페이지를 단순 조회용에서 **'지능형 리서치 터미널'**로 격상한다. TradingView 위젯의 시각화와 에이전트의 검색 지능을 결합한다.

## 2. 지능형 검색 시스템 (Search Engine)
- **Feature**: 자율 완성 드롭다운 (Auto-complete Selectbox).
- **Logic**:
    1. 마스터가 텍스트(예: "Apple") 입력.
    2. 에이전트가 `yfinance.search(query)` 호출하여 상위 5개 티커 리스트 확보.
    3. TradingView 규격에 맞게 변환 (예: `AAPL` -> `NASDAQ:AAPL`).
    4. 드롭다운으로 마스터에게 최종 선택지 제공.

## 3. UI/UX 레이아웃 명세

### 3.1 Top Navigation (Common Header)
- 모든 재정 관련 페이지 상단에 고정되는 4단 메뉴 버튼.
- `[🏠 전체 홈] [🌍 시장 현황] [🎯 종목 발굴] [🔍 종목 상세]`

### 3.2 Main Content Tabs (Investing.com Style)
1. **차트 (Overview)**: TradingView Advanced Chart 위젯 (풀사이즈).
2. **기술적 지표 (Technical)**: TradingView Gauge 위젯 + RSI/MA 상세 데이터.
3. **펀더멘털 (Fundamentals)**: 매출, 영업이익, 시가총액 추이 및 섹터 비교.
4. **AI 통찰 (Research)**: `ResearchEngine`이 생성한 심층 리포트 및 PDF.

## 4. 데이터 매핑 가이드 (TradingView Standard)
- **US Stocks**: `EXCHANGE:TICKER` (e.g., `NASDAQ:NVDA`, `NYSE:PLTR`)
- **KR Stocks**: `KRX:CODE` (e.g., `KRX:005930`)
- **Crypto**: `BINANCE:SYMBOL` (e.g., `BINANCE:BTCUSD`)

## 5. 승인 요청
마스터, "검색 지능"과 "TradingView"가 결합된 이 설계대로 진행해도 되겠습니까?
