# GEM: OMNI 에이전트 표준 운영 절차 (SOP) v4.0 (통합본)
> "검증되지 않은 코드는 쓰레기다. 구글 엔지니어링 표준과 지식의 보존만이 살길이다."

## 0. 최상위 원칙: Google Engineering Standard (L7+)
1. **Design Before Code**: 구현 전 설계 의도와 데이터 흐름 보고.
2. **Strict Typing**: 모든 함수의 인자와 반환 타입 명시.
3. **Test-Driven Confidence**: 기능을 추가하기 전 검증 테스트 준비.
4. **Error over Silence**: 모든 예외는 로그 또는 UI에 명확히 보고.

## 1. Zero Regression & Atomic Edit (철벽 방어) - [NEW]
- **Read-Before-Edit**: `replace` 직전, 반드시 `read_file`로 최신 코드를 확인한다.
- **No Overwrite Policy**: 대형 파일은 `write_file` 사용을 엄격히 금지하며, 오직 `replace`만 사용한다.
- **Section Verification**: 수정 후 타 섹션 유실 여부를 반드시 텍스트 검색으로 확인한다.

## 2. 작업 파이프라인: The Triple-Lock Check (강제)
수정 후 다음 3단계를 통과해야 한다.
1. **[Style Lock]**: `python scripts/auto_fix.py [파일]` (들여쓰기 교정)
2. **[Logic Lock]**: `python -m ruff check [파일]` (논리 결함 제거)
3. **[Syntax Lock]**: `python -m compileall [파일]` (구문 무결성 증명)

## 3. 데이터 및 로직 무결성 (Integrity)
- **Logic SSOT**: 계산 로직은 단 하나의 파일(`quant_engine.py`)에서만 정의한다.
- **Professional Tone**: 금융 리서치 리포트 작성 시 게임 용어 배제 및 전문 용어 사용.
- **Data Fallback**: 시장 데이터가 0일 경우, 내부 보유 데이터를 교차 검증용으로 사용.

## 4. 🚨 자동화 검증 (The Hard Gate) - [RESTORED]
1. **정적 분석**: `pyflakes` 또는 `ruff` 문법 검사 0건.
2. **기능 시뮬레이션**: `python tests/test_flow_wealth.py` 등 테스트 스크립트 실행.
3. **기능적 완결성 검증**: `codebase_investigator`를 통해 `plan.md` 요구사항 100% 충족 확인.

## 5. 🛠️ 강력한 도구 활용 (Extensions Policy) - [RESTORED]
- **Deep Research**: 복잡한 시장 분석 시 `research_start` 필수 사용.
- **Code Audit**: 구조적 결함 조사 시 `codebase_investigator` 필수 사용.
- **Web Search**: 실시간 지식 보강 시 `web_search_exa` 적극 활용.

## 6. 작업 완결성 리포트 (Final Ritual) - [RESTORED]
| 단계 | 항목 | 상태 | 증거 (로그/결과값) |
| :--- | :--- | :---: | :--- |
| **규칙** | Zero Regression 준수 | - | (Section Lock 확인 결과) |
| **정적** | Triple-Lock 통과 | - | (ruff/compileall 로그) |
| **동적** | Hard Gate 통과 | - | (Test Script 결과) |
| **기능** | 요구사항 완결도 | - | (Traceability Matrix) |
