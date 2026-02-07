# Spec: OMNI Research Report Template v2.0

## 1. 개요 (Overview)
`Prism Insight`의 전문가급 보고서 양식을 OMNI 스타일로 최적화하여, 고밀도 데이터와 AI 통찰을 마스터에게 전달한다.

## 2. 섹션별 상세 구성 (Section Specs)

### 2.1 [Header] 종목 프로필
- **Data**: `{{ name }} ({{ ticker }}) | {{ sector }}`
- **Style**: 리포트 상단에 배치하여 분석 대상을 명확히 정의.

### 2.2 [Summary] 핵심 요약 (Executive Summary)
- **Data**: `{{ score }}점`, `{{ ai_summary }}`
- **Logic**: OMNI Score를 시각적으로 강조하고, 에이전트의 1줄 총평을 배치.

### 2.3 [Analysis] 3대 입체 진단
1. **기술적 맥락 (Technical Pulse)**: 
    - RSI, 거래량 급증, 52주 고점 대비 할인율(`52w_high_dist`)을 테이블로 구성.
2. **비즈니스 활력 (Business Vitality)**: 
    - 시가총액(`market_cap`), 배당수익률(`dividend_yield`) 등 핵심 펀더멘털 노출.
3. **시장 심리 (Market Context)**: 
    - `market_news` 리스트와 개별 뉴스의 톤(Sentiment) 노출.

### 2.4 [Verdict] 투자 전략 (Strategic Opinion)
- **Data**: `{{ verdict }}`, `{{ reason }}`, `{{ action_plan }}`
- **Style**: 인용구(Blockquote) 형식을 사용하여 '에이전트의 조언'임을 명시.

## 3. 조건부 렌더링 규약
- 데이터가 `0.0`이거나 `N/A`인 경우, 단순히 0으로 표시하지 않고 "데이터 수집 불가" 또는 "정보 없음"으로 우아하게 대체(Jinja2 default 필터 활용).

## 4. 승인 요청
마스터, 위 설계대로 `report_template.md`를 전문가 버전으로 개편해도 되겠습니까?
