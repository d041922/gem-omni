# Test Plan: Market Screener (The Hunter)

## 1. 개요 (Overview)
본 문서는 `skills/market_screener.py`와 그 하부 `FactorEngine`의 정확성을 검증하기 위한 테스트 전략을 정의한다. 퀀트 엔진의 신뢰도는 오직 **"계산의 정확성"**에서 나온다.

## 2. 테스트 환경 (Environment)
- **Framework**: `pytest`, `pytest-mock`
- **Data Mocking**: `yfinance` 응답을 모킹하여 특정 가격/거래량 시나리오(RSI 30, 거래량 3배 등)를 강제로 주입.

## 3. 테스트 케이스 (Test Cases)

### 3.1 Unit Tests: FactorEngine (개별 지표 검증)

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **UT-F01** | `calc_rsi_accuracy` | 고정된 종가 리스트 주입 | 계산된 RSI가 표준 공식 결과와 일치 (오차 0.01 이내) |
| **UT-F02** | `calc_vol_surge` | 평균 거래량 100, 현재 300 주입 | `vol_surge` 점수가 가중치에 맞게 만점 처리됨 |
| **UT-F03** | `calc_per_relative` | 종목 PER 10, 섹터 평균 20 주입 | 저평가 가점(Relative Value)이 정상 반영됨 |

### 3.2 Unit Tests: Scoring Logic (통합 점수 검증)

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **UT-S01** | `weighted_sum_check` | 모든 팩터 데이터가 완벽할 때 | `Sum(Factor * Weight) == OMNI Score` 확인 |
| **UT-S02** | **`weight_normalization`** | **PER 데이터가 `None`일 때** | PER 가중치(20%)를 제외한 나머지 지표들의 가중치를 합이 100%가 되도록 재분배하여 점수 산출 |
| **UT-S03** | `score_clipping` | 지표가 비정상적으로 높을 때 | 최종 점수가 100점을 초과하지 않도록 제한(Clipping) |

### 3.3 Integration & Edge Cases

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **IT-01** | `orchestrator_sync` | 스크리닝 결과 업데이트 호출 | `world_state.json`의 `intelligence` 섹션에 정확한 스키마로 기록됨 |
| **EC-01** | `empty_ticker_list` | 빈 리스트를 스크리닝 요청 | 에러 없이 빈 결과 반환 및 로그 기록 |
| **EC-02** | `api_rate_limit_retry` | API 호출 시 429 Error 발생 시뮬레이션 | `tenacity`에 의한 Exponential Backoff 재시도 확인 |
| **EC-03** | `invalid_ticker_format` | 존재하지 않는 티커 ("INVALID") 포함 | 해당 티커만 건너뛰고(Skip) 나머지 정상 처리 |

## 4. 실행 및 리포트
```bash
pytest tests/test_market_screener.py -v
```
결과는 마스터에게 Markdown Table 형식의 **'Quality Report'**로 보고한다.
