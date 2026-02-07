# Spec: Stock Analysis - Advanced Technicals (v2.2)

## 1. 개요 (Overview)
`Stock Analysis` 페이지의 '기술적 분석' 탭에 전문가용 지지/저항 데이터와 다중 이평선 추세판을 추가하여 진입/청산 시점 결정을 돕는다.

## 2. 핵심 지표 명세 (Indicator Specs)

### 2.1 Pivot Points (Standard)
- **Source**: `yfinance` 전일(1d) OHLC 데이터.
- **Formula**:
    - `P (Pivot) = (H + L + C) / 3`
    - `R1 = (2 * P) - L`, `S1 = (2 * P) - H`
    - `R2 = P + (H - L)`, `S2 = P - (H - L)`
- **Display**: 현재가가 각 라인 사이에 어디에 위치하는지 리스트업.

### 2.2 MA Ribbon Status (Trend Tracker)
- **Source**: `yfinance` 최근 200일 종가 데이터.
- **Checked Periods**: 5, 10, 20, 50, 100, 200.
- **Logic**:
    - `Close > MA`: 🟢 Bullish (강세)
    - `Close < MA`: 🔴 Bearish (약세)
- **Display**: 6단계 신호등 레이아웃.

## 3. 구현 계획 (Implementation)
- **Task 1**: `FactorEngine` 클래스에 `calculate_pivot_points` 및 `get_ma_ribbon_status` 메서드 추가.
- **Task 2**: `pages/stock_analysis.py`의 '기술적 분석' 탭 UI 보강.

## 4. 검증 시나리오
- **UT-TECH-01**: 상장한 지 200일이 안 된 종목의 경우 MA200을 "데이터 부족"으로 안전하게 처리하는지 확인.
- **UT-TECH-02**: 계산된 Pivot 포인트가 현재가 주변에 논리적으로 배치되는지 확인.

## 5. 승인 요청
마스터, 위 설계대로 '차트의 뇌'를 강화해도 되겠습니까?
