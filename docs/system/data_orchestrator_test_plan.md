# Test Plan: Data Orchestrator

## 1. 개요 (Overview)
본 문서는 `skills/data_orchestrator.py`의 무결성을 보장하기 위한 테스트 전략을 정의한다. **"코딩 전 테스트 설계"** 원칙에 따라, 구현체는 이 테스트들을 통과하도록 작성되어야 한다.

## 2. 테스트 환경 (Environment)
- **Framework**: `pytest`
- **Mocking**: `unittest.mock`을 사용하여 외부 API(yfinance, kis) 호출을 완벽히 격리(Mock)한다.
- **Fixture**: `tests/fixtures/mock_world_state.json` (표준 스키마 준수 데이터)

## 3. 테스트 케이스 (Test Cases)

### 3.1 Unit Tests (단위 테스트)

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **UT-01** | `read_state_valid_cache` | TTL이 유효한 캐시 데이터 요청 | 파일 I/O 없이 메모리/파일의 기존 데이터 반환 (`is_stale=False`) |
| **UT-02** | `read_state_expired` | TTL(1분)이 지난 데이터 요청 | 내부 `fetch` 로직 트리거 후 업데이트된 데이터 반환 |
| **UT-03** | `atomic_write_integrity` | 임시 파일 생성 및 Rename 동작 검증 | `world_state.json`이 깨지지 않고 정상 갱신됨 |
| **UT-04** | `schema_validation_fail` | API가 잘못된 포맷 반환 시 | 해당 필드 갱신 거부, 기존 값 유지, Error Log 기록 |

### 3.2 Integration Tests (통합 테스트)

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **IT-01** | `cold_start_creation` | `data/` 폴더가 비어있을 때 최초 실행 | `world_state.json` 파일 생성 및 기본 골격(Skeleton) 작성 |
| **IT-02** | `concurrency_lock` | 두 개의 프로세스가 동시에 `update_state` 호출 | `FileLock`에 의해 순차 처리되며 데이터 손실 없음 |

### 3.3 Edge Cases (극한 상황)

| ID | Case Name | Description | Expected Outcome |
|:---|:---|:---|:---|
| **EC-01** | `api_total_blackout` | 모든 외부 API가 Timeout/Error 반환 | `is_stale=True` 상태로 기존 데이터 반환, 시스템 크래시 없음 |
| **EC-02** | `zero_value_anomaly` | 주가/환율이 0 또는 음수로 들어옴 | 갱신 거부, 경고 로그("Anomaly Detected") 출력 |
| **EC-03** | `permission_denied` | `world_state.json` 쓰기 권한 없음 | 명시적 `PermissionError` 발생 및 사용자 보고 |

## 4. 실행 계획
구현 직후 다음 명령어로 검증한다.
```bash
pytest tests/test_data_orchestrator.py -v
```
