# GEM: OMNI - AI 자산 관리 시스템

개인 투자자를 위한 전문가 수준의 AI 기반 포트폴리오 관리 시스템

## 주요 기능

### 📊 포트폴리오 대시보드
- Google Sheets 기반 실시간 포트폴리오 조회
- 자동 메트릭 계산 (수익률, 평가금액, 손익)
- 리스크 지표 분석 (집중도, 변동성, Sharpe Ratio)
- AI 기반 투자 인사이트 생성

### 🔍 개별 종목 분석
- 미국/한국 주식 실시간 분석
- 기술적 지표 (RSI, MACD, MA, 볼린저밴드)
- 펀더멘털 정보 (PER, 시가총액, 베타)
- AI 투자 의견 (매수/보유/매도 + 목표가 + 전략)
- 포트폴리오 보유 종목 자동 인식

### 🤖 Multi-Agent 시스템
- CrewAI 기반 4개 전문 에이전트
  - Data Sync Agent: 데이터 동기화
  - Analyst Agent: 포트폴리오 분석
  - Risk Agent: 리스크 평가
  - Strategy Agent: 투자 전략 수립

## 토큰 최적화

**85-90% 토큰 절감 달성** ✅

- 프롬프트와 데이터 분리 (90% 절감)
- 데이터 캐싱 시스템 (87.7% 절감)
- Context cascade 제거 (51.7% 절감)
- Streamlit 캐싱 (@st.cache_data)

**비용 절감**:
- 분석 1회당: $0.072 → $0.008 (89% 절감)
- 연간 (600회): $43 → $5 ($38 절약)

상세 내용: `docs/reports/FINAL_OPTIMIZATION_REPORT.md`

## 빠른 시작

### 1. 환경 설정
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### 2. API 키 설정
`.env` 파일 생성:
```
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_key  # Optional
```

### 3. 실행
```bash
streamlit run app.py
```

브라우저에서 http://localhost:8501 접속

## 프로젝트 구조

```
GEM_OMNI/
├── app.py                      # 메인 애플리케이션
├── pages/                      # Streamlit 페이지
│   └── stock_analysis.py       # 개별 종목 분석
├── agents/                     # CrewAI 에이전트
│   ├── crewai_agents/          # 에이전트 정의
│   ├── crews/                  # Crew 오케스트레이션
│   └── tools/                  # 에이전트 도구
├── core/                       # 핵심 시스템
│   ├── base.py                 # 기본 클래스
│   ├── memory.py               # 메모리 시스템
│   └── models.py               # 데이터 모델
├── skills/                     # 재사용 가능 라이브러리
│   ├── finance_core_lib.py     # 금융 계산
│   ├── stock_analyzer.py       # 종목 분석
│   └── technical_indicators.py # 기술적 지표
├── .claude/                    # AI 프롬프트 (캐싱용)
│   ├── agents/                 # 에이전트 프롬프트
│   └── prompts/                # 시스템 프롬프트
├── rules/                      # 코딩 규칙
│   ├── 100-python-standard.mdc
│   ├── 300-streamlit-standard.mdc
│   └── 400-token-optimization.mdc
├── tests/                      # 테스트 파일
├── scripts/                    # 유틸리티 스크립트
└── docs/                       # 문서
    ├── guides/                 # 사용 가이드
    ├── reports/                # 분석 리포트
    └── reference/              # 참고 자료
```

## 사용 방법

### 포트폴리오 대시보드
1. 사이드바 → "📊 Portfolio Dashboard"
2. Google Sheets 데이터 자동 로드
3. "🔍 Run AI Analysis" 클릭
4. AI 인사이트 확인

### 개별 종목 분석
1. 사이드바 → "🔍 Stock Analysis"
2. 티커 입력
   - 미국: AAPL, NVDA, MSFT
   - 한국: 005930.KS (삼성전자)
3. "🚀 종목 분석" 클릭
4. 차트 + 지표 확인
5. "🤖 AI 투자 의견 생성" 클릭

## 기술 스택

- **Frontend**: Streamlit, Plotly
- **AI**: Google Gemini 2.0, CrewAI
- **Data**: yfinance, Google Sheets API
- **Language**: Python 3.13

## 문서

- **사용 가이드**: `docs/guides/`
  - ARCHITECTURE.md: 시스템 구조
  - CREWAI_GUIDE.md: 에이전트 사용법
- **분석 리포트**: `docs/reports/`
  - OPTIMIZATION_REPORT.md: 최적화 과정
  - TEST_RESULTS.md: 검증 결과
- **코딩 규칙**: `rules/`
  - 100-python-standard.mdc
  - 400-token-optimization.mdc

## 라이선스

MIT License

## 기여

이슈 및 PR 환영합니다!

---

**최종 업데이트**: 2026-01-25
**버전**: 1.0.0
**상태**: Production Ready ✅
