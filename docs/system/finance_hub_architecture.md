# Architecture: OMNI Finance Hub & Tool Integration

## 1. 개요 (Overview)
본 문서는 재정 에이전트의 4대 핵심 화면 구조와 이를 지원하는 외부 도구(Extensions) 및 서브 에이전트의 통합 방식을 정의한다.

## 2. 4단계 분석 깔때기 (The Funnel)

| 단계 | 페이지 (Page) | 핵심 역할 | 필수 도구 (Extension) |
|:---:|:---|:---|:---|
| **Level 1** | **Wealth Home** | 전체 자산 조망 및 전략 비중 관리 | `google-workspace` (Sheets) |
| **Level 2** | **Market Overview** | 글로벌 거시 지표 및 섹터 흐름 분석 | `exa` (Market Search) |
| **Level 3** | **Screener** | 퀀트 팩터 기반 유망 종목 발굴 | `yfinance` (Fast Info) |
| **Level 4** | **Stock Analysis** | 개별 종목 정밀 분석 및 AI 가이드 | `exa` + `Deep Research` |

## 3. 확장 프로그램 강제 통합 규약 (Policy)

### 3.1 Data Flow (SSOT)
- 모든 페이지는 반드시 `DataOrchestrator`를 통해서만 데이터를 읽어야 한다.
- `Market Overview` 구현 시, `exa`를 통해 실시간 뉴스를 가져오는 로직을 `skills/`에 별도로 분리한다.

### 3.2 UI Standards
- `context7`을 활용하여 Streamlit의 최신 컴포넌트(예: `st.dataframe` column_config)를 조회하여 적용한다.
- 모든 차트는 `Plotly`로 통일하며, `pages/style_utils.py`의 스타일 가이드를 준수한다.

## 4. 서브 에이전트 및 스킬 활용 (Sub-Agent & Skills)

### 4.1 Sub-Agents
- **`codebase_investigator`**: 대규모 코드 수정 전/후에 호출하여 아키텍처 위반 사항을 체크한다.
- **`cli_help`**: 신규 익스텐션 도입 시 가용 도구 목록을 사전 스캔한다.

### 4.2 Skills (Active Deployment)
- **`apify-ultimate-scraper`**: `yfinance`가 실패하는 특수 종목(한국 펀드 등) 가격 페칭 시 `skillz`를 통해 활성화하여 사용한다.

## 5. 결론 및 승인
마스터의 '행복한 나'를 위한 재정 인프라를 위 4단계 허브 구조로 확정하며, 모든 개발 과정에 도구 사용을 강제한다.
