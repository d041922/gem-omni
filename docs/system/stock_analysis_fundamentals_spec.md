# Spec: Stock Analysis - Deep Fundamentals (v2.1)

## 1. 개요 (Overview)
`Stock Analysis` 페이지의 '펀더멘털' 탭을 대대적으로 보강하여, 기업의 재무 건전성과 시장의 평가(컨센서스)를 시각적으로 전달한다.

## 2. 데이터 매핑 (Data Mapping)

### 2.1 Financial Health (재무 건전성)
- **Source**: `yfinance.Ticker.financials` (연간), `quarterly_financials` (분기)
- **Visualization**: `Plotly` 복합 차트 (Combo Chart)
    - **Bar**: 총 매출 (Total Revenue)
    - **Line**: 순이익 (Net Income)
    - **Annotation**: 전년 동기 대비 성장률 (YoY Growth %)

### 2.2 Analyst Consensus (시장 기대치)
- **Source**: `yfinance.Ticker.info`
- **Visualization**: `Plotly` Bullet Chart (게이지)
    - **Range**: 최저 목표가 ~ 최고 목표가
    - **Marker**: 현재 주가
    - **Target**: 평균 목표가 (`targetMeanPrice`)
    - **Text**: "상승 여력 +15.4%" 등의 직관적 메시지.

### 2.3 Valuation Matrix (가치 평가)
- **Source**: `yfinance.Ticker.info`
- **Visualization**: Metric Card Grid
    - **PER**: Trailing / Forward 비교.
    - **PEG**: 1.0 기준 고평가/저평가 색상 코딩.
    - **PBR**: 자산 가치 대비 평가.

## 3. 구현 계획 (Implementation)
- **Task 1**: `skills/market_screener.py`에 `get_financial_data` 및 `get_consensus_data` 메서드 추가.
- **Task 2**: `pages/stock_analysis.py`의 '펀더멘털' 탭 UI 리팩토링.

## 4. 검증 시나리오
- **UT-FUND-01**: 재무 데이터가 없는 종목(신규 상장 등)일 경우 차트 대신 "데이터 부족" 안내문 노출.
- **UT-FUND-02**: 목표가 데이터가 없을 경우 게이지 차트 숨김 처리.

## 5. 승인 요청
마스터, 위 설계대로 '펀더멘털 분석' 기능을 구현해도 되겠습니까?
