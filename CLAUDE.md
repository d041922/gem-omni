# GEM: OMNI - AI 자산 관리 시스템

## 프로젝트 개요
개인 투자자를 위한 전문가 수준의 AI 기반 포트폴리오 관리 시스템

## 투자 철학 및 원칙

### 1. 데이터 기반 의사결정
- 모든 투자 판단은 정량적 데이터와 정성적 근거를 결합
- 감정이 아닌 수치와 논리에 기반한 분석
- 출처가 명확한 데이터만 사용 (Google Sheets, KIS API, yfinance)

### 2. 리스크 관리 우선
- 수익률보다 손실 방지가 우선
- 포트폴리오 분산을 통한 리스크 최소화
- 단일 종목 비중은 전체의 15%를 초과하지 않음
- 섹터 집중도 모니터링 필수

### 3. 장기적 관점
- 단타보다는 중장기 투자 지향
- 시장 타이밍보다는 자산 배분이 중요
- 정기적 리밸런싱을 통한 포트폴리오 최적화

## 코딩 규칙 및 표준

### 금융 계산
```python
# 모든 금융 계산은 float 정밀도 유지
# 통화 단위: KRW(원화), USD(달러)
# 환율: USD/KRW 기본값 1450원
```

### ⚡ 토큰 최적화 규칙 (필수)
**목표:** API 비용 절감을 위한 토큰 사용량 최소화 (83.7% 달성)

1. **데이터 캐싱 필수**
   - 대용량 데이터는 `tmp/cache/` 디렉토리에 JSON 파일로 저장
   - LLM에는 요약 통계만 전달 (< 500 토큰)
   - 전체 데이터는 파일 경로로 참조

2. **Context 사용 금지**
   - CrewAI Task에서 `context=[...]` 사용 금지
   - 데이터는 파일 경로로 전달
   - 각 에이전트는 `CachedDataLoaderTool`로 필요시 로드

3. **출력 크기 제한**
   - 에이전트 출력: < 500 단어
   - 전체 데이터 반환 금지
   - 핵심 인사이트와 파일 경로만 반환

4. **도구 개발 원칙**
```python
# ❌ Bad: 전체 데이터 반환
return {"data": df.to_dict('records')}  # 5,000 토큰

# ✅ Good: 요약 + 파일 경로
save_portfolio_data(df, "portfolio.json")
return {"summary": {...}, "file_path": "..."}  # 300 토큰
```

### 데이터 소스
1. **Google Sheets**: 포트폴리오 기본 데이터 (종목명, 수량, 매수가)
2. **yfinance**: 실시간 미국 주식 가격
3. **KIS API**: 한국 주식 실시간 시세 (향후 구현)

### 에이전트 워크플로우
```
1. Data Sync Agent: 데이터 로드 및 동기화
2. Analyst Agent: 포트폴리오 메트릭 계산
3. Risk Agent: 리스크 분석 (Beta, 상관계수, Sharpe Ratio)
4. Strategy Agent: AI 기반 투자 전략 생성
```

## AI 분석 가이드라인

### 투자 제안 형식
모든 AI 분석은 **구체적이고 실행 가능한** 액션을 포함해야 함:
- ❌ "분산 투자를 고려하세요" (막연함)
- ✅ "PLTR 30% 익절 (약 ₩500만) 후 반도체 ETF에 재투자" (구체적)

### 필수 포함 요소
1. **종목명과 티커**: 정확한 대상 명시
2. **금액 또는 비율**: 구체적인 수치
3. **조건과 타이밍**: "현재가 $80 돌파시", "이번 주 내" 등
4. **근거**: 왜 이 액션이 필요한지 간단히 설명

## 백테스팅 및 검증

### 실행 전 필수 확인
- 포트폴리오 리밸런싱 스크립트 실행 전 백테스팅 결과 먼저 제시
- 실제 계좌 API 호출 전 반드시 사용자 승인 필요
- 손익 계산 검증: 매수금액 + 손익 = 평가금액

## 파일 구조

```
GEM_OMNI/
├── agents/
│   ├── crewai_agents/    # 4개 전문 에이전트
│   ├── crews/            # FinanceCrew 오케스트레이션 (토큰 최적화)
│   └── tools/
│       ├── data_cache.py         # 🆕 데이터 캐싱 시스템
│       ├── file_loader_tool.py   # 🆕 파일 로더 도구
│       ├── gsheet_tools.py       # ✅ 토큰 최적화 완료
│       ├── portfolio_tools.py    # ✅ 토큰 최적화 완료
│       └── quant_tools.py        # ✅ 토큰 최적화 완료
├── core/                 # 기본 시스템 (Memory, Base)
├── skills/               # 금융 계산 라이브러리
├── tmp/cache/            # 🆕 데이터 캐시 디렉토리 (83.7% 토큰 절감)
├── app.py               # Streamlit UI (메인)
├── CLAUDE.md            # 이 파일
└── OPTIMIZATION_REPORT.md  # 🆕 토큰 최적화 리포트
```

## 향후 확장 계획

### Phase 1 (완료) ✅
- [x] 기본 포트폴리오 계산
- [x] AI 인사이트 생성
- [x] Streamlit 대시보드
- [x] **토큰 최적화 (83.7% 절감)** 🎉

### Phase 2 (진행 중) 🚧
- [x] 리스크 지표 기본 구현 (Beta, Correlation)
- [x] **Data Cache System** (90% 토큰 절감)
- [x] **Context 제거 최적화** (51.7% 추가 절감)
- [ ] Top-Down/Bottom-Up 분석 체계화
- [ ] 자동 리밸런싱 제안
- [ ] Streamlit 프롬프트 최적화 (Step 3)

### Phase 3 (미래) 📋
- [ ] 실시간 알림 시스템
- [ ] 백테스팅 엔진
- [ ] 다중 계좌 통합 관리
- [ ] MCP 서버 통합 (Alpha Vantage, Korea Stock)
- [ ] NotebookLM 연동

## 참고 자료
- **OPTIMIZATION_REPORT.md** - 토큰 최적화 완료 리포트 (필독)
- ref/Claude CLI 기반 자산 관리 에이전트 설계.md
- ref/Claude Code 기반 지능형 자산 관리 시스템 통합 가이드.md
- docs/ARCHITECTURE.md
- docs/CREWAI_GUIDE.md

## 🎯 빠른 시작 가이드

### 토큰 최적화 테스트 실행
```bash
# Step 1: Data Cache 테스트
python test_token_optimization.py

# Step 2: Tools 통합 테스트
python test_tools_integration.py

# Step 3: Context 최적화 테스트
python test_context_optimization.py
```

### 캐시 관리
```python
from agents.tools.data_cache import get_cache_summary, clear_cache

# 캐시 상태 확인
cache_info = get_cache_summary()

# 1시간 이상 된 캐시 삭제
deleted = clear_cache(older_than_hours=1)
```
