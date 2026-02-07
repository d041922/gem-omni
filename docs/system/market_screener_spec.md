# System Spec: Market Screener & Factor Scoring

## 1. 개요 (Overview)
본 모듈은 시장 데이터를 수집하여 사전 정의된 퀀트 팩터(Factor)를 바탕으로 종목의 투자 매력도를 수치화한다. 수집된 정보는 `DataOrchestrator`를 통해 `world_state.json`의 `intelligence` 섹션에 저장된다.

## 2. 팩터 스코어링 알고리즘 (Enhanced Scoring)

### 2.1 가중치 설정 규약 (Factor Weight Config)
시스템은 다음 가중치 테이블을 바탕으로 점수를 산출하며, 이는 `data/user_policy.json`에서 마스터가 조정할 수 있다.

| Category | Factor | Weight | Logic |
|:---|:---|:---:|:---|
| **Technical** | RSI (14) | 20% | 30 이하(Bullish), 70 이상(Momentum Play) |
| | MACD Hist | 10% | Histogram 양전환 시 가점 |
| | MA Cross | 10% | 5/20일 골든크로스 시 가점 |
| **Fundamental**| PER vs Sec | 20% | 섹터 평균 PER보다 낮을수록 고득점 |
| | EPS Growth | 10% | YoY 20% 이상 성장 시 가점 |
| **Flow** | Vol Surge | 20% | 5일 평균 대비 거래량 2배 이상 시 고득점 |
| | Rel Strength| 10% | 지수(Index) 수익률 상회 시 가점 |

## 3. 핵심 모듈 설계 (`skills/market_screener.py`)

### 3.1 `class FactorEngine` (New)
- **역할**: 다양한 지표를 독립적으로 계산하여 `MarketScreener`에 공급.
- **Method**: `get_technical_factors()`, `get_fundamental_factors()`, `get_flow_factors()`.

### 3.2 `class MarketScreener`
- **Method**: `calculate_omni_score()`
    - `FactorEngine`에서 넘어온 수치들에 가중치를 곱해 0~100점 산출.
    - 데이터 누락 시 해당 지표는 제외하고 나머지 가중치를 재분배(Normalize)하여 안정성 확보.

### 3.2 배치 처리 및 안정성 (Batching & Safety)
- **Batch Size**: 20종목 단위로 끊어서 처리 (API 차단 방지).
- **Delay**: 배치 사이 1~2초의 의도적 지연 시간 삽입.
- **Cache**: 1시간 이내 스크리닝 결과가 있으면 재계산 없이 캐시 반환.

## 4. 데이터 규격 (Output Schema)

`world_state.json`의 `intelligence` 섹션에 들어갈 구조:

```json
"intelligence": {
  "screener_results": [
    {
      "ticker": "NVDA",
      "score": 85.5,
      "signals": ["RSI Overbought", "Volume Surge"],
      "updated_at": "2026-02-06T21:00:00Z"
    }
  ]
}
```

## 5. AI 인터페이스 (AI Context)
- `generate_screener_table() -> str`: 
    - 상위 종목 리스트를 Markdown Table 형식으로 변환.
    - 예: `| Ticker | Score | Signal | Price |`
