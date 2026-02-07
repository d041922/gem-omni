# Test Plan: Mandalart Dashboard & UI

## 1. 개요 (Overview)
본 문서는 `app.py` 및 UI 컴포넌트의 안정성을 검증하기 위한 전략을 정의한다. Streamlit의 특성상 완전한 E2E 자동화보다는 **핵심 로직(라우팅, 데이터 바인딩) 단위 테스트**에 집중한다.

## 2. 테스트 환경 (Environment)
- **Framework**: `pytest`
- **Mocking**: `streamlit` 모듈 및 `DataOrchestrator`를 모킹하여 UI 렌더링 로직을 격리 테스트.

## 3. 테스트 케이스 (Test Cases)

### 3.1 Unit Tests: Routing & State (라우팅 검증)

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **UT-R01** | `initial_state_load` | 앱 최초 실행 시 | `st.session_state.current_page`가 'home'으로 초기화됨 |
| **UT-R02** | `navigation_transition`| `navigate_to("wealth")` 호출 시 | `current_page`가 'wealth'로 변경되고 `st.rerun()` 호출됨 (Mock 확인) |

### 3.2 Unit Tests: Data Binding (데이터 바인딩)

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **UT-D01** | `card_value_display` | 오케스트레이터가 정상 데이터 반환 | 'Wealth' 카드에 `total_krw` 값이 포맷팅되어(예: ₩1.5억) 표시됨 |
| **UT-D02** | `empty_data_handling`| 오케스트레이터가 빈 딕셔너리 반환 | 크래시 없이 "Data Loading..." 또는 "N/A" 표시 |
| **UT-D03** | `pnl_color_logic` | 수익률이 양수/음수일 때 | 양수면 Red(#FF4B4B), 음수면 Blue(#1C7ED6) 색상 코드 반환 |

### 3.3 Integration: Component Rendering

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **IT-C01** | `mandalart_grid_structure` | 3x3 그리드 생성 함수 호출 | 9개의 카드 컴포넌트가 순서대로 렌더링 함수를 호출함 |
| **IT-C02** | `briefing_header_injection` | AI 컨텍스트 주입 시 | 헤더 영역에 Markdown 텍스트가 정상적으로 렌더링됨 |

## 4. 실행 및 리포트
UI 테스트는 코드를 직접 실행(`streamlit run`)하기 전, 로직의 건전성을 먼저 확보하는 단계이다.
```bash
pytest tests/test_dashboard_logic.py -v
```
