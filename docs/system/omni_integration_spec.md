# Spec: OMNI Grand Integration (v5.0)
> "From Calculator to Thinker: The Self-Evolving Agent"

## 1. 개요 (Overview)
`Prism Insight`의 심층 추적 및 기억 압축 로직을 OMNI에 이식하여, 마스터의 투자 스타일을 학습하고 스스로 진화하는 시스템을 구축한다.

## 2. Deep Memory Architecture (`core/memory.py` 확장)

### 2.1 Schema Upgrade
기존 `user_memories` 외에 다음 테이블을 추가하여 '투자 경험'을 구조화한다.

- **`trading_journal` (경험)**: 개별 매수/매도 결정의 기록.
    - `trigger_type`: 진입 사유 (e.g., 'RSI_Oversold', 'News_Hype')
    - `confidence_score`: 당시의 확신 수준 (0~100)
    - `outcome`: 실제 수익률 (사후 업데이트)
- **`trading_intuitions` (직관)**: 유사한 상황에서의 승률 통계.
    - `pattern`: 'RSI 30 이하 + 거래량 2배'
    - `win_rate`: 75.5%
- **`trading_principles` (원칙)**: 직관이 굳어진 불변의 규칙.
    - "바이오주는 임상 발표 전날 반드시 매도한다."

## 3. Analysis Workflow (The Thinking Process)

### 3.1 Pre-Trade: `AnalysisManager`
- `MarketScreener`가 종목을 포착하면, `AnalysisManager`가 `omni.db`를 조회한다.
- **Memory Check**: "과거에 이런 패턴(Trigger)으로 진입했을 때 승률이 어땠지?"
- **Verdict**: 승률이 60% 미만이면 추천을 보류하거나 경고 메시지("과거 승률 저조")를 첨부한다.

### 3.2 Post-Trade: `PerformanceTracker`
- **Batch Job**: 매일 장 마감 후 실행.
- **Task**: 
    1. `trading_journal`에 기록된 종목의 현재가 조회.
    2. 수익률(`outcome`) 업데이트.
    3. `trading_intuitions`의 승률(`win_rate`) 재계산.

## 4. 구현 로드맵 (Roadmap)
1.  **Step 1 (DB)**: `core/memory.py`에 신규 테이블(`journal`, `intuition`) 추가 및 마이그레이션.
2.  **Step 2 (Logic)**: `skills/analysis_manager.py` 구현 (스크리너 + 메모리 연동).
3.  **Step 3 (Feedback)**: `skills/performance_tracker.py` 구현 (사후 검증).

## 5. 승인 요청
위 설계대로 시스템의 두뇌를 업그레이드해도 되겠습니까?
