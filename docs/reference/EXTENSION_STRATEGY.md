# OMNI Extension Strategy & Mapping (Verified)

본 문서는 현재 활성화된 MCP 도구들의 실제 리스트를 기반으로 작성된 **실전 활용 전략서**이다.

## 1. 🛠️ Development (개발 및 보안)

| 활용 시나리오 | 필수 도구 (Tool) | 호출 예시 |
|:---|:---|:---|
| **라이브러리 사용법 조회** | `context7` | `resolve-library-id(libraryName="pandas")` -> `query-docs` |
| **실전 코드/에러 해결** | `exa` | `get_code_context_exa(query="streamlit session state reset pattern")` |
| **보안 점검 (배포 전)** | `security` | `scan_vulnerable_dependencies(paths=["."])` |
| **클라우드 배포/관리** | `gcloud` | `run_gcloud_command(args=["run", "deploy", ...])` |

## 2. 📊 Data & Finance (금융 인텔리전스)

| 활용 시나리오 | 필수 도구 (Tool) | 호출 예시 |
|:---|:---|:---|
| **포트폴리오 원장 관리** | `google-workspace` | `sheets.getText` (읽기), `sheets.update` (쓰기) |
| **기업/시장 심층 조사** | `exa` | `company_research_exa(companyName="Tesla")` |
| **특화 데이터 수집** | `skillz` | `activate_skill(name="apify-finance-scraper")` (활성화 후 사용) |
| **대규모 리포트 생성** | `deep-research` | `research_start(input="2026 AI Sector Outlook", report_format="Deep Dive")` |

## 3. 🏠 Life & Vision (삶의 조율)

| 활용 시나리오 | 필수 도구 (Tool) | 호출 예시 |
|:---|:---|:---|
| **일정/이벤트 연동** | `google-workspace` | `calendar.listEvents` ("이번 달 카드값 나가는 날") |
| **문서/이메일 자동화** | `google-workspace` | `docs.create`(리포트), `gmail.createDraft`(알림) |
| **인맥/연락처 관리** | `google-workspace` | `people.getUserConnections` |

## 4. 🧠 Knowledge & RAG (지식 관리)

| 활용 시나리오 | 필수 도구 (Tool) | 호출 예시 |
|:---|:---|:---|
| **내 문서 기반 답변** | `file-search` | `file_search_upload` -> `file_search_query` (RAG) |
| **새로운 스킬 학습** | `skillz` | `activate_skill(name="skill-creator")` |

---

## ⚠️ 규약: 도구 우선 순위 (Priority)
1.  **Fact**: 최신 정보는 무조건 `exa` 또는 `context7`을 통해 확인한다.
2.  **Sync**: 사용자 데이터는 무조건 `google-workspace`를 통해 원본과 동기화한다.
3.  **Search**: 단순 검색은 `google_web_search`, 심층 연구는 `deep-research`를 사용한다.