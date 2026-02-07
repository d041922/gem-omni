# Spec: Finance Hub Page Consolidation & Refactoring

## 1. 개요 (Overview)
본 문서는 파편화된 기존 분석 페이지들을 `DataOrchestrator` 기반의 4대 핵심 화면으로 통합하고, 구형 `DataManager` 의존성을 완전히 제거하기 위한 상세 명세이다.

## 2. 페이지별 리팩토링 규격

### 2.1 Market Overview (`market_overview.py`)
- **Data Source**: `DataOrchestrator.read_state()["data"]["market"]`
- **Features**:
    - 글로벌 4대 지수 (S&P500, NASDAQ, KOSPI, VIX) 노출.
    - 실시간 환율 및 10년물 국채 금리 추가.
    - `exa` 검색을 통한 '오늘의 시장 주요 뉴스' 3줄 요약 섹션 신설.

### 2.2 Stock Screener (`screener.py`) - NEW
- **Feature**: `MarketScreener`의 상위 20개 종목을 대형 리서치 테이블로 노출.
- **Interactions**: 종목 클릭 시 `Stock Analysis` 페이지로 티커 전달 및 이동.

### 2.3 Stock Analysis (`stock_analysis.py`)
- **Integration**: `wealth_screens/analysis.py`의 레거시 로직을 본 파일로 흡수/통합.
- **Enhanced Features**:
    - `yfinance` 차트 + `exa` 기반 실시간 뉴스 분석 결합.
    - 마스터의 포트폴리오 보유 여부를 `DataOrchestrator`로 체크하여 "보유 중인 종목" 배지 표시.

## 3. 라우팅 가드 (Routing Guard)
- `app.py`의 사이드바 메뉴를 `[홈, 시장현황, 종목발굴, 종목분석]` 4단 체계로 개편한다.

## 4. 검증 전략 (Step 4)
- 각 페이지 로드 시 `DataManager` 임포트가 없는지 `ruff`로 전수 조사.
- `DataOrchestrator` 연동 실패 시 빈 화면 대신 '데이터 동기화 필요' 안내문 노출.
