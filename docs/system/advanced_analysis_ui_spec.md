# Spec: Advanced Stock Analysis UI (v1.2)

## 1. 개요 (Overview)
`Stock Analysis` 페이지의 사용자 경험을 고도화하여, 리포트 생성 전 통찰을 먼저 제공하고 캐시된 데이터를 효율적으로 활용하도록 개선한다.

## 2. UI/UX 레이아웃 명세

### 2.1 Top: Contextual Awareness
- **Holding Badge**: 보유 중인 종목일 경우, 상단에 'Portfolio Item' 배지와 함께 현재 비중 노출.
- **Price Header**: 실시간 가격과 전일 대비 등락률을 굵게 표시.

### 2.2 Middle: Visual Evidence
- **Interactive Chart**: 캔들스틱 차트에 MA20, MA50 라인 오버레이.
- **Factor Mini-Cards**: RSI, 거래량 배수, 52주 고점 거리를 3개의 미니 Bento 박스로 노출.

### 2.3 Bottom: Smart Reporting
- **Preview Section**: 리포트의 '핵심 요약'과 '투자 의견'을 마크다운으로 실시간 렌더링.
- **Action Area**: 
    - [새 리포트 생성] 버튼 (캐시 무시 옵션).
    - [PDF 다운로드] 버튼 (생성 완료 시 활성화).

## 3. 기술적 로직
- **Caching Workflow**: 
    1. 페이지 로드 시 `ResearchEngine._get_cache_path` 확인.
    2. 존재 시 '불러오기' 모드 활성화.
- **Data Enrichment**: `ResearchEngine._enrich_report_data`를 호출하여 UI에도 포맷팅된 수치(`3.0조` 등) 사용.

## 4. 검증 계획
- **Visual Audit**: 마크다운 미리보기가 `glass-card` 스타일 내에서 깨지지 않고 출력되는지 확인.
- **Cache Test**: 동일 티커 재진입 시 분석 로딩 시간이 0.5초 이내인지 확인.

## 5. 승인 요청
마스터, 위 설계대로 '전문가용 분석 터미널' 수준으로 UI를 끌어올려도 되겠습니까?
