# 🛠️ OMNI DevTools Standard Operating Procedure (SOP v3.0)

**Principle:** "No Artifact, No Progress." (결과물이 없으면 다음 단계는 없다.)

---

## 1️⃣ Phase 1: Research (조사 및 정의)
*   **Actor:** `deep_research.py`
*   **Goal:** 요구사항 정의 및 도메인 분석.
*   **Mandatory Artifacts:**
    *   `spec.md`: 명세서 (목적, 데이터 모델, 핵심 알고리즘 포함).
    *   `requirements.txt`: 필요 라이브러리 목록.
*   **Gate Condition:**
    *   `spec.md`에 "TBD", "미정", "Unknown"이 포함되면 **FAIL**.

## 2️⃣ Phase 2: Design (청사진 제작)
*   **Actor:** `blueprint_maker.py`
*   **Goal:** 아키텍처 및 작업 순서 확정.
*   **Mandatory Artifacts:**
    *   `plan.md`: 작업지시서 (파일 경로, 함수 시그니처, 의존성 포함).
*   **Gate Condition:**
    *   설계된 파일 경로가 실제 프로젝트 루트에 존재하지 않거나 생성 계획이 없으면 **FAIL**.

## 3️⃣ Phase 3: Implementation (기술자의 작업)
*   **Actor:** `pilot_controller.py`
*   **Goal:** 실제 코드 작성 및 수정.
*   **Mandatory Artifacts:**
    *   `Modified Code`: 실제 파이썬 파일.
    *   `test_case.py`: 해당 기능을 검증할 테스트 스크립트.
*   **Rules:**
    *   기존 코드를 삭제하지 말고 **확장(Extend)**하라.
    *   모든 로직은 `try-except`로 감싸라.
*   **Gate Condition:**
    *   코드 내에 `pass`, `...`, `TODO`가 발견되면 **FAIL** (Anti-Cheat).
    *   파일 크기가 비정상적으로 줄어들면 **FAIL**.

## 4️⃣ Phase 4: Review (코드 감리)
*   **Actor:** `reviewer.py`
*   **Goal:** 품질 및 보안 검사.
*   **Mandatory Artifacts:**
    *   `REVIEW_REPORT.md`: 점수 및 지적 사항.
*   **Gate Condition:**
    *   Score < 90점이면 **FAIL**.

## 5️⃣ Phase 5: Verification (물리적 검증)
*   **Actor:** `verification_logic.py`
*   **Goal:** 런타임 무결성 검증.
*   **Mandatory Artifacts:**
    *   `STDOUT.log`: 실행 결과 로그.
*   **Gate Condition:**
    *   `test_case.py` 실행 시 `Exit Code 0`이어야 함.
    *   `STDOUT`이 비어있으면 **FAIL**.
