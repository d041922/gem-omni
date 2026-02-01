# 🛠️ OMNI DevTools v37.0 Specification

**최종 업데이트:** 2026-02-01
**버전:** v37.0 (The Cynic & Transfuser)
**상태:** 정식 운영 (Production Ready)

---

## 1. 핵심 철학 (Core Philosophy)
"Trust, but Verify. And if failing, Transfuse." (신뢰하되 검증하라. 실패하면 지식을 수혈하라.)
본 시스템은 에이전트의 '거짓 성공'을 원천 차단하고, 실제 실행 결과와 의도 일치 여부만을 성공의 척도로 삼습니다.

---

## 2. 5대 공정 정책 (SOP v3.0)

### Phase 1: Research (조사)
- **Gate:** 명세서(spec.md) 내에 `TBD`, `미정`, `unable to` 등 불확실한 표현 발견 시 즉시 반려 및 재조사 수행.

### Phase 2: Design (설계)
- **Gate:** 물리적 파일 경로와 함수 인터페이스가 명확히 정의된 설계도(plan.md) 산출 의무화.

### Phase 3: Implementation (구현)
- **Rule:** 코딩 전 반드시 **한글 논리 설계(Chain of Thought)**를 선행하여 리포트에 기록.
- **Environment:** OS 호환성을 위해 `pip` 대신 `sys.executable -m pip` 사용 강제.

### Phase 4: Review & Transfusion (감리 및 수혈)
- **Strict Review:** 일관성 있는 리뷰어가 과거 지적 사항을 대조하여 '제자리걸음(Stagnant)' 적발 시 즉시 공정 중단.
- **Knowledge Transfusion:** 검수 반려 시 **Exa 전문가**가 실제 코드 샘플을 추출하여 Pilot에게 강제 주입.

### Phase 5: Cynical Verification (회의적 검증)
- **Truth Check:** `Exit Code 0`이라도 로그 내에 `Error`, `Abort`, `Fail` 등의 부정 키워드가 발견되면 무조건 **FAILURE** 판정.

---

## 3. 핵심 모듈 구성
- `orchestrator.py`: 공정 지휘 및 회의적 판정.
- `experts.py`: Deep Research, Exa, Reviewer 정품 확장 프로그램 연결.
- `pilot_controller.py`: CoT 기반 자율 코딩 및 자가 치유 엔진.
- `verification_logic.py`: 키워드 스캔 기반 독한 감리 로직.
- `key_loader.py`: 보안 인증 통합 관리.

---
**This document serves as the absolute protocol for all GEM_OMNI Developer Agents.**
