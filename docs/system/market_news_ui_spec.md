# Spec: Market News UI Integration (v1.0)

## 1. 개요 (Overview)
`NewsManager`를 통해 정제된 실시간 금융 뉴스를 `Market Overview` 페이지에 시각화하고, 데이터의 자동 갱신 메커니즘을 구축한다.

## 2. 데이터 흐름 (Data Flow)
1. **Trigger**: `app.py` 또는 `market_overview.py` 진입 시 `is_expired("intelligence", 14400)` (4시간) 체크.
2. **Fetch**: 만료 시 에이전트(나)가 `exa.web_search_exa`를 호출하여 최신 뉴스 수집.
3. **Process**: `NewsManager.generate_strategic_briefing()`으로 3대 이슈 압축.
4. **Display**: `pages/market_overview.py`에서 `world_state.json`의 `daily_briefing` 필드 로드 및 렌더링.

## 3. UI 컴포넌트 명세 (Bento Grid)
- **News Item Card**:
    - **Header**: `headline` (Bold)
    - **Sub-header**: `sentiment` (배지) + `impact` (포트폴리오 연관성)
    - **Body**: `summary` (3줄 제한)
    - **Footer**: "기사 읽기" 링크 버튼

## 4. 기술 제약
- **Rate Limit**: `Exa` API 호출은 세션당 최소화하며, 4시간 캐싱을 엄격히 준수한다.
- **Fail-safe**: 뉴스 수집 실패 시 "현재 시장 뉴스를 가져올 수 없습니다"라는 정중한 안내문 노출.

## 5. 승인 요청
마스터, 위 설계대로 뉴스 데이터를 화면에 연결해도 되겠습니까?
