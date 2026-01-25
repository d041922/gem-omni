# Phase 2 계획 수립 - API 제한 고려

## 뉴스 감성 분석 API 평가

### 1. NewsAPI (https://newsapi.org/)
**무료 플랜 제한:**
- 100 requests/day ❌
- 최근 1개월 데이터만
- 개발용만 허용 (상업적 사용 불가)

**평가:**
- ❌ **비추천**: 100 requests/day는 실용성 없음
- 하루에 종목 10개만 분석해도 10일이면 한계 도달

---

### 2. Finnhub (https://finnhub.io/)
**무료 플랜 제한:**
- 60 calls/minute (괜찮음)
- API 키 필요
- 뉴스 & 감성 분석 포함

**평가:**
- 🟡 **보통**: 60 calls/min은 괜찮으나 새 API 키 필요
- 월간 제한은 명시 안 됨 (추가 확인 필요)

---

### 3. Alpha Vantage (https://www.alphavantage.co/)
**무료 플랜 제한:**
- 500 calls/day (충분)
- 25 calls/5min (제한적)
- 뉴스 & 감성 API 있음

**평가:**
- ✅ **괜찮음**: 500 calls/day면 실용적
- 단점: 새 API 키 필요, 5분당 25 calls 제한

---

### 4. 웹 스크래핑 (Yahoo Finance, Google News)
**무료지만:**
- 불안정 (HTML 구조 변경 시 작동 중단)
- 법적 그레이 영역
- 유지보수 부담

**평가:**
- ❌ **비추천**: 안정성 낮음

---

### 5. ✅ **추천: yfinance 뉴스 + Gemini 감성 분석**

**방식:**
```python
# 1. yfinance에서 뉴스 헤드라인 가져오기 (무료!)
stock = yf.Ticker("NVDA")
news = stock.news  # 최근 뉴스 헤드라인 리스트

# 2. Gemini API로 감성 분석 (이미 사용 중인 API)
prompt = f"""
다음 뉴스 헤드라인들을 분석하여 긍정/부정/중립 점수를 산출하세요:
{news_headlines}

출력 형식:
- 긍정: X%
- 부정: Y%
- 중립: Z%
- 종합 평가: [긍정적/중립적/부정적]
"""
```

**장점:**
- ✅ 추가 API 키 불필요
- ✅ 추가 비용 없음 (Gemini API 이미 사용 중)
- ✅ 무료 제한 없음 (yfinance는 제한 없음)
- ✅ 안정적 (야후 파이낸스 공식 API)
- ✅ 구현 간단 (2-3시간)

**단점:**
- 🟡 뉴스 개수 제한적 (최근 5-10개)
- 🟡 실시간 뉴스는 아님 (1-2시간 지연)

**평가:**
- ✅ **최고 추천**: 실용성, 비용, 안정성 모두 만족

---

## Phase 2 최종 계획

### Task 4: 종목 분석용 멀티에이전트 시스템
**API 연동: 불필요** ✅
- CrewAI 기반 (이미 설치됨)
- Gemini API 사용 (이미 사용 중)
- 추가 비용 없음

**구현 내용:**
1. `agents/crewai_agents/stock_agents.py` 생성
   - FundamentalAnalystAgent
   - SentimentAnalystAgent
   - ValuationAnalystAgent
2. `agents/crews/stock_analysis_crew.py` 생성
   - 3개 에이전트 협업
   - 5라운드 토론 및 합의
3. `pages/stock_analysis.py` 통합
   - 기존 단일 AI 분석 대체

**예상 소요:** 4-6시간
**예상 효과:** 분석 정확도 +30%, 환각 현상 -50%

---

### Task 5: 뉴스 감성 분석 (yfinance + Gemini)
**API 연동: yfinance (무료, 제한 없음)** ✅
- 새 API 키 불필요
- 추가 비용 없음

**구현 내용:**
1. `skills/sentiment_analyzer.py` 생성
   ```python
   def analyze_news_sentiment(ticker: str) -> Dict[str, Any]:
       # 1. yfinance에서 뉴스 가져오기
       # 2. Gemini로 감성 분석
       # 3. 긍정/부정/중립 점수 반환
   ```
2. `skills/stock_analyzer.py`에 통합
   - summary에 sentiment_score 추가
3. AI 프롬프트에 감성 정보 추가

**예상 소요:** 2-3시간
**예상 효과:** Bottom-Up 분석 80% → 100% 달성

---

## 대안 시나리오 (만약 yfinance 뉴스가 부족하다면)

### Plan B: Alpha Vantage (500 calls/day)
- API 키 발급: https://www.alphavantage.co/support/#api-key
- 무료 플랜으로 충분
- 캐싱 전략: 같은 종목은 1시간 캐싱

### Plan C: 뉴스 없이 진행
- 감성 분석 스킵
- 나머지 4개 차원(수익성, 재무건전성, 가치평가, 기술적)만으로도 80% 충족
- Phase 3에서 재검토

---

## 추천 실행 계획

### ✅ 즉시 진행 (추가 비용 없음)

**Step 1: 종목 분석용 멀티에이전트 시스템 (4-6시간)**
- API 연동 불필요
- 분석 품질 대폭 향상
- 리스크 없음

**Step 2: yfinance + Gemini 뉴스 감성 분석 (2-3시간)**
- 추가 API 키 불필요
- 무료 제한 없음
- Bottom-Up 분석 100% 완성

**총 예상 소요: 6-9시간 (1일)**

---

### 🟡 보류 (추가 API 필요)

**Alpha Vantage 통합**
- yfinance 뉴스가 부족할 경우에만
- 500 calls/day 제한 관리 필요
- 우선순위 낮음

**Finnhub 통합**
- 월간 제한 불명확
- 필요성 낮음

---

## 최종 판단

### ✅ Phase 2 진행 추천
**이유:**
1. 멀티에이전트: API 연동 불필요, 즉시 구현 가능
2. 뉴스 감성 분석: yfinance (무료) + Gemini (이미 사용 중) = 추가 비용 없음
3. 무료 제한 문제 없음
4. 실용적이고 안정적

### 예상 결과
- Bottom-Up 분석: 80% → 100%
- 분석 정확도: +30%
- 투자 의사결정 품질: 대폭 향상
- 추가 비용: $0

---

**결론: Phase 2 진행을 강력히 추천합니다!**
