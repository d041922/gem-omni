# Plan: UX Localization & Data Integrity Fix (v2.0)

## 1. 개요 (Overview)
본 문서는 자산 가치 계산의 정확성을 확보하고, **하드코딩된 환율을 실시간 데이터로 교체**하며, 한글 중심의 친절한 UX를 구축하기 위한 수정 계획이다.

## 2. 데이터 정합성 및 자동화 (Data & Automation)

### 2.1 실시간 환율 엔진 도입 (No Hard-coding)
- **Action**: `DataOrchestrator` 내부에 `get_realtime_exchange_rate()` 메서드 구현.
- **Source**: `yf.Ticker("USDKRW=X")`를 사용하여 현재 시점의 실시간 환율 페칭.
- **Persistence**: 조회된 환율은 `world_state.json`에 저장하여 모든 계산의 SSOT로 활용.

### 2.2 통화별 지능형 자산 계산 (Currency Intelligence)
- **Logic**: 종목 티커 끝자리를 분석하여 통화 자동 분기.
    - `.KS`, `.KQ` -> KRW (환율 1.0 적용)
    - 그 외 (미국주식 등) -> 실시간 조회된 USD_KRW 환율 적용.

### 2.3 구글 시트 데이터 전처리 (Data Sanitization)
- **Action**: 모든 수치 데이터에서 콤마(`,`), 통화기호(`₩`, `$`)를 제거하는 정규화 함수 적용.

## 3. UX 한글화 및 지능형 브리핑 (UX & Insight)

### 3.1 Signal 매핑 및 배지 UI
영문 시그널을 한글로 변환하고 시각적 태그(Badge) 적용.
- `Oversold` -> `🔵 과매도(저점)`
- `Overbought` -> `🔴 과매수(과열)`
- `Volume Surge` -> `🔥 수급폭발`

### 3.2 AI Briefing 로직 복원
- 데이터를 해석하여 마스터에게 보고하는 'Insight Generator'를 `DataOrchestrator`에 탑재.

## 4. 실행 순서 (Execution Steps)
1. **Step 1**: `DataOrchestrator`의 환율 하드코딩 제거 및 실시간 페칭 로직 구현.
2. **Step 2**: `MarketScreener`에 한글 시그널 매핑 테이블 추가.
3. **Step 3**: `app.py` 및 `wealth_home.py` UI 업데이트.
