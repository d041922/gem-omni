# PRD: OMNI Mandalart Dashboard (The Control Center)

## 1. 개요 (Overview)
OMNI 시스템의 첫 화면이자 마스터의 인생 전체를 조망하는 **'관제 센터'**이다. 
단순한 메뉴 나열이 아닌, **'행복한 나'** 만다라트의 각 영역 상태를 실시간 데이터(SSOT) 기반으로 시각화한다.

## 2. 핵심 가치 (Core Values)
1. **Connectivity**: 퀀트 엔진의 차가운 데이터와 마스터의 따뜻한 삶(비전)을 연결한다.
2. **Immediacy**: 앱을 열자마자 가장 중요한 재정 지표와 AI의 브리핑을 3초 이내에 파악할 수 있게 한다.
3. **Consistency**: UI의 모든 수치는 `Data Orchestrator`의 `world_state.json`과 100% 일치한다.

## 3. UI/UX 상세 구성

### 3.1 Top Section: Intelligence Briefing
- **내용**: `Data Orchestrator`의 AI 컨텍스트를 활용한 개인화 메시지.
- **포맷**: "현재 자산 성장 속도(Wealth Velocity)가 목표 대비 **120%**입니다. 친구 생일 선물을 위해 20만 원을 인출해도 포트폴리오 안전성에 문제가 없습니다."

### 3.2 Main Section: The Mandalart (3x3 Grid)
`001_OMNI_VISION`의 배치를 엄격히 준수한다.

| 위치 | 영역 | 데이터 연동 (Data Source) |
|:---:|:---|:---|
| **Center** | **Happy Me** | 전체 영역 성취도 평균 (현재는 Finance 중심) |
| ↗️ | **Finance** | `portfolio.summary.total_krw`, `daily_pnl_pct` |
| ⬆️ | Health | Locked (Status: Ready) |
| ⬅️ | Career | Locked (Status: Ready) |
| 🔄 | **Sync** | 오케스트레이터의 `last_full_check` 시간 및 갱신 버튼 |

### 3.3 Dashboard Interactions
- **Wealth 클릭 시**: `wealth_home.py` 또는 포트폴리오 상세 분석 페이지로 이동.
- **Sync 클릭 시**: `Data Orchestrator.fetch_world_state(force_refresh=True)` 호출 및 화면 갱신.

## 4. 기술 명세 (Technical Requirements)
- **Framework**: Streamlit `layout="wide"`
- **Data Hook**: `st.session_state`가 아닌 `DataOrchestrator.read_state()`를 직접 참조.
- **Styling**: `pages/style_utils.py`를 활용한 모던하고 다크한 'Professional' 룩 유지.

## 5. 단계별 구현 계획
1. **Step 1**: `app.py` 라우팅 및 3x3 만다라트 레이아웃 리뉴얼.
2. **Step 2**: `Finance` 카드에 `world_state.json` 데이터 바인딩.
3. **Step 3**: 상단 AI Briefing 컴포넌트 추가 및 퀀트 통찰 주입.
