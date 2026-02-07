# Spec: Research Report Caching System (v1.0)

## 1. 개요 (Overview)
종목 분석 리포트 생성은 많은 API 호출(yfinance, Exa)과 LLM 토큰을 소모한다. 24시간 유효한 파일 기반 캐시를 도입하여 시스템 효율성을 극대화한다.

## 2. 기술 명세 (Technical Spec)

### 2.1 저장 구조 (Storage)
- **Path**: `data/reports/cache/`
- **Naming**: `{ticker}_{date}.json` (예: `NVDA_20260206.json`)
- **Format**: 
    ```json
    {
      "metadata": {"ticker": "NVDA", "generated_at": "ISO_TIMESTAMP"},
      "markdown": "리포트 본문 내용...",
      "pdf_bytes": "base64_encoded_binary"
    }
    ```

### 2.2 캐시 정책 (Policy)
- **TTL (Time To Live)**: 생성 시점으로부터 24시간.
- **Validation**:
    1. 파일 존재 여부 확인.
    2. 현재 시간 - 파일 생성 시간 < 24시간 인지 확인.
    3. 만료되었거나 파일이 깨진 경우(Corrupted) Miss 처리.

## 3. 구현 로직 (`skills/research_engine.py`)
- `get_report(ticker: str) -> str`: 캐시 먼저 확인 후 없으면 생성 로직 호출.
- `_save_to_cache(ticker, content)`: 생성된 리포트를 원자적 쓰기로 저장.

## 4. 검증 시나리오 (Test Plan)
- **UT-CACHE-01**: 캐시가 없을 때 새 파일이 생성되는지 확인.
- **UT-CACHE-02**: 24시간 이내 요청 시 API 호출 없이 기존 파일 내용을 반환하는지 확인.

## 5. 승인 요청
마스터, 위 설계대로 캐시 시스템을 구축하여 '비용과 속도' 두 마리 토끼를 잡아도 되겠습니까?
