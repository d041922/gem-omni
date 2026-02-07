# Spec: Prism Insight Integration & Memory System

## 1. 개요 (Overview)
본 문서는 `Prism Insight`의 고급 기능을 `GEM: OMNI`에 이식하여, 시스템에 **영구적 기억(Memory)**과 **자가 학습(Self-Learning)** 능력을 부여하기 위한 명세이다.

## 2. 통합 아키텍처 (Integration Architecture)

### 2.1 Core Memory System (`core/memory.py`)
- **Backend**: `sqlite3` (File: `data/omni.db`)
- **Schema (Prism 참조)**:
    - `memories`: 대화 로그, 마스터의 지시사항.
    - `trading_journal`: 매수/매도 결정의 근거와 결과.
    - `principles`: 저널에서 추출된 마스터의 투자 원칙 (예: "바이오주 금지").
- **Function**:
    - `add_memory(type, content)`: 기억 저장.
    - `recall(query)`: 벡터 유사도 또는 키워드로 관련 기억 검색.
    - `compress()`: 오래된 기억을 요약하여 '원칙'으로 승격.

### 2.2 Reporting Engine (`skills/reporting_engine.py`)
- **Feature**: `Prism`의 `report_generator`를 경량화.
- **Output**: Markdown 리포트를 HTML/PDF로 변환.
- **Trigger**: `Stock Analysis` 페이지에서 "심층 리포트 생성" 버튼 클릭 시 작동.

## 3. 데이터 흐름 (Data Flow)
1. **User Action**: 마스터가 "엔비디아 매수할까?" 질문.
2. **Memory Recall**: `core/memory.py`가 과거 엔비디아 관련 대화와 마스터의 '기술주 선호' 원칙을 인출.
3. **Quant Analysis**: `MarketScreener`가 현재 점수 산출.
4. **Synthesis**: LLM이 기억 + 퀀트 점수를 종합하여 답변 생성.
5. **Journaling**: 마스터의 최종 결정(매수/보류)을 `trading_journal`에 기록.

## 4. 검증 계획
- **Test-Memory-CRUD**: DB 생성, 기억 저장, 조회, 삭제 테스트.
- **Test-Compression**: 10개의 일지가 1개의 원칙으로 요약되는지 테스트.

## 5. 승인 요청
위 설계대로 '기억하는 에이전트'를 구축해도 되겠습니까?
