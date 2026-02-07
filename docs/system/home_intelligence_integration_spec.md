# Spec: Home Dashboard Intelligence Integration (v1.0)

## 1. 개요 (Overview)
`MarketScreener`의 분석 결과 중 가장 가치 있는 정보(Top Pick)를 메인 대시보드(`app.py`)의 'Master Briefing' 섹션에 통합하여 마스터의 빠른 의사결정을 돕는다.

## 2. 데이터 매핑 및 UI 명세 (Data Mapping)

| 기능 (Feature) | 데이터 경로 (Data Path) | UI 표현 (Display) |
|:---|:---|:---|
| **오늘의 원픽** | `intelligence.screener_results[0]` | 브리핑 섹션 하단 'Hero Badge' |
| **핵심 시그널** | `item.signals` (한글 변환) | 컬러 태그 (Badge) |
| **퀀트 스코어** | `item.score` | "전략 점수: XX점" |

## 3. 구현 로직 (`app.py`)

### 3.1 `render_top_pick_card(pick_data: dict)`
- **Input**: 스크리너 1위 종목 데이터.
- **Style**: OMNI Blue 배경의 반투명 유리 카드 스타일.
- **Interaction**: 클릭 시 `Analysis` 페이지로 이동 (티커 자동 입력 기능은 추후 구현).

### 3.2 `render_home` 보강
- `DataOrchestrator.read_state()` 결과에서 상위 종목 존재 여부를 체크하는 로직 추가.
- 데이터 존재 시 `render_top_pick_card`를 브리핑 텍스트 바로 아래 호출.

## 4. 검증 계획
- **UT-HOME-INT**: 스크리너 결과가 비어있을 때 브리핑 섹션이 깨지지 않는지 확인.
- **Visual Audit**: 히어로 카드가 3x3 만다라트 그리드의 균형을 해치지 않는지 확인.

## 5. 승인 요청
마스터, 홈 화면에 '오늘의 사냥 결과'를 전면 배치해도 되겠습니까?
