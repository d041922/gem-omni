# Spec: OMNI Self-Evolution Engine (v1.0)
> "Transforming Experience into Wisdom"

## 1. 개요 (Overview)
`EvolutionEngine`은 쌓여가는 투자 일지(`trading_journal`)를 주기적으로 분석하여, 마스터만의 고유한 승리 공식과 패배 공식을 **'투자 원칙(Principle)'**으로 결정화(Crystallize)하는 시스템이다.

## 2. 진화 파이프라인 (The Evolution Pipeline)

### 2.1 Trigger Condition
- **Batch Job**: 매주 주말 또는 일지 데이터가 10건 이상 쌓였을 때 실행.
- **Manual**: 마스터가 "내 매매 복기해줘"라고 명령했을 때 실행.

### 2.2 Logic Flow (`skills/evolution_engine.py`)
1.  **Data Fetching**: `omni.db`에서 최근 완료된(`tracking_status='completed'`) 저널 10~20건 로드.
2.  **Clustering**: 수익률(`outcome`)을 기준으로 **Success Group**과 **Failure Group**으로 분류.
3.  **LLM Pattern Recognition**:
    -   Prompt: "다음 성공 거래들의 공통된 진입 근거(`trigger_type`)와 시장 상황(`situation_analysis`)을 분석하여 하나의 문장으로 요약하라."
    -   Output: "RSI 30 이하에서 진입하고 거래량이 2배 이상일 때 승률이 높다."
4.  **Principle Registration**: 추출된 문장을 `investment_principles` 테이블에 저장 (Source ID 태깅).

## 3. Feedback Application
- 생성된 원칙은 즉시 `AnalysisManager`에 로드되어, 향후 유사한 종목이 포착될 때 가산점/감점 요인으로 작용한다.

## 4. 검증 계획
- **UT-EVO-01**: 긍정적 일지 3개와 부정적 일지 3개를 주입했을 때, 각각 별도의 원칙이 도출되는지 확인.
- **UT-EVO-02**: 도출된 원칙이 DB에 저장되고 `AnalysisManager`가 이를 읽어오는지 확인.

## 5. 승인 요청
마스터, 위 설계대로 OMNI에게 '학습 능력'을 부여해도 되겠습니까?
