# Design Doc: Missing Methods & Auto-Sync Recovery

## 1. 개요 (Overview)
본 문서는 `DataOrchestrator` 클래스에서 누락된 `is_expired` 메서드를 복구하고, `app.py`의 자동 동기화 로직을 안정화하기 위한 설계서이다.

## 2. 해결 과제 (Problem)
- **Problem A**: `DataOrchestrator`에서 `is_expired` 메서드가 삭제되어 `AttributeError` 발생.
- **Problem B**: `app.py`에서 `sync_portfolio` 호출 시 데이터가 없을 때의 예외 처리 미흡.

## 3. 기술 명세 (Technical Specification)

### 3.1 `is_expired` 메서드 복구
- **Input**: `section: str`, `ttl_seconds: int`
- **Logic**: 
    1. `world_state.json` 로드.
    2. 해당 섹션의 `updated_at` 필드 확인.
    3. 현재 시간과의 차이가 `ttl_seconds`보다 크면 `True` 반환.
    4. 필드가 없거나 1970년도 데이터면 무조건 `True` 반환.

### 3.2 `app.py` 자동 동기화 가드 (Guard)
- **Logic**:
    ```python
    try:
        if orchestrator.is_expired("portfolio", 300):
            orchestrator.sync_portfolio()
    except AttributeError:
        # 메서드 부재 시 수동 동기화 유도 또는 기본값 로드
        pass
    ```

## 4. 검증 계획 (Verification)
- **UT-EX-01**: `DataOrchestrator` 인스턴스 생성 후 `hasattr(obj, 'is_expired')` 검증.
- **UT-EX-02**: `is_expired` 호출 시 실제 시간 차이에 따른 Boolean 결과값 검증.

## 5. 결론
"기능 추가"보다 "구조적 온전함"을 최우선으로 하여, 깨진 클래스 구조를 복원한다.
