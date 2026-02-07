# Spec: OMNI News Intelligence & Daily Briefing (v1.0)

## 1. 개요 (Overview)
전 세계 금융 시장의 방대한 뉴스 중 마스터의 자산과 직결된 정보만 선별하여, 매일 아침(또는 요청 시) 지능형 브리핑을 제공한다.

## 2. 핵심 로직 파이프라인 (Pipeline)

### 2.1 실시간 뉴스 수집 (Exa Engine)
- **Tool**: `web_search_exa`
- **Query Strategy**: 
    - "Major financial events in the last 24 hours"
    - "{보유종목 티커} latest earnings and analyst sentiment"
- **Filter**: `type="news"`, `livecrawl="preferred"`

### 2.2 지능형 요약 및 분석 (Gemini Brain)
- **Input**: Exa 검색 결과 (HTML/Text 파편)
- **Analysis Task**:
    1. **중복 제거**: 여러 매체에서 보도된 동일 이슈 통합.
    2. **영향도 평가**: 긍정/부정/중립 판별 및 포트폴리오 영향도 점수 산출.
    3. **Actionable Advice**: "엔비디아 실적 호조로 인해 기술주 비중 유지를 권장합니다" 등 구체적 조언.

### 2.3 데이터 저장 및 공급 (Orchestration)
- **Storage**: 가공된 브리핑은 `world_state.json`의 `intelligence` 섹션에 패치.
- **Cache**: 1시간 TTL 적용하여 과도한 API 호출 및 토큰 소모 방지.

## 3. UI 컴포넌트 명세
- **Location**: `Market Overview` 상단 '오늘의 시장 핵심 뉴스' 섹션.
- **Format**: 
    - [Headline] (Sentiment Badge)
    - [Impact] "보유 종목 PLTR에 긍정적"
    - [3-line Summary]

## 4. 검증 시나리오
- **UT-NEWS-01**: 보유 종목 리스트가 검색 쿼리에 정상적으로 주입되는지 확인.
- **UT-NEWS-02**: Gemini 응답이 정의된 JSON 규격(`top_stories`, `sentiment`)을 준수하는지 확인.

## 5. 승인 요청
마스터, 위 설계대로 실시간 뉴스 인텔리전스를 구축해도 되겠습니까?
