# GEM: OMNI - 구현 로드맵

## 📌 현재 상태 (2026-01-25)

### ✅ 완료된 작업
- [x] Core/Satellite 분류 로직 개선
- [x] 신규 섹터 추가 (로봇, 전력/에너지)
- [x] 차트 UI 간소화 (3개 탭)
- [x] 개별 종목 분석 페이지
- [x] 포트폴리오 메트릭 계산

### ⏳ 진행 중인 작업
- 없음 (새 로드맵 시작)

---

## 🎯 전체 비전

```
현재 시스템              →      목표 시스템
───────────────────────────────────────────────
정적 프롬프트            →      동적 시장 분석
"AI 추천해"              →      "오늘 RSI 30 이하 10종목"
수동 종목 선택           →      자동 스크리닝
근거 없는 추천           →      리서치 리포트 기반
개별 종목 분석           →      포트폴리오 통합 인사이트
```

---

## 🚀 구현 단계

### Phase 1: 시장 인텔리전스 인프라 (3-4일) ⭐ 최우선
**목표**: 실시간 시장 데이터를 기반으로 의사결정

#### Task #5: Market Screener 개발
**예상 시간**: 1-2일
**산출물**:
```
skills/market_screener.py
├── screen_momentum_stocks()      # RSI + 거래량 기반
├── screen_undervalued_stocks()   # PER/PBR 기반
├── screen_breakout_candidates()  # 52주 신고가 근접
└── get_sector_leaders()          # 섹터 내 상위 종목

tmp/cache/screener_results.json
{
  "momentum": [
    {"ticker": "NVDA", "rsi": 65, "volume_surge": 2.3},
    {"ticker": "AMD", "rsi": 58, "volume_surge": 1.8}
  ],
  "undervalued": [...],
  "breakout": [...]
}
```

**활용 예시**:
```python
# 포트폴리오 분석 시
new_candidates = market_screener.screen_momentum_stocks(
    rsi_range=(30, 70),
    volume_surge=2.0
)
→ AI: "현재 모멘텀 강한 종목 12개 발견. NVDA, AMD는 이미 보유 중."
```

---

#### Task #6: Sector Rotation 분석 엔진
**예상 시간**: 1-2일
**산출물**:
```
skills/sector_analyzer.py
├── analyze_sector_rotation()     # 리딩/래깅 섹터
├── get_sector_momentum()         # 섹터 모멘텀 스코어
├── calculate_relative_strength() # 상대 강도
└── recommend_sector_allocation() # 포트폴리오 제안

tmp/cache/sector_rotation.json
{
  "leading_sectors": [
    {"name": "Technology", "momentum": 8.5, "return_1m": 12.3},
    {"name": "Healthcare", "momentum": 7.2, "return_1m": 8.1}
  ],
  "lagging_sectors": [
    {"name": "Energy", "momentum": 2.1, "return_1m": -3.5}
  ],
  "money_flow": "Tech → Healthcare (유입 중)"
}
```

**활용 예시**:
```python
# 포트폴리오 분석 시
rotation = sector_analyzer.analyze_sector_rotation()
→ AI: "Tech 섹터 과열 신호. Healthcare로 로테이션 권장.
      현재 Tech 비중 45% → 35%로 축소, Healthcare 10% → 20%로 확대"
```

---

#### Task #7: Market Intelligence Hub (대시보드)
**예상 시간**: 1일
**산출물**:
```
app.py - 새 섹션 추가
┌─────────────────────────────────────────┐
│ 🌍 Global Market Pulse (기존)           │
│ S&P 500, NASDAQ, KOSPI, VIX             │
├─────────────────────────────────────────┤
│ 🔥 Market Intelligence (신규)           │
│ ┌─────────────┬─────────────────────┐   │
│ │ 섹터 히트맵  │ 오늘의 스크리닝      │   │
│ │ Tech: 🟢 +3% │ 1. NVDA (RSI 65)    │   │
│ │ Energy: 🔴-2%│ 2. AMD (RSI 58)     │   │
│ │ Healthcare:  │ 3. SMCI (RSI 72)    │   │
│ │ 🟢 +2%       │ [전체 보기 →]       │   │
│ └─────────────┴─────────────────────┘   │
├─────────────────────────────────────────┤
│ 💼 Portfolio Health (기존)              │
│ AI Analysis, Risk Metrics               │
└─────────────────────────────────────────┘
```

**사용자 경험**:
1. 앱 오픈 → 즉시 시장 상황 파악
2. "지금 Tech 섹터 과열, Healthcare 강세"
3. "우리 포트폴리오는 Tech 45% → 조정 필요"

---

### Phase 2: 리서치 지식 기반 구축 (3-4일) ⭐⭐ 고우선순위

#### Task #1: SEC Edgar API 통합
**예상 시간**: 1일
**산출물**:
```
skills/sec_edgar.py
├── fetch_latest_filings(ticker)   # 10-K, 10-Q, 8-K
├── extract_key_metrics()          # 매출, 순이익 등
└── summarize_with_gemini()        # AI 요약

tmp/research/NVDA/
├── 10K_2024Q4.json
│   {
│     "filing_date": "2024-01-15",
│     "revenue": "$22B (+22% YoY)",
│     "key_insights": "데이터센터 부문 +41% 급성장...",
│     "summary": "Gemini 자동 요약..."
│   }
├── 10Q_2024Q3.json
└── earnings_call_2024Q4.txt
```

**활용 예시**:
```python
# 종목 분석 시
filing = sec_edgar.fetch_latest_filings("NVDA")
→ AI: "NVDA 최근 10-K (2024-01-15):
      매출 $22B (+22% YoY), 데이터센터 +41% 성장.
      2025 가이던스: AI 칩 수요 지속 강세 전망."
```

---

#### Task #2: ChromaDB 기반 RAG 시스템
**예상 시간**: 2일
**산출물**:
```
skills/knowledge_base.py
class ResearchKnowledgeBase:
    ├── add_document(ticker, doc_type, content)
    ├── search(ticker, query, top_k=3)
    ├── get_analyst_consensus(ticker)
    └── get_earnings_trend(ticker)

tmp/vectordb/
├── chroma.sqlite3          # 벡터 DB
├── embeddings/             # Google Embeddings
└── index/                  # 인덱스

사용 예시:
kb = ResearchKnowledgeBase()
kb.add_document("NVDA", "10-K", filing_text)
results = kb.search("NVDA", "2025년 전망은?")
→ [
    "2025 가이던스: AI 칩 수요 지속 강세 (10-K p.45)",
    "Goldman Sachs: 목표가 $850 상향 (리포트 p.3)",
    "Morgan Stanley: 데이터센터 시장 연 30% 성장 전망"
  ]
```

**활용 예시**:
```python
# 포트폴리오 AI 분석 시
context = kb.search("NVDA", "실적 및 전망")
→ AI 프롬프트에 자동 주입
→ AI: "NVDA 보유 중. 최근 10-K에 따르면 데이터센터 매출 +41%.
      Goldman Sachs 목표가 $850 (현재가 $780, 상승여력 9%).
      홀딩 유지 권장."
```

---

#### Task #3: 포트폴리오 AI 분석 통합
**예상 시간**: 1일
**산출물**:
```
app.py - AI 분석 로직 수정

Before:
user_prompt = f"NVDA 분석해줘"

After:
# 1. 리서치 검색
research = kb.search("NVDA", "실적 및 목표가")

# 2. 시장 데이터 추가
market_context = {
    'sector_momentum': sector_analyzer.get_sector_momentum("Technology"),
    'screener_rank': market_screener.get_rank("NVDA")
}

# 3. 통합 프롬프트
user_prompt = f"""
## 종목: NVDA

### 📊 리서치 근거
{research[0]}: "2025 가이던스 강세" (출처: 10-K)
{research[1]}: "목표가 $850" (출처: Goldman Sachs)

### 📈 시장 상황
- Tech 섹터 모멘텀: 8.5/10 (강세)
- 스크리닝 순위: 3위/500 (모멘텀 상위)

위 데이터를 바탕으로 투자 의견 제시.
"""

→ AI: "NVDA 홀딩 유지 (목표가 $850, 상승여력 9%)
      근거 1: 10-K 실적 강세
      근거 2: Goldman Sachs 리포트
      근거 3: Tech 섹터 모멘텀 양호
      리스크: 섹터 비중 45% (40% 초과 주의)"
```

---

### Phase 3: 한국 시장 커버리지 (선택, 2-3일) ⭐ 중우선순위

#### Task #4: 한국 증권사 리포트 크롤러
**예상 시간**: 2-3일
**산출물**:
```
skills/korean_broker_crawler.py
├── crawl_kiwoom_research()
├── crawl_samsung_securities()
├── crawl_mirae_asset()
└── extract_pdf_content()

tmp/research/005930.KS/
├── 삼성증권_반도체_2024Q4.pdf
├── 키움증권_삼성전자_목표가_상향.pdf
└── parsed_text.json
```

**주의사항**:
- 공개 리포트만 수집 (합법성)
- robots.txt 준수
- PDF 다운로드 → OCR/텍스트 추출

---

## 📊 최종 결과물 (6-9일 후)

### 1. 포트폴리오 대시보드 (app.py)
```
┌────────────────────────────────────────┐
│ 🌍 Global Market Pulse                 │
│ S&P 500 ▲0.5% | NASDAQ ▲0.8%          │
├────────────────────────────────────────┤
│ 🔥 Market Intelligence (신규)          │
│                                        │
│ 섹터 히트맵:                           │
│ Tech 🟢 +3.2% | Healthcare 🟢 +2.1%   │
│ Energy 🔴 -2.3% | Financials 🟡 +0.5%│
│                                        │
│ 오늘의 스크리닝 (모멘텀):               │
│ 1. NVDA (RSI 65, 거래량 +230%)        │
│ 2. AMD (RSI 58, 거래량 +180%)         │
│ 3. SMCI (RSI 72, 52주 고점 근접)      │
│ [전체 보기 →]                          │
├────────────────────────────────────────┤
│ 💼 Portfolio Health                    │
│ [Run AI Analysis] 🔄                   │
│                                        │
│ 🧠 AI 분석 결과 (리서치 기반):         │
│                                        │
│ 1. NVDA (엔비디아) - Satellite - 홀딩  │
│    ✅ 보유 유지 (현재 17% 비중)        │
│    📊 근거:                            │
│    - 10-K 실적: 데이터센터 +41% 성장   │
│    - Goldman Sachs 목표가 $850 상향    │
│    - Tech 섹터 모멘텀 8.5/10 (강세)    │
│    ⚠️ 모니터링: 섹터 비중 45% 주의     │
│                                        │
│ 2. Energy 섹터 추가 검토               │
│    💡 신규 매수 후보: XLE, ENPH        │
│    📊 근거:                            │
│    - 현재 Energy 비중 0% (과소)        │
│    - 스크리닝 결과: ENPH RSI 35 (저평가)│
│    - 섹터 로테이션: Energy 모멘텀 회복  │
│                                        │
│ 📚 출처:                               │
│ - NVIDIA 10-K (2024-01-15)            │
│ - Goldman Sachs Research (2024-01-12) │
│ - 실시간 섹터 분석 (2026-01-25 14:30) │
└────────────────────────────────────────┘
```

### 2. 개별 종목 분석 (pages/stock_analysis.py)
```
┌────────────────────────────────────────┐
│ 🔍 NVDA (엔비디아) 심층 분석           │
├────────────────────────────────────────┤
│ 현재가: $780 ▲2.3%                     │
│ 52주 위치: 78% 🟢                      │
├────────────────────────────────────────┤
│ 📈 차트 + 기술적 지표                  │
│ [Candlestick Chart]                    │
│ RSI: 65, MACD: 강세                    │
├────────────────────────────────────────┤
│ 🧠 AI 투자 분석 (리서치 기반)          │
│                                        │
│ ✅ 매수/홀딩 의견                       │
│                                        │
│ 📊 펀더멘털 근거:                      │
│ - 최근 10-K: 매출 $22B (+22% YoY)     │
│ - 데이터센터: $18B (+41% YoY)         │
│ - 2025 가이던스: AI 칩 수요 지속       │
│   (출처: SEC 10-K, 2024-01-15 p.45)   │
│                                        │
│ 📈 애널리스트 컨센서스:                │
│ - Goldman Sachs: $850 (▲9%)           │
│ - Morgan Stanley: $820 (▲5%)          │
│ - 평균 목표가: $835 (▲7%)             │
│   (출처: Bloomberg, 2024-01-20)       │
│                                        │
│ 🔥 시장 모멘텀:                        │
│ - Tech 섹터 순위: 3위/50 (상위 6%)    │
│ - 모멘텀 스코어: 8.2/10 (강세)         │
│ - 거래량: 평균 대비 +230% (관심 급증)  │
│                                        │
│ ⚠️ 리스크:                             │
│ - RSI 65 (중립, 70 넘으면 과매수)      │
│ - Tech 섹터 집중도 높음 (분산 필요)    │
│                                        │
│ 💡 액션:                               │
│ - 현재 보유: 50주 (평가액 $39,000)     │
│ - 추천: 홀딩 유지, $850 도달 시 25% 익절│
│ - 손절선: $720 (PSAR 기준)             │
└────────────────────────────────────────┘
```

---

## 🔄 시스템 간 연계

```
Market Intelligence
      ↓
┌──────────────────┐
│ Market Screener  │ → 신규 매수 후보
│ Sector Rotation  │ → 리밸런싱 제안
└──────────────────┘
      ↓
Research Knowledge Base
      ↓
┌──────────────────┐
│ SEC Edgar        │ → 실적 근거
│ Analyst Reports  │ → 목표가
└──────────────────┘
      ↓
AI Analysis
      ↓
┌──────────────────┐
│ Portfolio Health │ → 종합 의견
│ Stock Analysis   │ → 매수/매도 액션
└──────────────────┘
      ↓
User Action
```

---

## 🎯 활용 시나리오

### 시나리오 1: 아침 루틴
```
1. 앱 오픈
2. Market Intelligence 확인
   → "Tech 섹터 과열, Healthcare 강세"
3. Portfolio Health 분석 실행
   → "Tech 45% → 35% 축소 권장"
   → "근거: Goldman Sachs 리포트 + 섹터 로테이션"
4. 스크리닝 결과 확인
   → "ENPH (에너지) RSI 35, 저평가"
5. 개별 종목 분석
   → "ENPH 매수 적기, 목표가 $180"
6. 실행: NVDA 25% 익절 → ENPH 매수
```

### 시나리오 2: 종목 발굴
```
1. Market Screener 실행
   → "모멘텀 상위 10종목"
2. SMCI 발견 (RSI 72, 거래량 +300%)
3. Stock Analysis 페이지 이동
4. AI 분석 실행
   → "최근 10-K: 매출 +150%, 목표가 $850"
   → "근거: Morgan Stanley 리포트"
5. 포트폴리오 추가 여부 판단
```

### 시나리오 3: 리밸런싱
```
1. Portfolio Health 분석
   → "Tech 섹터 45% (목표 35%)"
2. Sector Rotation 확인
   → "Healthcare로 자금 유입 중"
3. 스크리닝 결과
   → "Healthcare 섹터 상위 5종목"
4. 리서치 확인
   → "XLV ETF: Goldman Sachs 목표가 상향"
5. 실행: NVDA 일부 익절 → XLV 매수
```

---

## 📅 일정

### Week 1 (Day 1-4): Phase 1
- Day 1: Task #5 (Market Screener)
- Day 2: Task #6 (Sector Rotation)
- Day 3: Task #7 (Dashboard 통합)
- Day 4: 테스트 및 버그 수정

### Week 2 (Day 5-8): Phase 2
- Day 5: Task #1 (SEC Edgar)
- Day 6-7: Task #2 (ChromaDB RAG)
- Day 8: Task #3 (AI 분석 통합)

### Week 3 (선택): Phase 3
- Day 9-11: Task #4 (한국 증권사)

---

## 🎓 기술 스택 추가

### 새로 도입
- **ChromaDB**: 벡터 데이터베이스 (RAG)
- **LangChain** (선택): 문서 로딩/임베딩
- **sec-edgar-downloader**: SEC 공시 수집
- **PyPDF2/pdfplumber**: PDF 파싱

### 기존 유지
- Streamlit, Google Gemini, yfinance, CrewAI

---

## 📝 요구사항 업데이트

### requirements.txt 추가
```txt
# 벡터 DB & RAG
chromadb==0.4.22
langchain==0.1.0
sentence-transformers==2.3.1

# SEC Edgar
sec-edgar-downloader==5.0.2

# PDF 처리
PyPDF2==3.0.1
pdfplumber==0.11.0

# 한국 증권사 크롤링 (선택)
selenium==4.16.0
beautifulsoup4==4.12.3
```

---

## 🚨 리스크 및 대응

### 리스크 1: API 할당량 초과
**대응**:
- 캐싱 강화 (5분)
- yfinance 무료 tier 한계 → Finnhub 대체
- Google Embeddings 무료 tier 모니터링

### 리스크 2: 리서치 데이터 품질
**대응**:
- SEC Edgar 우선 (신뢰도 높음)
- 증권사 리포트는 공개 문서만
- 사용자 피드백 수집

### 리스크 3: 한국 증권사 크롤링 합법성
**대응**:
- 공개 리포트만 수집
- robots.txt 준수
- API 제공 시 API 우선
- 불가능하면 Phase 3 포기

---

**최종 업데이트**: 2026-01-25
**예상 완료**: 2026-02-08 (2주)
**우선순위**: Phase 1 → Phase 2 → (Phase 3)
