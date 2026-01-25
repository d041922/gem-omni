# **클로드 코드 및 MCP 기반의 지능형 자산 관리 시스템: 기술-방법론-UI/UX 통합 아키텍처**

## **1\. 시스템 철학: '인간 중심의 지능형 통제소'**

본 시스템은 AI에게 전권을 위임하는 '블랙박스' 자동매매가 아닌, AI가 도출한 \*\*'수치적 근거(Evidence)'\*\*를 인간이 검토하고 승인하는 **Human-in-the-loop 통제소** 모델을 지향한다. 이는 AI의 환각 리스크를 제어하고 투자자의 철학을 시스템에 이식하기 위함이다.

## **2\. 클로드 코드(Claude Code)의 에이전틱 아키텍처 및 최신 기능**

클로드 CLI의 최신 기능을 활용하여 개발 효율성을 높이고 복잡한 분석 업무를 분산 처리한다.

### **2.1 하위 에이전트(Sub-agents) 및 오케스트레이션**

* **분산 작업 처리**: /cowork 명령을 통해 여러 하위 에이전트(Explore, Plan, Bash 등)를 동시에 생성하여 병렬로 작업을 수행한다.1  
* **비동기 실행**: 사용자가 계획을 승인하면 클라이언트 터미널을 점유하지 않고 클라우드 환경에서 자율적으로 작업을 완료한 뒤 결과만 요약 보고받을 수 있다.4  
* **사용자 정의 에이전트**: \~/.claude/agents/ 디렉토리에 마크다운 형식의 시스템 프롬프트를 정의하여 '퀀트 분석가', '거시 경제 전문가' 등 전문 하위 에이전트를 생성한다.6

### **2.2 에이전트 스킬(Skills) 및 훅(Hooks)**

* **전문 지식 모듈화**: 스킬은 SKILL.md를 포함한 디렉토리 구조로, procedural knowledge를 패키징한다. ultrathink 키워드를 포함하면 모델이 더 깊은 추론 과정을 거치도록 유도할 수 있다.8  
* **자동화 훅**: SessionStart, SubagentStop 등의 라이프사이클 이벤트에 스크립트를 연결하여, 세션 시작 시 최신 시장 데이터를 자동으로 로딩하거나 분석 종료 후 보고서를 PDF로 생성하는 과정을 자동화한다.2

## **3\. 전문가 수준의 투자 의사결정 프로세스 (5단계 플로우)**

바이브 코딩의 불확실성을 배제하기 위해 실제 자산운용사의 표준 워크플로우를 시스템에 강제한다.

| 단계 | 주요 작업 (Task) | 활용 지표 및 데이터 |
| :---- | :---- | :---- |
| **1\. Snapshot** | 시장 환경 진단 | VIX 지수, 연준 금리(Fed Rate), 환율, 원자재 가격 14 |
| **2\. Screening** | 알파 팩터 필터링 | ROE, P/E, EPS 성장률, 기관 수급 동향, 모멘텀 지수 16 |
| **3\. Research** | 심층 분석 (Grounding) | DART 공시, 수익 보고서, **NotebookLM** 기반 비정형 데이터 분석 18 |
| **4\. Risk Audit** | 리스크 시뮬레이션 | 샤프 지수 최적화, MDD(최대 낙폭) 계산, 섹터 집중도 체크 20 |
| **5\. Execution** | 최종 승인 및 주문 | Alpaca API 연동, 슬리피지 및 거래세 반영 주문 실행 |

#### **자산 배분 최적화 (Sharpe Ratio)**

에이전트는 다음 수식을 극대화하는 방향으로 포트폴리오 비중을 조절하도록 설계된다.

![][image1]  
(![][image2]: 포트폴리오 수익률, ![][image3]: 무위험 수익률, ![][image4]: 포트폴리오 표준편차)

## **4\. 데이터 생태계: MCP 및 리서치 파이프라인**

모델 컨텍스트 프로토콜(MCP)은 외부 데이터와 AI 에이전트 사이의 표준화된 통로 역할을 수행한다.

* **주요 금융 MCP 서버**:  
  * **Alpha Vantage**: 글로벌 주식 시세 및 기술적 지표.  
  * **jjlabsio/korea-stock-mcp**: DART 공시 및 한국 거래소(KRX) 데이터.19  
  * **Alpaca**: 실제 매매 실행 및 계좌 관리.  
* **NotebookLM 통합**: 개인 리서치 노트를 NotebookLM에 업로드하고 클로드 코드가 이를 조회하게 함으로써, 출처가 명확한(Source-grounded) 리포트를 생성하고 환각을 방지한다.

## **5\. 시스템 안정화 및 자가 피드백 메커니즘**

### **5.1 룰 기반 안정화 (CLAUDE.md & .cursorrules)**

* **공통 규칙 (\~/.claude/CLAUDE.md)**: 개인 투자 철학(예: "손절 라인 \-10% 엄수") 및 코딩 컨벤션을 정의한다.2  
* **경계 관리 (.cursorrules)**: 특정 모듈(예: 주문 처리)에 대한 에이전트의 수정 권한을 제한하거나, 수정 전 반드시 테스트 코드를 통과하도록 강제한다.

### **5.2 다중 에이전트 토론 (Multi-Agent Debate, MAD)**

단일 AI의 확증 편향을 깨기 위해 서로 다른 페르소나를 가진 에이전트들이 논쟁하는 프로세스를 도입한다.

* **Bull vs Bear**: "강세론자"와 "약세론자" 에이전트가 각자의 데이터 근거를 가지고 2회 이상 반박 토론을 거친다.6  
* **감사자(Auditor)**: 두 주장 사이의 논리적 모순을 지적하고 최종 투자 매력도 점수를 산출한다.16

### **5.3 자가 피드백 루프 (Self-Reflection)**

작업 완료 전 에이전트 스스로 실수를 검토하게 하는 'MIRROR' 프레임워크 패턴을 적용한다.

* **검증 프롬프트**: "방금 제안한 포트폴리오 리밸런싱에 거래세와 슬리피지가 반영되었는가? 리스크 한도를 넘지 않았는가?" 10

## **6\. UI/UX 및 대시보드 설계 (Streamlit)**

스트림릿은 에이전트의 사고 과정을 투명하게 보여주는 인터페이스로 활용된다.

* **L1. Market Snapshot**: 실시간 거시 지표 및 섹터 맵 시각화.  
* **L2. Agent Intelligence**: 에이전트의 **실시간 사고 로그** 스트리밍(st.status) 및 MAD 토론 내용 표시.26  
* **L3. Execution Desk**: 에이전트가 제안한 주문 리스트를 수정 가능한 표(st.data\_editor)로 노출하고 인간이 최종 승인.27

## **7\. 토큰 사용량 및 비용 최적화 (Efficiency Engineering)**

고빈도 시장 데이터 처리를 위해 토큰 소모를 극적으로 줄이는 기술을 적용한다.

* **프롬프트 캐싱 (Prompt Caching)**: 도구 정의 및 투자 지침 등 정적 컨텍스트를 캐싱하여 **비용 90%, 지연 시간 85%를 절감**한다.  
* **자동 지연 로딩 (Tool Search Tool)**: MCP 도구가 많아질 경우 실제 필요한 도구만 검색하여 로드함으로써 컨텍스트 오버헤드를 85% 줄인다.  
* **파일 기반 스킬 처리**: 대규모 데이터를 에이전트 컨텍스트에 직접 넣지 않고 로컬 임시 파일(/tmp/)에 저장한 뒤, 전문 스킬이 요약본(\~500 토큰)만 반환하도록 설계한다.26

## **8\. 실전 사례: PRISM-INSIGHT**

한국 시장을 타겟으로 한 **PRISM-INSIGHT**는 13개의 전문 에이전트가 협업하여 가상 수익률 408%를 달성한 대표적 사례이다.28 이 시스템은 급등주 탐지부터 분석 리포트 생성, 자동 시뮬레이션까지 전 과정을 대시보드로 투명하게 공개하여 에이전틱 금융의 가능성을 입증하였다.29

---

본 보고서에서 제시한 통합 아키텍처는 클로드의 강력한 추론력과 MCP의 확장성, 그리고 엄격한 엔지니어링 룰을 결합하여, 바이브 코딩의 불확실성을 걷어내고 지속 가능한 투자 성과를 창출하는 강력한 개인 자산 관리 파트너가 될 것이다.22

#### **참고 자료**

1. Claude Code 2.1 NEW Update IS HUGE\! Sub Agents /skills, Claude Canvas, LSPs, & MORE\!, 1월 25, 2026에 액세스, [https://www.youtube.com/watch?v=s0JCE3WCL3s](https://www.youtube.com/watch?v=s0JCE3WCL3s)  
2. How to Use Claude Code: A Guide to Slash Commands, Agents ..., 1월 25, 2026에 액세스, [https://www.producttalk.org/how-to-use-claude-code-features/](https://www.producttalk.org/how-to-use-claude-code-features/)  
3. Trade Strategy and Execution | CFA Institute, 1월 25, 2026에 액세스, [https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/trade-strategy-execution](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/trade-strategy-execution)  
4. Getting Started with Cowork | Claude Help Center, 1월 25, 2026에 액세스, [https://support.claude.com/en/articles/13345190-getting-started-with-cowork](https://support.claude.com/en/articles/13345190-getting-started-with-cowork)  
5. Claude just introduced Cowork: the Claude code for non-dev stuff : r/ClaudeAI \- Reddit, 1월 25, 2026에 액세스, [https://www.reddit.com/r/ClaudeAI/comments/1qb6gdx/claude\_just\_introduced\_cowork\_the\_claude\_code\_for/](https://www.reddit.com/r/ClaudeAI/comments/1qb6gdx/claude_just_introduced_cowork_the_claude_code_for/)  
6. Create custom subagents \- Claude Code Docs, 1월 25, 2026에 액세스, [https://code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)  
7. Can someone tell me what's going on here? Iykyk and I want to know. Please...coworking, subagent migration, claude cli vs claude code desktop cli thingy : r/ClaudeAI \- Reddit, 1월 25, 2026에 액세스, [https://www.reddit.com/r/ClaudeAI/comments/1qijif2/can\_someone\_tell\_me\_whats\_going\_on\_here\_iykyk\_and/](https://www.reddit.com/r/ClaudeAI/comments/1qijif2/can_someone_tell_me_whats_going_on_here_iykyk_and/)  
8. Agent Skills \- Claude API Docs \- Claude Console, 1월 25, 2026에 액세스, [https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)  
9. Extend Claude with skills \- Claude Code Docs, 1월 25, 2026에 액세스, [https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)  
10. AI for Finance | Google Workspace, 1월 25, 2026에 액세스, [https://workspace.google.com/solutions/ai/finance/](https://workspace.google.com/solutions/ai/finance/)  
11. Tired of Spending 2 Hours Daily on Stock Market Research? Use This Agentic AI System Instead \- DataDrivenInvestor, 1월 25, 2026에 액세스, [https://medium.datadriveninvestor.com/tired-of-spending-2-hours-daily-on-stock-market-research-use-this-agentic-ai-system-instead-d53bbc54075f](https://medium.datadriveninvestor.com/tired-of-spending-2-hours-daily-on-stock-market-research-use-this-agentic-ai-system-instead-d53bbc54075f)  
12. Use case: Analyze financial statements and calculate ratios | Gemini Enterprise, 1월 25, 2026에 액세스, [https://docs.cloud.google.com/gemini/enterprise/docs/use-case-analyze-financial-statements](https://docs.cloud.google.com/gemini/enterprise/docs/use-case-analyze-financial-statements)  
13. Finance MCP Server \- LobeHub, 1월 25, 2026에 액세스, [https://lobehub.com/mcp/akshatbindal-finance-mcp-server](https://lobehub.com/mcp/akshatbindal-finance-mcp-server)  
14. Best MCP servers for stock market data and algorithmic trading \- Medium, 1월 25, 2026에 액세스, [https://medium.com/data-science-collective/best-mcp-servers-for-stock-market-data-and-algorithmic-trading-ca51e89cd0a1](https://medium.com/data-science-collective/best-mcp-servers-for-stock-market-data-and-algorithmic-trading-ca51e89cd0a1)  
15. The Four Stages of the Stock Market Cycle | Charles Schwab, 1월 25, 2026에 액세스, [https://www.schwab.com/learn/story/four-stages-stock-market-cycles](https://www.schwab.com/learn/story/four-stages-stock-market-cycles)  
16. From Deep Learning to LLMs: A survey of AI in Quantitative Investment \- arXiv, 1월 25, 2026에 액세스, [https://arxiv.org/html/2503.21422v1](https://arxiv.org/html/2503.21422v1)  
17. Automate Strategy Finding with LLM in Quant Investment \- ACL Anthology, 1월 25, 2026에 액세스, [https://aclanthology.org/2025.findings-emnlp.1005.pdf](https://aclanthology.org/2025.findings-emnlp.1005.pdf)  
18. The CLI Tool That Unlocks Google NotebookLM | by Ewan Mak | Jan, 2026 | Medium, 1월 25, 2026에 액세스, [https://medium.com/@tentenco/notebooklm-py-the-cli-tool-that-unlocks-google-notebooklm-1de7106fd7ca](https://medium.com/@tentenco/notebooklm-py-the-cli-tool-that-unlocks-google-notebooklm-1de7106fd7ca)  
19. AI, Meet the Korean Stock Market: A Deep Dive into the jjlabsio DART & KRX MCP Server, 1월 25, 2026에 액세스, [https://skywork.ai/skypage/en/ai-korean-stock-market-dive/1979045039327977472](https://skywork.ai/skypage/en/ai-korean-stock-market-dive/1979045039327977472)  
20. Asset Allocation Software \- Informa Connect, 1월 25, 2026에 액세스, [https://informaconnect.com/zephyr/asset-allocation/](https://informaconnect.com/zephyr/asset-allocation/)  
21. Manager Evaluation & Due Diligence \- Venn by Two Sigma, 1월 25, 2026에 액세스, [https://www.venn.twosigma.com/resources/manager-evaluation-due-diligence](https://www.venn.twosigma.com/resources/manager-evaluation-due-diligence)  
22. Building a Multi-Agent AI System for Financial Market Analysis \- Analytics Vidhya, 1월 25, 2026에 액세스, [https://www.analyticsvidhya.com/blog/2025/02/financial-market-analysis-ai-agent/](https://www.analyticsvidhya.com/blog/2025/02/financial-market-analysis-ai-agent/)  
23. A Multi-Agent Framework for Quantitative Finance : An Application to Portfolio Management Analytics \- ACL Anthology, 1월 25, 2026에 액세스, [https://aclanthology.org/2025.emnlp-industry.55.pdf](https://aclanthology.org/2025.emnlp-industry.55.pdf)  
24. Yahoo Finance | Awesome MCP Servers, 1월 25, 2026에 액세스, [https://mcpservers.org/servers/a05031113/yahoo-fianace-mcp](https://mcpservers.org/servers/a05031113/yahoo-fianace-mcp)  
25. Effective Agentic Coding Practices \- Builder Society, 1월 25, 2026에 액세스, [https://www.buildersociety.com/threads/effective-agentic-coding-practices.7796/](https://www.buildersociety.com/threads/effective-agentic-coding-practices.7796/)  
26. How to build a ClickHouse-backed AI Agent with Streamlit ..., 1월 25, 2026에 액세스, [https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/streamlit-agent](https://clickhouse.com/docs/use-cases/AI/MCP/ai-agent-libraries/streamlit-agent)  
27. Customer support agent \- Claude API Docs, 1월 25, 2026에 액세스, [https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat](https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat)  
28. Show HN: Multi-agent AI stock analyzer – 408% return trading Korean market \- All | Search powered by Algolia, 1월 25, 2026에 액세스, [https://hn.algolia.com/?query=Show%20HN%3A%20Multi-agent%20AI%20stock%20analyzer%20%E2%80%93%20408%25%20return%20trading%20Korean%20market\&type=story\&dateRange=all\&sort=byDate\&storyText=false\&prefix\&page=0](https://hn.algolia.com/?query=Show+HN:+Multi-agent+AI+stock+analyzer+%E2%80%93+408%25+return+trading+Korean+market&type=story&dateRange=all&sort=byDate&storyText=false&prefix&page=0)  
29. Popular MCP Servers \- Glama, 1월 25, 2026에 액세스, [https://glama.ai/mcp/servers](https://glama.ai/mcp/servers)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAaCAYAAACzdqxAAAABYUlEQVR4Xu2UsSuFYRTGH6EoixRZ72A1WI0MFhMZmOzXIim7f8CiUDJIshjIYLmj8g9YDKRsBmWw4Hmc773Od1x99/soy/3VU7dz3ve9533ecz6gQ4d/Y4Y6oG6oe+qU2nEao7qaqyuwRb3HINmHxbepnpArZIBqoPXB67D4LTUScoXUqEfqOSbIIezga2ow5AqZxdfmyAMstxoT7bAJ27wX4r1ZXP7qdymSDa+wa6sTzmAHXrp1pfE2eA+XsnjpShM/2TBBvVCjId4Wvs0W8ylMUW+oeLBvs/GQSzeJvXtBXVHLsCnVe3yzaxe2+YTqc3H9Ps9yulU/dUxNw25yBytK6EYaok9UnarURq+jtIBMwjyuw/xfg30zNmB/mgrROn1vSjFEzcEesjuL6VDZlFC10a5KaBLTQw+j9bRW4gk2OCuwh1zIp6shX70Nf4L81rg3qPl86neoI/SAqtq3ZpMPD2RMO/RwyxEAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAZCAYAAAArK+5dAAABfUlEQVR4Xu2VPyhFURzHf4pSCBG9MJBFKYNsBoPFYnpKUQaDzSZlsBmVZCHCpGQ0Kq+MBgaTUhiYLIqi/Pl+3+/e806/+266717b+9Sn997vd9457/zu75wnUqVK1gzAbXgNH4PXPbgTOA/b3OgK6IJ5uAy/4Wrwma7AB/gJF8MvVMoEvBdd0KcfPsEfE0/MGjyBtSbeBC8k5QJ98BmO2gSYFZ38wyaSMCk6SbuJswHuRJ/BlMklguXhAj0wB8fgNHyHx7DbjYxSDzthnU2ENMKC6AJha7JN2T1zsMaNjDIEz+EpPDI5B8vwAt9MvBl+iZYvji24Cc/ghsk5dkV//b6Jc+uMH5q4D3c5YoM+rfBSdKIZk2NnMc7DZmmBB6L5q+A9YxGGRUvzKlpPn3HRCXjCCc9HQyldpCD6DGNZEp3kRqKdYhcYhB2ldPHhs7ypYAOE9xKvDB+WsNzBzAzukIv8GwvyR/3Tkrr+5eiFt6Kndt3kMoNl4T9c7BXyC2C9RREpD2tMAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAZCAYAAADTyxWqAAABGElEQVR4XmNgGAWjYBTQADADsRMQHwbid0D8Hw0/BWI1uGoCYD4DRBPIoCdA/BeIfwHxIyheCMT8cNV4ACsQfwViPyBmhIopAPEJBiINQAYxQJyDLggEz4FYCV0QH9AH4k9AzIImLg3Ep4FYEE0cL/BlgIQVOgB5uQFNDOTlq0BcBcQzgHgxEJ9EVmAKxN+QBYCAB4h3AbEMmngIA8SgW0AsDxUrB2IOmAKQxgMMkEgAARDdAMQPoHxk4ALEW4G4FUkMZJgkEh8MhKGCcFtwgIcMiEgBhesDhBTpADlSMoB4N5IcSQDk6otAPB2ImxkgESCBooIEAIoQTwZIOAugyZEEQEnlBhBPAmJxNDmSASxR8zIgshwKAAA5Lyxab0qPFwAAAABJRU5ErkJggg==>