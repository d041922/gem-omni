# **클로드 CLI 및 모델 컨텍스트 프로토콜(MCP) 기반의 에이전틱 개인 자산 관리 시스템 설계 및 구축에 관한 종합 연구 보고서**

## **에이전틱 금융의 도래와 지능형 자산 관리의 패러다임 전환**

현대 자본시장의 복잡성이 증대됨에 따라 개인 투자자가 직면하는 정보의 비대칭성과 분석의 한계는 더욱 심화되고 있다. 이러한 배경에서 대규모 언어 모델(LLM)과 에이전틱 워크플로우(Agentic Workflow)의 결합은 단순한 기술적 진보를 넘어 개인 자산 관리의 패러다임을 근본적으로 변화시키고 있다.1 특히 앤트로픽(Anthropic)이 선보인 클로드 코드(Claude Code)와 모델 컨텍스트 프로토콜(Model Context Protocol, MCP)은 인공지능이 단순한 조언자를 넘어 파일 시스템에 직접 접근하고, 외부 API와 실시간으로 통신하며, 스스로 코드를 수정하고 실행하는 자율적 실행체로 진화할 수 있는 토대를 마련하였다.1

본 보고서는 클로드 CLI를 핵심 엔진으로 활용하고, 커서(Cursor)를 통한 정밀한 엔지니어링, 스트림릿(Streamlit)을 통한 직관적인 인터페이스 구현을 통해 전문가 수준의 개인 자산 관리 에이전트를 구축하는 포괄적인 프레임워크를 제시한다.6 특히 기존의 '바이브 코딩(Vibe Coding)'이 갖는 불확실성과 유지보수의 취약성을 극복하기 위해 에이전틱 엔지니어링(Agentic Engineering)의 원칙을 적용하며, 제미나이(Gemini) 및 노트북LM(NotebookLM)을 활용한 심층 리서치 파이프라인의 통합 방안을 상세히 고찰한다.9

## **클로드 코드(Claude Code)의 에이전틱 아키텍처와 핵심 기능**

클로드 코드는 개발자의 터미널 내에서 작동하는 단순한 인터페이스를 넘어, 인간 프로그래머가 사용하는 모든 도구에 접근할 수 있는 권한을 가진 자율 에이전트이다.1 자산 관리 시스템의 중추로서 클로드 코드는 컨텍스트 관리, 도구 사용, 그리고 다중 에이전트 협업이라는 세 가지 핵심 축을 중심으로 작동한다.12

### **하위 에이전트(Sub-agents)와 컨텍스트 분리 전략**

복잡한 자산 관리 업무는 단일 컨텍스트 내에서 처리될 경우 급격한 성능 저하와 '컨텍스트 부패(Context Rot)' 현상을 겪게 된다.15 클로드 코드는 이를 해결하기 위해 하위 에이전트 아키텍처를 도입하여 각 업무를 독립된 작업 공간으로 분리한다.13

| 에이전트 유형 | 주요 기능 및 특성 | 컨텍스트 운용 방식 |
| :---- | :---- | :---- |
| **Main Agent** | 전체 전략 수립 및 하위 에이전트 오케스트레이션 | 전역 설정 및 CLAUDE.md 로드 15 |
| **Explore Agent** | 코드베이스 및 데이터 구조의 신속한 파악 | 읽기 전용 도구 위주의 경량 컨텍스트 13 |
| **Plan Agent** | 분석 방법론 설계 및 구현 단계 논리 구성 | 상태 변화 전 아키텍처 설계 집중 13 |
| **Custom Agent** | 퀀트 분석, 시장 리서치 등 특정 도메인 전문화 | 전용 시스템 프롬프트 및 도구 제한 13 |

이러한 분리 구조는 하위 에이전트가 특정 임무를 수행한 후 그 결과만을 상위 에이전트에게 요약 보고하게 함으로써, 메인 에이전트의 200,000 토큰 컨텍스트 윈도우를 깨끗하게 유지하고 의사결정의 정확도를 극대화한다.15 특히 사용자는 \~/.claude/agents/ 디렉토리에 마크다운 형식의 시스템 프롬프트를 정의함으로써 자신만의 전문 자산 관리 하위 에이전트를 생성할 수 있다.13

### **에이전트 스킬(Skills)을 통한 전문 지식의 모듈화**

스킬(Skills)은 에이전트에게 특정 분야의 전문 지식과 워크플로우를 패키징하여 제공하는 파일 시스템 기반의 기능이다.12 자산 관리 에이전트의 전문성은 이러한 스킬의 정교함에서 결정된다.12

1. **계층적 구조**: 스킬은 SKILL.md를 필수로 하는 디렉토리 구조를 가지며, 메타데이터(Level 1), 세부 지침(Level 2), 그리고 실행 스크립트 및 참조 데이터(Level 3)로 구성된다.12  
2. **동적 로딩**: 클로드는 모든 스킬의 메타데이터를 기동 시 로드하지만, 실제 세부 지침과 코드는 해당 스킬이 필요하다고 판단되는 시점에만 컨텍스트에 불러온다.12 이는 토큰 효율성을 비약적으로 향상시킨다.12  
3. **네트워크 및 로컬 권한**: 클로드 코드 내의 스킬은 로컬 컴퓨터의 전체 네트워크 접근 권한을 가지므로, 실시간 시장 데이터 수집 및 외부 API 호출에 제약이 없다.12

에이전트가 "현재 내 포트폴리오의 리스크를 평가해줘"라는 요청을 받으면, 미리 정의된 risk-analysis 스킬이 트리거되어 관련 Python 스크립트를 실행하고, 최신 거시 경제 지표를 조회하며, 사전에 입력된 리스크 관리 철학에 따라 보고서를 생성한다.12

## **모델 컨텍스트 프로토콜(MCP)과 금융 데이터 생태계 통합**

금융 시장은 방대한 양의 정형 및 비정형 데이터가 실시간으로 교차하는 공간이다. MCP는 이러한 외부 데이터 소스와 AI 에이전트 사이의 '표준화된 통로' 역할을 수행하며, 자산 관리 시스템의 데이터 무결성을 보장한다.4

### **주요 금융 MCP 서버 및 도구 분석**

전문가 수준의 에이전트를 위해서는 신뢰할 수 있는 데이터 소스를 확보하는 것이 필수적이다.20 현재 시장에서 활용 가능한 주요 MCP 서버들은 각기 다른 영역의 데이터 우위를 점하고 있다.21

| MCP 서버 카테고리 | 대표 서버 및 도구 | 제공되는 핵심 데이터/기능 |
| :---- | :---- | :---- |
| **글로벌 마켓** | Alpha Vantage, Yahoo Finance | 전 세계 주식, 외환, 암호화폐, 기술적 지표 21 |
| **전문 리서치** | Octagon AI, Financial Datasets | SEC 필링, 수익 보고서, 기업 IR 자료 전문 분석 22 |
| **매매 및 계좌** | Alpaca, Brokerage API | 주문 실행, 포트폴리오 잔고 확인, 실시간 손익 계산 4 |
| **국내 시장(한국)** | jjlabsio, kospi-kosdaq-server | DART 공시 데이터, KRX 시세, 투자자별 매매 동향 27 |

이러한 MCP 서버들은 claude\_desktop\_config.json 파일을 통해 통합 관리된다.26 클로드 코드는 이 설정을 공유하여 사용자의 자연어 명령을 정교한 API 요청으로 변환한다.4 예를 들어, "삼성전자의 3개년 배당 수익률 추이를 뽑고, 관련 공시 자료에서 향후 주주 환원 정책의 변화가 있는지 요약해줘"라는 명령은 korea-stock-mcp의 get\_financial\_statement와 get\_disclosure 도구를 결합하여 수행된다.27

## **전문가 수준의 투자 워크플로우 및 의사결정 프레임워크**

바이브 코딩의 한계인 '직관에 의존한 단편적 분석'을 극복하기 위해서는 실제 자산 운용사(Asset Management)가 따르는 표준적인 투자 프로세스를 에이전트의 논리 구조에 이식해야 한다.9 전문적인 투자 프로세스는 시장 조사, 종목 분석, 포트폴리오 구축, 실행 및 사후 관리의 순환 구조를 가진다.30

### **시장 분석 및 자산 배분 전략 (Top-Down Approach)**

에이전트는 투자 대상 종목을 찾기 전, 현재 시장의 국면과 거시 경제적 환경을 선제적으로 진단해야 한다.33 이는 개별 종목의 수익률보다 자산 배분(Asset Allocation)이 전체 포트폴리오 성과에 미치는 영향이 더 크기 때문이다.35

1. **시장 주기 분석**: 찰스 슈왑의 4단계 시장 주기(축적, 상승, 분산, 하락)를 기준으로 현재 위치를 평가한다.33  
2. **거시 지표 모니터링**: 금리(Fed Rate), 인플레이션(CPI/PCE), 변동성 지수(VIX) 등을 Alpha Vantage MCP를 통해 실시간으로 수집한다.24  
3. **자산 배분 모델링**: 현대 포트폴리오 이론(MPT) 혹은 블랙-리터만 모델(Black-Litterman)을 적용하여 위험 대비 기대 수익률을 최적화하는 자산 비중을 도출한다.35

#### **자산 배분 최적화 수식 예시 (Sharpe Ratio)**

포트폴리오의 효율성을 측정하기 위해 샤프 지수를 활용하며, 에이전트는 이를 극대화하는 방향으로 비중을 조절한다.

![][image1]  
여기서 ![][image2]는 포트폴리오 기대 수익률, ![][image3]는 무위험 수익률, ![][image4]는 포트폴리오 수익률의 표준편차(변동성)를 의미한다.

### **심층 종목 분석 및 근거 플로우 (Bottom-Up)**

종목 선정 단계에서 에이전트는 정량적 지표와 정성적 근거를 결합한 '투자 메모(Investment Memo)'를 작성하도록 설계되어야 한다.20

| 분석 차원 | 주요 지표 및 도구 | 전문가적 해석 기준 |
| :---- | :---- | :---- |
| **수익성** | ROE, 영업이익률, EPS 성장률 | 자본 효율성이 산업 평균 대비 우수한지 확인 19 |
| **재무 건전성** | 부채비율, 유동비율 | 불황을 견딜 수 있는 현금 동원 능력이 있는지 평가 38 |
| **가치 평가** | P/E, P/B, EV/EBITDA, DCF | 내재 가치 대비 저평가 여부 및 역사적 밴드 확인 20 |
| **기술적 모멘텀** | SMA(20/50/200), RSI, MACD | 장기 추세 정배열 및 과매도 국면 탈출 확인 33 |
| **뉴스 및 심리** | 뉴스 헤드라인 감성 분석 | 시장의 기대치가 주가에 선반영되었는지 진단 19 |

에이전트는 단순히 지표를 나열하는 것이 아니라, "P/E가 낮음에도 불구하고 최근 기관 수급이 이탈하고 있으며, 뉴스 분석 결과 경영권 분쟁이라는 하드 카탈리스트(Hard Catalyst)가 존재하므로 보수적 접근이 필요함"과 같은 종합적인 판단을 내려야 한다.37

## **제미나이(Gemini) 및 노트북LM(NotebookLM)을 통한 리서치 파이프라인 고도화**

클로드 코드가 실행과 분석의 중심이라면, 구글의 제미나이 1.5 프로와 노트북LM은 방대한 비정형 데이터를 처리하고 지식 베이스를 구축하는 데 있어 강력한 보조 엔진이 된다.41 특히 노트북LM은 업로드된 문서에만 기반하여 답변하는 'Grounding' 능력이 탁월하여 투자 분석의 정확도를 높인다.10

### **노트북LM MCP 및 스킬 통합 전략**

에이전트가 수동으로 정보를 복사-붙여넣기 하는 과정을 없애기 위해 notebooklm-mcp 서버나 전용 스킬을 활용한다.10

1. **지식 저장소 구축**: 사용자는 기업의 연례 보고서(10-K), 컨퍼런스 콜 스크립트, 개인적인 리서치 노트를 노트북LM에 업로드한다.11  
2. **에이전트 질의**: 클로드 에이전트는 필요한 시점에 노트북LM에게 "이 기업의 지난 4분기 실적 발표에서 경영진이 언급한 공급망 리스크의 세부 내용은 무엇인가?"라고 묻는다.43  
3. **출처 기반 답변**: 노트북LM은 문서 내 특정 페이지와 문장을 인용하며 답변을 제공하고, 클로드는 이를 바탕으로 투자 논거를 강화한다.10

이러한 파이프라인은 클로드의 뛰어난 코드 실행 능력과 제미나이의 거대한 컨텍스트 처리 능력을 결합하여, 수천 페이지의 문서를 순식간에 분석하고 실행 가능한 투자 신호로 변환하는 '슈퍼 리서처'를 탄생시킨다.11

## **스트림릿(Streamlit) 대시보드 및 사용자 인터페이스 설계**

자율 에이전트 시스템일지라도 최종적인 투자의 책임은 인간에게 있으며, 이를 위해 에이전트의 사고 과정과 포트폴리오 상태를 한눈에 파악할 수 있는 인터페이스가 필요하다.7 스트림릿은 파이썬만으로 전문가급 BI 대시보드를 구축할 수 있게 해준다.7

### **대시보드 아키텍처 및 실시간 모니터링**

스트림릿 대시보드는 에이전트 SDK와 연결되어 실시간으로 데이터를 시각화한다.46

* **포트폴리오 상태 관제**: 보유 종목의 비중, 수익률, 섹터별 분산도를 파이 차트와 시계열 그래프로 표시한다.7  
* **에이전트 루프 스트리밍**: 하위 에이전트들이 현재 어떤 도구를 사용하고 있는지, 시장의 어떤 데이터를 수집 중인지 실시간 텍스트로 노출한다.46  
* **투자 제안 및 인터랙션**: 에이전트가 도출한 매매 제안에 대해 '승인' 혹은 '반려'를 선택할 수 있는 위젯을 배치한다.49  
* **리스크 알림**: 포트폴리오 드리프트(Drift)가 설정한 임계치(예: 5%)를 넘어설 경우 경고 메시지를 띄우고 리밸런싱 주문 생성을 권고한다.50

스트림릿은 특히 'BI as Code' 컨셉에 부합하여, AI가 생성한 코드를 즉시 웹 앱으로 배포하고 수정할 수 있어 개인 투자자가 자신의 전략 변화에 맞춰 대시보드를 민첩하게 고도화하는 데 최적의 도구이다.45

## **바이브 코딩 극복을 위한 에이전틱 엔지니어링 실무**

단순히 AI에게 코드를 맡기는 '바이브 코딩'은 프로젝트의 규모가 커질수록 유지보수 불능 상태에 빠지게 된다.9 이를 극복하기 위해 클로드 코드를 활용한 개발 단계에서는 다음의 소프트웨어 공학적 규칙을 준수해야 한다.53

### **CLAUDE.md를 활용한 컨텍스트 유지 및 메모리 관리**

클로드 코드는 세션마다 CLAUDE.md 파일을 자동으로 로드하여 개발 환경의 규칙과 상태를 인식한다.15

1. **전역 설정 (\~/.claude/CLAUDE.md)**: 개인의 투자 철학, 선호하는 프로그래밍 언어 스타일(예: "모든 금융 계산은 decimal 라이브러리를 사용하라"), 그리고 공통적으로 적용될 위험 관리 가이드라인을 정의한다.15  
2. **프로젝트 설정 (./CLAUDE.md)**: 해당 프로젝트의 데이터 구조, 사용된 MCP 서버 목록, 그리고 "포트폴리오 리밸런싱 스크립트 실행 전 반드시 백테스팅 결과를 먼저 제시하라"와 같은 구체적인 워크플로우 제약을 명시한다.15  
3. **참조 파일 관리**: 너무 많은 정보를 CLAUDE.md에 담아 컨텍스트를 낭비하지 않도록, 세부적인 API 명세나 과거 수익률 데이터는 별도의 마크다운 파일로 분리하고 필요할 때만 참조하도록 유도한다.15

### **매뉴얼 승인 및 계획 수립 모드 활용**

클로드 코드의 \--permission-mode plan 혹은 하위 에이전트의 Plan 모드를 적극 활용하여, 에이전트가 실제 파일 시스템을 수정하기 전 반드시 논리적 타당성을 검토받도록 한다.13 "이 코드가 내 실제 계좌의 주문 API를 호출하는가?" 혹은 "수익률 계산식에서 배당금이 누락되지 않았는가?"와 같은 질문을 던져 에이전트의 작업을 검증하는 절차가 바이브 코딩의 리스크를 줄이는 핵심이다.14

## **결론: 에이전틱 자산 관리자의 미래와 기술적 완성**

클로드 CLI와 MCP 생태계를 기반으로 구축된 개인 자산 관리 에이전트는 개인 투자자에게 기관 수준의 데이터 분석력과 실행력을 부여한다.1 이는 단순히 수익률을 높이는 도구를 넘어, 시장의 소음 속에서 명확한 투자 원칙을 지키게 돕는 지능형 파트너로서의 가치를 지닌다.3

시스템의 완성도는 기술의 나열이 아닌, 투자의 '근거(Evidence)'를 얼마나 체계적으로 관리하고 검증하느냐에 달려 있다.59 하위 에이전트를 통한 업무 분담, MCP를 통한 신뢰할 수 있는 데이터 통합, 그리고 노트북LM을 활용한 비정형 데이터의 정량화는 현대적 자산 관리 시스템이 지향해야 할 기술적 지향점이다.4 본 보고서에서 제시한 설계 가이드를 바탕으로 구축된 시스템은 바이브 코딩의 불확실성을 걷어내고, 데이터와 논리에 기반한 지속 가능한 투자 성과를 창출하는 강력한 자산이 될 것이다.9

#### **참고 자료**

1. Building agents with the Claude Agent SDK \- Anthropic, 1월 25, 2026에 액세스, [https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)  
2. From Deep Learning to LLMs: A survey of AI in Quantitative Investment \- arXiv, 1월 25, 2026에 액세스, [https://arxiv.org/html/2503.21422v1](https://arxiv.org/html/2503.21422v1)  
3. Large Language Models for Financial and Investment Management: Applications \- MIT Media Lab, 1월 25, 2026에 액세스, [https://web.media.mit.edu/\~xdong/paper/jpm24b.pdf](https://web.media.mit.edu/~xdong/paper/jpm24b.pdf)  
4. Alpaca MCP Server, 1월 25, 2026에 액세스, [https://docs.alpaca.markets/docs/alpaca-mcp-server](https://docs.alpaca.markets/docs/alpaca-mcp-server)  
5. The Ultimate Guide to the Official Alpaca Trading MCP Server \- Skywork.ai, 1월 25, 2026에 액세스, [https://skywork.ai/skypage/en/ultimate-guide-official-alpaca-trading/1978674241763659776](https://skywork.ai/skypage/en/ultimate-guide-official-alpaca-trading/1978674241763659776)  
6. Claude Code 2.1 NEW Update IS HUGE\! Sub Agents /skills, Claude Canvas, LSPs, & MORE\!, 1월 25, 2026에 액세스, [https://www.youtube.com/watch?v=s0JCE3WCL3s](https://www.youtube.com/watch?v=s0JCE3WCL3s)  
7. Streamlit • A faster way to build and share data apps, 1월 25, 2026에 액세스, [https://streamlit.io/](https://streamlit.io/)  
8. squadbase/streamlit-claude-code-starter \- GitHub, 1월 25, 2026에 액세스, [https://github.com/squadbase/streamlit-claude-code-starter](https://github.com/squadbase/streamlit-claude-code-starter)  
9. Vibe Coding vs Agentic Coding: A Shift in Developer Mindset \- Rocket.new, 1월 25, 2026에 액세스, [https://www.rocket.new/blog/vibe-coding-vs-agentic-coding-a-shift-in-developer-mindset](https://www.rocket.new/blog/vibe-coding-vs-agentic-coding-a-shift-in-developer-mindset)  
10. I got tired of copy-pasting NotebookLM answers into Claude, so I built an MCP server for it : r/ClaudeAI \- Reddit, 1월 25, 2026에 액세스, [https://www.reddit.com/r/ClaudeAI/comments/1o84y0r/i\_got\_tired\_of\_copypasting\_notebooklm\_answers/](https://www.reddit.com/r/ClaudeAI/comments/1o84y0r/i_got_tired_of_copypasting_notebooklm_answers/)  
11. The CLI Tool That Unlocks Google NotebookLM | by Ewan Mak | Jan, 2026 | Medium, 1월 25, 2026에 액세스, [https://medium.com/@tentenco/notebooklm-py-the-cli-tool-that-unlocks-google-notebooklm-1de7106fd7ca](https://medium.com/@tentenco/notebooklm-py-the-cli-tool-that-unlocks-google-notebooklm-1de7106fd7ca)  
12. Agent Skills \- Claude API Docs \- Claude Console, 1월 25, 2026에 액세스, [https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)  
13. Create custom subagents \- Claude Code Docs, 1월 25, 2026에 액세스, [https://code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)  
14. How to Create AI Agents using Claude Agent SDK (A Step by Step Guide) \- Helply, 1월 25, 2026에 액세스, [https://helply.com/blog/create-ai-agent-using-claude-agent-sdk](https://helply.com/blog/create-ai-agent-using-claude-agent-sdk)  
15. How to Use Claude Code: A Guide to Slash Commands, Agents ..., 1월 25, 2026에 액세스, [https://www.producttalk.org/how-to-use-claude-code-features/](https://www.producttalk.org/how-to-use-claude-code-features/)  
16. Can someone tell me what's going on here? Iykyk and I want to know. Please...coworking, subagent migration, claude cli vs claude code desktop cli thingy : r/ClaudeAI \- Reddit, 1월 25, 2026에 액세스, [https://www.reddit.com/r/ClaudeAI/comments/1qijif2/can\_someone\_tell\_me\_whats\_going\_on\_here\_iykyk\_and/](https://www.reddit.com/r/ClaudeAI/comments/1qijif2/can_someone_tell_me_whats_going_on_here_iykyk_and/)  
17. How I use Claude Code for real engineering, 1월 25, 2026에 액세스, [https://www.youtube.com/watch?v=kZ-zzHVUrO4](https://www.youtube.com/watch?v=kZ-zzHVUrO4)  
18. Extend Claude with skills \- Claude Code Docs, 1월 25, 2026에 액세스, [https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)  
19. Building a Multi-Agent AI System for Financial Market Analysis \- Analytics Vidhya, 1월 25, 2026에 액세스, [https://www.analyticsvidhya.com/blog/2025/02/financial-market-analysis-ai-agent/](https://www.analyticsvidhya.com/blog/2025/02/financial-market-analysis-ai-agent/)  
20. Top Fundamental Analysis Tools for 2026 (Buyer's Guide) \- AlphaSense, 1월 25, 2026에 액세스, [https://www.alpha-sense.com/resources/product-articles/fundamental-analysis-tools/](https://www.alpha-sense.com/resources/product-articles/fundamental-analysis-tools/)  
21. Awesome MCP Servers, 1월 25, 2026에 액세스, [https://mcpservers.org/](https://mcpservers.org/)  
22. Top 10 Best MCP (Model Context Protocol) Servers in 2026 \- Cyber Press, 1월 25, 2026에 액세스, [https://cyberpress.org/best-mcp-servers/](https://cyberpress.org/best-mcp-servers/)  
23. Beginner-friendly Yahoo Finance MCP server for Claude. Get real-time stock data, charts, financials, analyst ratings, and compare multiple companies. \- GitHub, 1월 25, 2026에 액세스, [https://github.com/danishashko/yahoo-finance-mcp](https://github.com/danishashko/yahoo-finance-mcp)  
24. Best MCP servers for stock market data and algorithmic trading \- Medium, 1월 25, 2026에 액세스, [https://medium.com/data-science-collective/best-mcp-servers-for-stock-market-data-and-algorithmic-trading-ca51e89cd0a1](https://medium.com/data-science-collective/best-mcp-servers-for-stock-market-data-and-algorithmic-trading-ca51e89cd0a1)  
25. Popular MCP Servers \- Glama, 1월 25, 2026에 액세스, [https://glama.ai/mcp/servers](https://glama.ai/mcp/servers)  
26. Alpaca's official MCP Server lets you trade stocks, ETFs, crypto, and options, run data analysis, and build strategies in plain English directly from your favorite LLM tools and IDEs \- GitHub, 1월 25, 2026에 액세스, [https://github.com/alpacahq/alpaca-mcp-server](https://github.com/alpacahq/alpaca-mcp-server)  
27. AI, Meet the Korean Stock Market: A Deep Dive into the jjlabsio DART & KRX MCP Server, 1월 25, 2026에 액세스, [https://skywork.ai/skypage/en/ai-korean-stock-market-dive/1979045039327977472](https://skywork.ai/skypage/en/ai-korean-stock-market-dive/1979045039327977472)  
28. Unlocking Korean Markets: The Ultimate AI Engineer's Guide to the KOSPI/KOSDAQ Stock Data MCP Server \- Skywork.ai, 1월 25, 2026에 액세스, [https://skywork.ai/skypage/en/korean-markets-ai-engineer-guide/1977632329143742464](https://skywork.ai/skypage/en/korean-markets-ai-engineer-guide/1977632329143742464)  
29. The AI Engineer's Guide to the Yahoo Finance MCP Server by narumi \- Skywork.ai, 1월 25, 2026에 액세스, [https://skywork.ai/skypage/en/ai-engineer-yahoo-finance-mcp-server/1979015379360010240](https://skywork.ai/skypage/en/ai-engineer-yahoo-finance-mcp-server/1979015379360010240)  
30. How the Asset Management & Mutual Funds Industries Work \- Umbrex, 1월 25, 2026에 액세스, [https://umbrex.com/resources/how-industries-work/banking-financial-services/how-the-asset-management-mutual-funds-industry-works/](https://umbrex.com/resources/how-industries-work/banking-financial-services/how-the-asset-management-mutual-funds-industry-works/)  
31. Investment Process Flow Chart \- Slide Geeks, 1월 25, 2026에 액세스, [https://www.slidegeeks.com/powerpoint/Investment-Process-Flow-Chart](https://www.slidegeeks.com/powerpoint/Investment-Process-Flow-Chart)  
32. Trade Strategy and Execution | CFA Institute, 1월 25, 2026에 액세스, [https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/trade-strategy-execution](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/trade-strategy-execution)  
33. The Four Stages of the Stock Market Cycle | Charles Schwab, 1월 25, 2026에 액세스, [https://www.schwab.com/learn/story/four-stages-stock-market-cycles](https://www.schwab.com/learn/story/four-stages-stock-market-cycles)  
34. The Future of Asset Management: the Macro Imperative \- AllianceBernstein, 1월 25, 2026에 액세스, [https://www.alliancebernstein.com/content/dam/global/insights/insights-whitepapers/the-future-of-asset-management.pdf](https://www.alliancebernstein.com/content/dam/global/insights/insights-whitepapers/the-future-of-asset-management.pdf)  
35. Asset Allocation Software \- Informa Connect, 1월 25, 2026에 액세스, [https://informaconnect.com/zephyr/asset-allocation/](https://informaconnect.com/zephyr/asset-allocation/)  
36. How to Rebalance Your Stock Portfolio with Python | by Intrinio \- Medium, 1월 25, 2026에 액세스, [https://intrinio.medium.com/how-to-rebalance-your-stock-portfolio-with-python-71a188d70087](https://intrinio.medium.com/how-to-rebalance-your-stock-portfolio-with-python-71a188d70087)  
37. Tired of Spending 2 Hours Daily on Stock Market Research? Use This Agentic AI System Instead \- DataDrivenInvestor, 1월 25, 2026에 액세스, [https://medium.datadriveninvestor.com/tired-of-spending-2-hours-daily-on-stock-market-research-use-this-agentic-ai-system-instead-d53bbc54075f](https://medium.datadriveninvestor.com/tired-of-spending-2-hours-daily-on-stock-market-research-use-this-agentic-ai-system-instead-d53bbc54075f)  
38. Five Key Components of Investment Manager Selection and Monitoring \- Trust Point, 1월 25, 2026에 액세스, [https://trustpointinc.com/five-key-components-of-investment-manager-selection-and-monitoring/](https://trustpointinc.com/five-key-components-of-investment-manager-selection-and-monitoring/)  
39. Use case: Analyze financial statements and calculate ratios | Gemini Enterprise, 1월 25, 2026에 액세스, [https://docs.cloud.google.com/gemini/enterprise/docs/use-case-analyze-financial-statements](https://docs.cloud.google.com/gemini/enterprise/docs/use-case-analyze-financial-statements)  
40. Top 3 Prompts for Analyzing Stock Drivers with Perplexity \- Prospero.ai, 1월 25, 2026에 액세스, [https://www.prospero.ai/resources-blog/top-3-prompts-for-analyzing-stock-drivers-with-perplexity](https://www.prospero.ai/resources-blog/top-3-prompts-for-analyzing-stock-drivers-with-perplexity)  
41. Analyzing Financial Reports with Gemini 1.5 | by Ertuğrul Demir | Medium, 1월 25, 2026에 액세스, [https://ertugruldemir.medium.com/analyzing-financial-reports-with-gemini-1-5-8d8695578a79](https://ertugruldemir.medium.com/analyzing-financial-reports-with-gemini-1-5-8d8695578a79)  
42. AI for Finance | Google Workspace, 1월 25, 2026에 액세스, [https://workspace.google.com/solutions/ai/finance/](https://workspace.google.com/solutions/ai/finance/)  
43. Use this skill to enable Claude Code to communicate directly with your Google NotebookLM notebooks. Query your uploaded documents and get source-grounded, citation-backed answers from Gemini. Features browser automation, library management, persistent authentication, and answers exclusively from your own knowledge base. \- GitHub, 1월 25, 2026에 액세스, [https://github.com/PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill)  
44. The Secret to Connecting Claude Code and NotebookLM : r/AISEOInsider \- Reddit, 1월 25, 2026에 액세스, [https://www.reddit.com/r/AISEOInsider/comments/1qbl7b7/the\_secret\_to\_connecting\_claude\_code\_and/](https://www.reddit.com/r/AISEOInsider/comments/1qbl7b7/the_secret_to_connecting_claude_code_and/)  
45. From GUI Dashboards to BI-as-Code: Free Streamlit \+ AI Handbook \- Reddit, 1월 25, 2026에 액세스, [https://www.reddit.com/r/BusinessIntelligence/comments/1lsd7qg/from\_gui\_dashboards\_to\_biascode\_free\_streamlit\_ai/](https://www.reddit.com/r/BusinessIntelligence/comments/1lsd7qg/from_gui_dashboards_to_biascode_free_streamlit_ai/)  
46. How to build a ClickHouse-backed AI Agent with Streamlit ..., 1월 25, 2026에 액세스, [https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/streamlit-agent](https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/streamlit-agent)  
47. Building a Convex MCP Server with Live Agent Dashboard in Streamlit \- Medium, 1월 25, 2026에 액세스, [https://medium.com/@bravekjh/building-a-convex-mcp-server-with-live-agent-dashboard-in-streamlit-21ff0a149c48](https://medium.com/@bravekjh/building-a-convex-mcp-server-with-live-agent-dashboard-in-streamlit-21ff0a149c48)  
48. Automating Portfolio Rebalancing with Python and Strategy | by Time Money Code | Medium, 1월 25, 2026에 액세스, [https://medium.com/@timemoneycode/automating-portfolio-rebalancing-with-python-and-strategy-ef56dde96725](https://medium.com/@timemoneycode/automating-portfolio-rebalancing-with-python-and-strategy-ef56dde96725)  
49. Customer support agent \- Claude API Docs, 1월 25, 2026에 액세스, [https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat](https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat)  
50. Transform Portfolio Management: How AI Agents Automate Rebalancing & Trade Execution, 1월 25, 2026에 액세스, [https://datagrid.com/blog/ai-agents-portfolio-rebalancing](https://datagrid.com/blog/ai-agents-portfolio-rebalancing)  
51. Portfolio Rebalancing Using Python \- Evgeny Pogorelov, 1월 25, 2026에 액세스, [https://evgenypogorelov.com/portfolio-rebalancing-python.html](https://evgenypogorelov.com/portfolio-rebalancing-python.html)  
52. New Handbook: BI‑as‑Code for Non‑Developers – Streamlit × Claude Code \+ One‑Click Codespace Starter \- Show the Community\!, 1월 25, 2026에 액세스, [https://discuss.streamlit.io/t/new-handbook-bi-as-code-for-non-developers-streamlit-x-claude-code-one-click-codespace-starter/117700](https://discuss.streamlit.io/t/new-handbook-bi-as-code-for-non-developers-streamlit-x-claude-code-one-click-codespace-starter/117700)  
53. Understanding Vibe Coding and Its Implications | Black Duck Blog, 1월 25, 2026에 액세스, [https://www.blackduck.com/blog/vibe-coding-and-its-implications.html](https://www.blackduck.com/blog/vibe-coding-and-its-implications.html)  
54. Agentic AI Prompting: Best Practices for Smarter Vibe Coding \- Ran The Builder, 1월 25, 2026에 액세스, [https://www.ranthebuilder.cloud/post/agentic-ai-prompting-best-practices-for-smarter-vibe-coding](https://www.ranthebuilder.cloud/post/agentic-ai-prompting-best-practices-for-smarter-vibe-coding)  
55. Effective Agentic Coding Practices \- Builder Society, 1월 25, 2026에 액세스, [https://www.buildersociety.com/threads/effective-agentic-coding-practices.7796/](https://www.buildersociety.com/threads/effective-agentic-coding-practices.7796/)  
56. Claude Code on the web, 1월 25, 2026에 액세스, [https://code.claude.com/docs/en/claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web)  
57. Asset Management | Bloomberg Professional Services, 1월 25, 2026에 액세스, [https://www.bloomberg.com/professional/solutions/asset-management/](https://www.bloomberg.com/professional/solutions/asset-management/)  
58. Asset management \- a comprehensive guide, 1월 25, 2026에 액세스, [https://iongroup.com/blog/markets/asset-management-a-comprehensive-guide/](https://iongroup.com/blog/markets/asset-management-a-comprehensive-guide/)  
59. MCP-Agent: How to Build Scalable Deep Research Agents \- AI Alliance, 1월 25, 2026에 액세스, [https://thealliance.ai/blog/building-a-deep-research-agent-using-mcp-agent](https://thealliance.ai/blog/building-a-deep-research-agent-using-mcp-agent)  
60. A Multi-Agent Framework for Quantitative Finance : An Application to Portfolio Management Analytics \- ACL Anthology, 1월 25, 2026에 액세스, [https://aclanthology.org/2025.emnlp-industry.55.pdf](https://aclanthology.org/2025.emnlp-industry.55.pdf)  
61. Show HN: Multi-agent AI stock analyzer – 408% return trading Korean market \- All | Search powered by Algolia, 1월 25, 2026에 액세스, [https://hn.algolia.com/?query=Show%20HN%3A%20Multi-agent%20AI%20stock%20analyzer%20%E2%80%93%20408%25%20return%20trading%20Korean%20market\&type=story\&dateRange=all\&sort=byDate\&storyText=false\&prefix\&page=0](https://hn.algolia.com/?query=Show+HN:+Multi-agent+AI+stock+analyzer+%E2%80%93+408%25+return+trading+Korean+market&type=story&dateRange=all&sort=byDate&storyText=false&prefix&page=0)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAZCAYAAAA14t7uAAABQElEQVR4Xu2UvUpDQRCFj6CiIIhYGEGwtk6b0lY7QfABLGJqa18hYBMikiogYqXY+QIWWigKVorY2UhsFH/OOHPJMAZzc9cyH3yw9+xP9s7dLDBkSD8W6RP9cj4417pDi/EIXXTDZSP0xvIxlw+ETD6nMyGft77DkOdiDr93m1FBwsKb0Mlxt8IVtG8yduThGjo5coSERYV3+kkb5h7t0DdojQsxCt1VPeRnlsvJKET2cZZCPmv5SshzI1+7V32Xkbiw1Pc5huQEunDZZVK2XdqmNVqlF3TajflhAjq5GTvQPSkL9iw/vkW3oeNXLZc3alkb49BJUdlRRsmyW3oPvVMyXuiUtffRe2N/InW+pDsh999E3mzdPRdG/p2v1pY3/HB9Sch9ckqP6R0SzrlHdis3YDzzSch9cQCt77/UNDffVmlLtH1tAd8AAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAABN0lEQVR4Xu2UQStFURSFl/LKTEq9lIFMpEzNzJ6BiRKTV8yVoUiZyD+QySvxB+QPmJmbGJoo6ZWBgZIMKKzdPruO1b3pdi+j99Wqd9fa7XfPOftcYMCAppmiHqivJPsdek/ebhTX4YN6UZPMwf+kq0EVhuFNjjUgE/DsSvxKLMCbzGpA9tDACi7gTZQW3L/UoCq2/5/USdIZ9Qo/ZNui2thbPsGb31H95G3kRSWsUY/UkAbBOLzZqvgxPTPi54xS1/ilbhteMCb+ZPLXxc/ZpPbVVO5RfMAxPTZhRaxQt/C6jmQ/sCa2TMXOwrLp9HyQZcEbNaJmYAdqb2BNntOzXbjgKGXz8L0+z7KgaOWVWKRuqEMNSBs+bX/GMnWqZpPY7S8bgFpsUUvwL2/p5aqDfT52qJ4G/8Y3muJFBQ25lOEAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAZCAYAAADTyxWqAAAA7ElEQVR4XmNgGAWjYBTQADAC8Ucg/o8DX0QoJQwqGSCaZgJxHxA/hPJDgTgEiCURSvEDcwaIRlY0cZCYC5oYQfATiKegCzJADPNFF8QHuBkgmpTQxEWg4tJo4ngBLwNEEygCYIAFiOcA8WskMRAoBuJ2IP4LxCeA2AaIr6CoAIJ/QKyIxL/FgD0MZwFxEVQOBr4CMQ8SH+5VGNZClkQDd4H4ARIfpB6kHwWATAclAQ50CTTwG4i3QtkgtciuJAmAwhI5hsuBuAwhTRoABTgo4A8A8RYgjkSRJRGsYSAjEWMDDgyQWE9ggOQY2gIAPNwyC5jQjTIAAAAASUVORK5CYII=>