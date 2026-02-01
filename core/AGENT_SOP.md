# GEM: OMNI 에이전트 표준 운영 절차 (SOP) v3.0 (2026-01-31 Update)
> "검증되지 않은 코드는 쓰레기다. 실행 결과로만 증명한다."

## 1. 작업 전 보고 (Pre-Work)
- [블루프린트 & 규칙 확인] 보고 (`docs/system/RULES.md` 참조)
- [작업 계획 & 검증 전략] 보고 (어떻게 테스트할 것인가?)

## 2. 구현 (Implementation)
- **규칙 준수**: 기존 코드 스타일 및 폴더 구조(`docs/`, `scripts/`, `tests/`) 유지.
- **원자적 수정**: 한 번에 너무 많은 파일을 건드리지 않는다.

## 3. 🚨 자동화 검증 (The Hard Gate) - **필수**
코드 수정 후 다음 두 가지 테스트를 반드시 통과해야 한다.

1.  **정적 분석 (Static Analysis)**
    - 명령: `python -m pyflakes [수정된 파일들]`
    - 기준: Syntax Error, NameError, Import Error **0건**.
2.  **기능 시뮬레이션 (Simulation)**
    - 명령: `python tests/test_flow_wealth.py` (또는 해당 기능의 Test Script)
    - 기준: **ALL TESTS PASSED** 로그 확보.

## 4. 작업 완결성 리포트 (Final Ritual)
위 Hard Gate를 통과한 경우에만 작성한다.

| 단계 | 항목 | 상태 | 증거 (로그/결과값) |
| :--- | :--- | :---: | :--- |
| **규칙** | 폴더구조/코딩컨벤션 준수 | - | (확인된 규칙 명시) |
| **정적** | pyflakes 문법 검사 | - | (Clean 로그 첨부) |
| **동적** | AppTest 시뮬레이션 | - | (PASS 로그 첨부) |
| **기능** | 요구사항 구현 완성도 | - | (구현된 핵심 기능 나열) |

**경고: 위 체크리스트의 증거가 '에이전트의 말'이 아닌 '쉘 명령어 실행 결과'여야 한다.**
