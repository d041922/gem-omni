# PRD: OMNI 데이터 오케스트레이터 (Central Data Hub)

## 1. 배경 및 필요성 (Background)
현재 OMNI 시스템은 여러 페이지와 스킬에서 각자 외부 API를 호출하거나 데이터를 처리하고 있다. 이는 다음과 같은 고질적인 문제를 야기한다.
- **데이터 불일치**: 페이지마다 보여주는 숫자가 조금씩 다름.
- **성능 저하 & 비용 발생**: 동일한 데이터를 위해 중복 API 호출 발생.
- **분석의 어려움**: AI가 분석하기 위해 각기 다른 포맷의 데이터를 매번 정제해야 함.

## 2. 목적 (Objectives)
1. **Single Source of Truth (SSOT)**: 모든 데이터는 `data/world_state.json`을 통해서만 공급된다.
2. **효율적 자원 관리**: 캐싱 전략을 통해 외부 API 호출을 최소화하고 응답 속도를 높인다.
3. **AI-Ready Data**: LLM이 즉시 통찰을 도출할 수 있도록 고도로 정제된 데이터 스키마를 제공한다.

## 3. 핵심 기능 (Key Features)

### 3.1 Unified Reading & Writing (동기화)
- **Read:** 모든 UI/LLM 요청에 대해 중앙 캐시(`world_state.json`)를 먼저 조회하여 응답 속도 최적화.
- **Write:** 자산 정보 수정 시 오케스트레이터가 로컬 캐시를 즉시 갱신하고, 비동기(Asynchronous)로 외부 DB(Google Sheets)와 동기화하여 지연 시간 제거.

### 3.2 Intelligent Caching (TTL 정책)
- **Real-time (1m):** 국내외 주식 현재가, 실시간 환율.
- **Mid-term (30m):** 거시 경제 지표, 공포/탐욕 지수, 섹터 모멘텀.
- **Long-term (1h+):** 뉴스 요약, 산업 리포트, 분석 엔진 통찰.

### 3.3 예외 처리 (Error Handling)
- **API Timeout:** 요청 실패 시 'Stale 데이터'를 반환하며, 마스터에게 데이터 시점이 과거임을 명확히 고지.
- **Schema Validation:** 외부 수집 데이터가 표준 스키마에 맞지 않으면 즉시 폐기하고 에러 로그 생성 및 보고.

## 4. 데이터 스키마 규약 (Standard Schema)
모든 응답은 아래의 메타데이터를 포함한다:
- `timestamp`: 데이터 최종 갱신 시간 (ISO 8601)
- `is_stale`: 데이터 신선도 여부 (True/False)
- `data`: 실제 데이터 페이로드 (assets, market_indices, signals 등)

## 4. 유저 시나리오 (User Scenarios)
1. **마스터의 질문**: "내 포트폴리오 지금 어때?"
2. **시스템 동작**:
    - UI가 `Data Orchestrator`에 데이터 요청.
    - 오케스트레이터가 `world_state.json` 확인.
    - 데이터가 낡았다면 API 호출 후 `world_state.json` 업데이트.
    - 정제된 데이터를 UI와 LLM 분석기에 동시에 전달.
3. **결과**: UI의 숫자와 LLM이 읽는 숫자가 100% 일치함.

## 5. 성공 지표 (Success Metrics)
- 페이지 로딩 속도 40% 이상 개선.
- 외부 API 호출 횟수 30% 이상 감소.
- 에이전트 답변 중 "데이터 불일치" 관련 오류 발생 건수 0.
