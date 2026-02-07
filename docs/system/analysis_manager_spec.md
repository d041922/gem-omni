# Spec: OMNI Analysis Manager (v1.0)
> "The Strategy Brain that connects Quant and Memory"

## 1. 개요 (Overview)
`MarketScreener`가 발굴한 종목을 `UserMemoryManager`의 과거 데이터 및 `NewsManager`의 시장 심리와 결합하여, 마스터에게 최종 추천 여부를 결정하는 오케스트레이션 모듈이다.

## 2. 분석 파이프라인 (Pipeline)

### 2.1 Input Data
- **Candidate**: `MarketScreener` 결과 (Ticker, Quant Score, Signals).
- **Context**: `NewsManager` 결과 (Market Sentiment).
- **Memory**: `UserMemoryManager` 결과 (Past Win Rate, Principles).

### 2.2 Logic Flow (`skills/analysis_manager.py`)
1.  **Pattern Matching**: 후보 종목의 시그널(예: RSI_Oversold)이 과거 `trading_intuitions`에 존재하는지 조회.
2.  **Win Rate Adjustment**: 과거 승률이 60% 이상이면 가산점, 미만이면 감점.
3.  **Principle Guard**: `investment_principles`에 등록된 금지 키워드(예: "Bio", "Penny Stock") 포함 시 즉시 탈락(Filter Out).
4.  **Final Scoring**: `Quant Score (50%) + Memory Score (30%) + News Score (20%)`

### 2.3 Output Data
- **Strategic Verdict**: "강력 추천 (과거 승률 80% 패턴)"
- **Journaling Preparation**: 매수 시 `trading_journal`에 기록할 초안 생성.

## 3. 기술 명세
- **Dependencies**: `DataOrchestrator`, `UserMemoryManager`, `MarketScreener`.
- **Interface**: `analyze_candidate(ticker: str) -> Dict`

## 4. 검증 계획
- **UT-AM-01**: 금지 원칙(Principle)에 걸리는 종목이 필터링되는지 확인.
- **UT-AM-02**: 과거 승률 데이터가 최종 점수에 반영되는지 확인.

## 5. 승인 요청
위 설계대로 '지능형 분석가'를 구현해도 되겠습니까?
