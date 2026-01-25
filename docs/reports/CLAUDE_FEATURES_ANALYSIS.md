# 클로드 CLI 기능 활용 분석 및 개선 방안

## 작성일: 2026-01-25

---

## 📊 현재 클로드 기능 활용 현황

### ✅ 활용 중인 기능

#### 1. Custom Skills (잘 활용 중)
**위치**: `skills/` 디렉토리

**현재 구현된 Skills (10개):**
1. `stock_analyzer.py` - 종목 분석 (13KB, 핵심)
2. `technical_indicators.py` - 기술적 지표 계산 (7KB)
3. `sentiment_analyzer.py` - 뉴스 감성 분석 (5KB)
4. `finance_core_lib.py` - 재무 계산 라이브러리 (9KB)
5. `gsheet_loader.py` - Google Sheets 연동
6. `finance_tools.py` - 재무 도구
7. `chart_tools.py` - 차트 생성
8. `kis_tools.py` - 한국투자증권 API (미래 확장)
9. `quant_engine.py` - 퀀트 엔진
10. `rule_manager.py` - 규칙 관리

**평가**: ⭐⭐⭐⭐⭐ (5/5)
- 자체 개발한 Skills가 매우 잘 구조화됨
- 금융 도메인 특화 기능 충실

#### 2. Prompt Caching (효율적 활용)
**위치**: `.claude/prompts/`

**현재 프롬프트:**
1. `investment-analyst.md` - 포트폴리오 분석 프롬프트
2. `stock-analyst.md` - 종목 분석 프롬프트

**평가**: ⭐⭐⭐⭐⭐ (5/5)
- 토큰 절감 85-90% 달성
- 파일 기반 캐싱으로 효율적

#### 3. Hooks (안전장치)
**위치**: `.claude/hooks.yml`

**현재 Hooks:**
1. `PreToolUse` - main.py 수정 경고
2. `PostToolUse` - Python 문법 체크
3. `UserPromptSubmit` - 위험 명령 감지

**평가**: ⭐⭐⭐⭐ (4/5)
- 안전장치로 좋지만, 더 활용 가능

#### 4. CrewAI Framework (핵심)
**위치**: `agents/crewai_agents/`, `agents/crews/`

**구성:**
- 5개 전문 에이전트 (Fundamental, Sentiment, Valuation, Risk Control, Moderator)
- 멀티에이전트 협업 시스템
- Task 기반 워크플로우

**평가**: ⭐⭐⭐⭐⭐ (5/5)
- 최적의 프레임워크 선택
- 잘 구조화된 에이전트 시스템

---

### ❌ 미활용 또는 부분 활용 기능

#### 1. .claude/agents/ (정의만 있고 미사용)
**위치**: `.claude/agents/`

**현재 파일:**
1. `analyst-agent.md`
2. `data-sync-agent.md`
3. `risk-agent.md`
4. `strategy-agent.md`

**문제점:**
- 정의되어 있지만 실제 사용되지 않음
- CrewAI 에이전트와 중복

**개선 방안:**
- 삭제하거나 CrewAI 에이전트 문서화로 활용
- 또는 커스텀 명령어의 기반으로 활용

**우선순위**: 🟡 중간 (정리 필요)

#### 2. MCP (Model Context Protocol) Servers
**현재 상태**: 미사용

**활용 가능한 MCP Servers:**

##### A. Google Sheets MCP (추천 ⭐⭐⭐⭐⭐)
- **현재**: `skills/gsheet_loader.py`로 직접 구현
- **개선**: MCP Server로 전환 시 장점
  - 더 안정적인 연결
  - 실시간 업데이트 가능
  - 클로드가 직접 Sheets 읽기/쓰기
- **비용**: 무료
- **우선순위**: 🟢 높음

##### B. Finance Data MCP (조사 필요 ⭐⭐⭐)
- **현재**: yfinance 직접 호출
- **개선**: 금융 데이터 MCP 서버 찾기
  - Yahoo Finance MCP
  - Alpha Vantage MCP
  - IEX Cloud MCP
- **비용**: 무료 티어 확인 필요
- **우선순위**: 🟡 중간

##### C. Web Search MCP (선택적 ⭐⭐)
- **현재**: 뉴스는 yfinance에서 가져옴
- **개선**: 더 넓은 뉴스 소스
  - Google Search MCP
  - Brave Search MCP
- **비용**: API 키 필요 (제한적)
- **우선순위**: 🔵 낮음 (현재 방식 충분)

##### D. Database MCP (미래 ⭐)
- **현재**: Google Sheets로 충분
- **미래**: 포트폴리오 히스토리 저장
  - SQLite MCP
  - PostgreSQL MCP
- **우선순위**: 🔵 낮음 (장기)

#### 3. Custom Commands (미구현)
**현재 상태**: 없음

**추가 가능한 Commands:**

##### 🌅 `/morning-brief` (강력 추천 ⭐⭐⭐⭐⭐)
**기능:**
```
1. 전일 미국 시장 마감 (S&P 500, NASDAQ)
2. 한국 시장 개장 전 시황
3. 포트폴리오 보유 종목 중 주요 뉴스
4. 오늘의 투자 포인트
5. 주의할 리스크
```

**구현 방법:**
- `.claude/commands/morning-brief.md` 생성
- Google Sheets에서 포트폴리오 로드
- yfinance로 시장 데이터
- Gemini로 브리핑 생성

**예상 소요**: 2시간
**우선순위**: 🟢 매우 높음 (사용자 요청)

##### 🌙 `/evening-brief` (추천 ⭐⭐⭐⭐)
**기능:**
```
1. 오늘 미국 시장 결과
2. 포트폴리오 손익 변화
3. 보유 종목 주요 이슈
4. 내일 대응 전략
```

**우선순위**: 🟢 높음

##### 📊 `/portfolio-check` (추천 ⭐⭐⭐⭐)
**기능:**
```
1. 현재 포트폴리오 상태
2. 집중도 리스크 경고
3. 리밸런싱 필요 여부
4. AI 추천 액션
```

**우선순위**: 🟢 높음

##### 📈 `/stock-deep-dive <ticker>` (추천 ⭐⭐⭐)
**기능:**
```
1. 종목 심층 분석 (멀티에이전트 자동)
2. 경쟁사 비교
3. 섹터 전망
4. 투자 의견서 생성
```

**우선순위**: 🟡 중간

##### 🔔 `/set-alert <ticker> <condition>` (선택적 ⭐⭐)
**기능:**
```
특정 조건 발생 시 알림
예: /set-alert PLTR price>150
```

**우선순위**: 🔵 낮음 (복잡)

#### 4. CrewAI Tools (패키지에 있지만 미사용)
**현재 상태**: 설치되어 있지만 활용 안 함

**활용 가능한 CrewAI Tools:**

##### A. `FileSearchTool` (추천 ⭐⭐⭐)
- 포트폴리오 히스토리 검색
- 과거 분석 리포트 검색

##### B. `CSVSearchTool` (추천 ⭐⭐⭐⭐)
- Google Sheets 대신 로컬 CSV 사용 가능
- 백테스팅 데이터 분석

##### C. `WebsiteSearchTool` (선택적 ⭐⭐)
- 기업 IR 페이지 크롤링
- 경쟁사 분석

##### D. `CodeInterpreterTool` (미래 ⭐)
- 퀀트 전략 백테스팅
- 복잡한 계산

**우선순위**: 🟡 중간 (필요시 추가)

#### 5. Memory System (있지만 활용 낮음)
**위치**: `core/memory.py`

**현재 상태:**
- 파일은 존재하지만 활용도 낮음
- User Profile 저장 기능은 있지만 개인화 반영 부족

**개선 방안:**
- User Profile 강화 (투자 목표, 위험 성향, 투자 기간)
- AI 분석 시 개인화 정보 반영
- 학습 및 피드백 저장

**우선순위**: 🟢 높음 (사용자 요청)

---

## 🎯 우선순위별 개선 계획

### 🟢 높은 우선순위 (즉시 시작)

#### 1. Custom Commands 추가 (2-3시간)
- `/morning-brief` - 아침 브리핑 ⭐⭐⭐⭐⭐
- `/evening-brief` - 저녁 브리핑 ⭐⭐⭐⭐
- `/portfolio-check` - 포트폴리오 점검 ⭐⭐⭐⭐

**구현 방법:**
```bash
.claude/
  commands/
    morning-brief.md      # 아침 브리핑 명령어
    evening-brief.md      # 저녁 브리핑 명령어
    portfolio-check.md    # 포트폴리오 점검
```

**예상 소요**: 2-3시간
**효과**: 사용자 경험 대폭 향상, 일상적 사용 촉진

#### 2. Memory System 개인화 강화 (2시간)
- `core/memory.py` 확장
- User Profile 강화:
  ```python
  {
    "investment_goal": "은퇴 자금 마련",
    "risk_tolerance": "중간",  # 보수적/중간/공격적
    "investment_horizon": "10년",  # 단기/중기/장기
    "preferred_strategy": "가치 투자",  # 가치/성장/배당/퀀트
    "max_single_position": 10,  # %
    "max_sector_concentration": 30,  # %
    "rebalancing_threshold": 5  # %
  }
  ```

**구현:**
1. `pages/settings.py` - 개인화 설정 UI
2. AI 프롬프트에 개인화 정보 포함
3. Risk Agent가 개인 기준으로 경고

**예상 소요**: 2시간
**효과**: AI 분석이 사용자 맞춤형으로 변경

#### 3. Google Sheets MCP 전환 검토 (1-2시간)
- 기존 `skills/gsheet_loader.py` vs MCP 비교
- MCP 서버 설치 및 테스트
- 장단점 분석 후 결정

**예상 소요**: 1-2시간
**효과**: 더 안정적인 데이터 연동 (선택적)

---

### 🟡 중간 우선순위 (선택적)

#### 1. .claude/agents/ 정리 (30분)
- 미사용 파일 삭제 또는
- CrewAI 에이전트 문서화로 재활용

#### 2. CrewAI Tools 활용 검토 (1시간)
- CSVSearchTool 백테스팅용
- FileSearchTool 히스토리 검색용

#### 3. Finance Data MCP 조사 (1시간)
- Yahoo Finance MCP 찾기
- yfinance vs MCP 비교

---

### 🔵 낮은 우선순위 (장기)

#### 1. Web Search MCP (복잡)
- 현재 yfinance 뉴스로 충분

#### 2. Database MCP (미래)
- 포트폴리오 히스토리 저장

#### 3. Alert System (복잡)
- 실시간 알림 시스템

---

## 💡 공유/상용 도구 활용 조사

### MCP Server Registry 확인
- **공식 MCP Registry**: https://github.com/modelcontextprotocol/servers
- **커뮤니티 MCP**: https://github.com/topics/mcp-server

### 금융 관련 MCP Servers 조사 결과:

#### 1. Google Sheets MCP ✅
- **저장소**: `@modelcontextprotocol/server-google-sheets`
- **설치**: `npm install @modelcontextprotocol/server-google-sheets`
- **비용**: 무료
- **장점**: 공식 지원, 안정적
- **단점**: Node.js 필요

#### 2. Yahoo Finance API Tools (조사 필요)
- 공식 MCP는 없지만 CrewAI Tools 패키지에 있을 수 있음
- yfinance가 이미 무료이고 안정적이므로 굳이 MCP 필요 없음

#### 3. Brave Search MCP ✅
- **저장소**: `@modelcontextprotocol/server-brave-search`
- **비용**: API 키 필요 (무료 티어 제한적)
- **용도**: 뉴스 검색 확장 (선택적)

### CrewAI Tools 활용:
- 이미 설치됨: `crewai_tools` 패키지
- 70개 이상의 도구 사용 가능
- 금융 특화 도구는 없지만 범용 도구 활용 가능

**결론:**
- 금융 도메인 특화 MCP는 거의 없음
- 현재 직접 구현한 방식(yfinance, Google Sheets API)이 더 효율적
- MCP는 Google Sheets만 선택적으로 고려

---

## 📋 즉시 실행 가능한 개선 작업

### Task 1: Custom Commands 구현 (최우선)
**파일:**
1. `.claude/commands/morning-brief.md`
2. `.claude/commands/evening-brief.md`
3. `.claude/commands/portfolio-check.md`

**예상 소요**: 2-3시간
**효과**: ⭐⭐⭐⭐⭐

### Task 2: 개인화 시스템 구축
**파일:**
1. `core/memory.py` 확장
2. `pages/settings.py` 신규 생성
3. AI 프롬프트에 개인화 정보 통합

**예상 소요**: 2시간
**효과**: ⭐⭐⭐⭐⭐

### Task 3: .claude/agents/ 정리
**작업:**
- 미사용 파일 삭제 또는
- CrewAI 에이전트 설명으로 재활용

**예상 소요**: 30분
**효과**: ⭐⭐

---

## 🎉 최종 권장사항

### 즉시 시작 (높은 우선순위):
1. ✅ **Custom Commands 추가** (아침/저녁 브리핑, 포트폴리오 점검)
2. ✅ **개인화 시스템 구축** (투자 목표, 위험 성향 반영)

### 선택적 검토 (중간 우선순위):
3. 🔍 Google Sheets MCP 전환 (현재 방식도 충분하지만 검토)
4. 🔍 CrewAI Tools 활용 (CSVSearchTool, FileSearchTool)

### 장기 계획 (낮은 우선순위):
5. Database MCP (포트폴리오 히스토리)
6. Web Search MCP (뉴스 확장)

---

## 📊 비용 대비 효용성 분석

| 항목 | 추가 비용 | 개발 시간 | 효용성 | 우선순위 |
|:---|:---:|:---:|:---:|:---:|
| Custom Commands | $0 | 2-3시간 | ⭐⭐⭐⭐⭐ | 🟢 최우선 |
| 개인화 시스템 | $0 | 2시간 | ⭐⭐⭐⭐⭐ | 🟢 최우선 |
| Google Sheets MCP | $0 | 1-2시간 | ⭐⭐⭐ | 🟡 선택적 |
| CrewAI Tools | $0 | 1시간 | ⭐⭐⭐ | 🟡 선택적 |
| Finance Data MCP | ? (조사 필요) | 2시간 | ⭐⭐ | 🔵 낮음 |
| Web Search MCP | API 키 필요 | 2시간 | ⭐⭐ | 🔵 낮음 |

**결론**: Custom Commands와 개인화 시스템이 비용 $0에 효용성 최대!

---

**작성일**: 2026-01-25
**상태**: 분석 완료, 구현 대기
**다음**: Custom Commands 및 개인화 시스템 구현
