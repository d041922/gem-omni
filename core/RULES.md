# [GEM: OMNI] 시스템 운영 원칙 및 통신 규약

## 1. 아키텍처 개요 (Architecture Overview)

본 시스템은 **Core(헌법) - Agents(사고) - Skills(실행)**의 3층 구조를 따른다.

### 1.1 Core (The Constitution)
- 시스템의 불변하는 가치와 최상위 제어 로직을 담당한다.
- **역할:** 라우팅, 전역 상태 관리, 사용자 의도 파악, 보안 필터링.
- **위치:** `core/`, `main.py`, `GEMINI.md`

### 1.2 Agents (The Thinking Layer)
- 특정 도메인(재정, 건강, 학습 등)에 특화된 사고 모듈이다.
- **역할:** Core로부터 할당받은 작업의 계획 수립, 도구(Skill) 선택 및 호출, 결과 해석.
- **구성:** `FinanceAgent`, `CodingAgent` 등 서브 에이전트로 확장.

### 1.3 Skills (The Action Layer)
- 실제 외부 세계와 상호작용하거나 계산을 수행하는 원자 단위 기능이다.
- **역할:** API 호출, 파일 조작, 데이터 연산.
- **특징:** Stateless하며, 입력과 출력이 명확해야 한다.

---

## 2. 통신 프로토콜 (Communication Protocol)

모든 컴포넌트 간 통신은 명시적인 데이터 구조(JSON/Dict)를 원칙으로 한다.

### 2.1 메인 에이전트(Main) ↔ 서브 에이전트(Sub)
- **요청 (Main -> Sub):**
    ```json
    {
      "task_id": "unique_id",
      "intent": "analyze_portfolio",
      "context": { ... },
      "constraints": [ ... ]
    }
    ```
- **응답 (Sub -> Main):**
    ```json
    {
      "task_id": "unique_id",
      "status": "success | failure | need_info",
      "result": "요약된 결과 텍스트",
      "data": { ...구조화된 데이터... }
    }
    ```

### 2.2 서브 에이전트(Sub) ↔ 스킬(Skill)
- 서브 에이전트는 스킬을 직접 import하거나 스킬 레지스트리를 통해 호출한다.
- 스킬은 실행 결과를 반환하되, 판단(Thinking)을 포함하지 않는다.

---

## 3. 에이전트 행동 지침 (Agent Directives)

1. **상호 배제 (Mutual Exclusion):** 각 서브 에이전트는 자신의 도메인에만 집중한다. (예: 재정 에이전트는 코드를 직접 수정하지 않고 제안만 한다.)
2. **보고 체계:** 작업 수행 중 치명적인 오류 발생 시 즉시 Core에 보고하고 대기한다.
3. **사용자 중심:** 모호한 상황에서는 임의로 판단하지 않고 마스터(사용자)에게 질의한다.

## 4. 확장 슬롯 (Expansion Slots)
현재 초기화된 슬롯은 다음과 같다.
- **[SLOT_01] Finance Agent:** 재정/투자 분석 및 관리 (우선 구현)
- **[SLOT_02] Health Agent:** (미구현)
- **[SLOT_03] Knowledge Agent:** (미구현)
