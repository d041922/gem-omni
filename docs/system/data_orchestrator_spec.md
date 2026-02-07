# System Spec: Data Orchestrator & State Management

## 1. 개요 (Overview)
본 모듈은 OMNI 시스템의 **'Single Source of Truth (SSOT)'**를 구현하며, 외부 API 호출과 데이터 가공, 캐싱을 총괄한다.

## 2. 데이터 구조 (Advanced Schema) - `data/world_state.json`

단순 플랫 구조가 아닌, **개별 메타데이터와 TTL 관리가 가능한 계층형 구조**를 채택한다.

```json
{
  "metadata": {
    "version": "2.0",
    "system_status": "HEALTHY",
    "last_full_check": "2026-02-06T20:00:00Z"
  },
  "market": {
    "indices": {
      "KOSPI": {"value": 2540.1, "change_pct": 1.2, "updated_at": "2026-02-06T20:44:00Z"},
      "S&P500": {"value": 5020.5, "change_pct": 0.5, "updated_at": "2026-02-06T20:44:00Z"}
    },
    "exchange_rate": {"USD_KRW": 1350.5, "source": "KIS", "updated_at": "2026-02-06T20:44:00Z"}
  },
  "portfolio": {
    "summary": {
      "total_krw": 150000000,
      "daily_pnl_pct": 0.8,
      "updated_at": "2026-02-06T20:45:00Z"
    },
    "holdings": [] 
  }
}
```

## 3. 핵심 로직 규약 (Logic Protocols)

### 3.1 Smart Fetching Logic (Granular TTL)
- **Protocol**: 모든 데이터 섹션은 고유의 TTL을 가진다.
    - `PRICE`: 1분 (주가, 환율)
    - `MACRO`: 30분 (시장 지수, 섹터)
    - `NEWS`: 4시간 (리포트, 뉴스)
- **Action**: `read_state` 호출 시 전체를 갱신하지 않고, **만료된 항목(Leaf Node)만 선별적으로 갱신(Patch)**하여 API 호출을 최소화한다.

### 3.2 Atomic Update (원자적 쓰기)
- **Constraint**: 파일 쓰기 중 시스템 중단(Power Failure)으로 인한 JSON 손상을 방지한다.
- **Implementation**: 
    1. `data/world_state.tmp`에 먼저 쓴다.
    2. 쓰기가 완벽히 끝나면 `os.replace()`로 `world_state.json`을 덮어씌운다.

### 3.3 AI Context Injection (프롬프트 규약)
- **Constraint**: LLM에게 전달하는 컨텍스트는 **Markdown Table** 형식을 우선한다.
- **Reason**: 자연어 나열보다 토큰 효율이 40% 이상 좋으며, LLM이 수치를 구조적으로 이해하기 유리하다.

### 3.4 Defensive Logic (방어적 설계)
- **Retry Strategy**: 
    - 외부 API 호출 실패 시 `Exponential Backoff`를 적용한다. (1초 -> 2초 -> 4초, 최대 3회)
    - `tenacity` 라이브러리 사용 권장.
- **Fallback Hierarchy**:
    1. 최신 라이브 API 데이터
    2. 로컬 캐시 (`world_state.json`)
    3. (Cold Start 실패 시) 하드코딩된 안전 기본값 (Safe Defaults) 또는 명시적 에러 (`SystemHaltException`)
- **Circuit Breaker**: 
    - 연속 5회 이상 API 실패 시, 해당 소스를 30분간 차단(Open)하고 캐시만 반환한다.

## 4. 하부 스킬 의존성 (Dependencies)
- `kis_tools.py`: 한국/미국 실시간 주가 페칭.
- `kr_market_crawler.py`: 국내 섹터/종목 정보.
- `portfolio_utils.py`: 자산 합산 및 수익률 계산 로직.

## 5. 예외 처리 (Error Handling)
- **Schema Validation**: 외부 API에서 `null`이나 비정상적인 값(-999 등)이 들어오면 해당 필드 업데이트를 거부하고 기존 값을 유지한다.
- **Concurrency**: `FileLock`을 사용하여 다중 프로세스/스레드 환경에서의 동시 쓰기 충돌을 방지한다.