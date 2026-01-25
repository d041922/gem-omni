# 종목 분석 시스템 현황 및 개선 방안

## 1. Bottom-Up 분석 로직 반영 현황

### 요구사항 (Claude CLI 기반 자산 관리 에이전트 설계.md)

| 분석 차원 | 주요 지표 | 현재 구현 상태 |
|:---|:---|:---|
| **수익성** | ROE, 영업이익률, EPS 성장률 | ❌ **미구현** |
| **재무 건전성** | 부채비율, 유동비율 | ❌ **미구현** |
| **가치 평가** | P/E, P/B, EV/EBITDA, DCF | 🟡 **부분 구현** (PER, PBR만) |
| **기술적 모멘텀** | SMA(20/50/200), RSI, MACD | ✅ **구현됨** (MA50 제외) |
| **뉴스 및 심리** | 뉴스 헤드라인 감성 분석 | ❌ **미구현** |

### 현재 구현된 기능 (skills/stock_analyzer.py)

**✅ 기술적 지표 (Technical Indicators)**
```python
- RSI (14일)
- MACD (12/26/9)
- 이동평균: MA20, MA60, MA200
- 볼린저밴드 (20일, ±2σ)
- 일목균형표 (전환선, 기준선, 선행스팬)
- 피보나치 레벨 (120일 기준)
```

**🟡 펀더멘털 지표 (Fundamentals - 기본만)**
```python
- PER (trailing), Forward PER
- PBR (Price to Book)
- PEG Ratio
- Beta
- 시가총액
- 배당수익률
```

**❌ 누락된 핵심 지표**
```python
- ROE (자기자본이익률)
- 영업이익률 (Operating Margin)
- 부채비율 (Debt-to-Equity)
- 유동비율 (Current Ratio)
- EPS 성장률 (EPS Growth Rate)
- EV/EBITDA
- DCF 밸류에이션
```

---

## 2. "주식 투자 시스템 설계 방법론.md" 분석

### 2.1 글로벌 자금 흐름 추적

**문서 제안 내용:**
- **MFI (Money Flow Index)**: 가격 + 거래량 기반 자금 흐름 지수
- **섹터 로테이션**: 11개 주요 섹터 ETF 추적, 12개월 모멘텀
- **국가 간 자본 이동**: IIF Portfolio Flows, IMF COFER 데이터

**현재 시스템:**
- ❌ MFI 미구현
- ❌ 섹터 분석 미구현 (개별 종목만)
- ❌ 글로벌 자금 흐름 추적 기능 없음

**적용 가능성:**
- 🟡 **중기 과제**: 개별 종목 분석에는 즉시 필요하지 않음
- ✅ **포트폴리오 레벨**: 향후 Top-Down 분석 시 유용

---

### 2.2 모델 컨텍스트 프로토콜 (MCP)

**문서 제안 내용:**
- MCP 서버를 통한 다양한 데이터 소스 통합
- Alpha Vantage, Tushare, EDGAR 등 연동
- LLM과 데이터 소스 간 표준화된 인터페이스

**현재 시스템:**
- ❌ 단순 yfinance만 사용
- ❌ MCP 구조 미도입

**적용 가능성:**
- 🟡 **장기 과제**: 현재 yfinance로 충분하나, 한국 주식(KIS API) 통합 시 유용
- ✅ **확장 시 고려**: 다양한 데이터 소스 필요 시 도입

---

### 2.3 멀티에이전트 시스템

**문서 제안 내용:**
- **Fundamental Agent**: SEC 공시, 재무제표 분석
- **Sentiment Agent**: 뉴스, 소셜미디어 감성 분석
- **Valuation Agent**: 역사적 멀티플, 기술적 지표
- **구조화된 토론**: 5라운드 교차 검토 및 합의 도출

**현재 시스템:**
- ✅ CrewAI 에이전트 존재 (Data Sync, Analyst, Risk, Strategy)
- ❌ **종목 분석용 전문 에이전트 없음** (포트폴리오 레벨만)
- ❌ 토론 기반 의사결정 미구현 (단일 Gemini API 호출만)

**적용 가능성:**
- ✅ **고우선순위**: 종목 분석에 멀티에이전트 도입 가능
- 예: Fundamental Agent → Sentiment Agent → Valuation Agent 순차 분석

---

### 2.4 과매수 대응 전략

**문서 제안 내용:**
- **ADX (Average Directional Index)**: 추세 강도 측정
- **파라볼릭 SAR**: 트레일링 스톱
- **MFI + 거래량**: 기관급 자금 유입 감지

**현재 시스템:**
- ❌ ADX 미구현
- ❌ 파라볼릭 SAR 미구현
- ✅ RSI만으로 과매수/과매도 판단 중

**적용 가능성:**
- ✅ **즉시 적용 가능**: technical_indicators.py에 추가 가능
- ADX는 추세 확인에 매우 유용

---

### 2.5 행동 재무학적 편향 제어

**문서 제안 내용:**
- **자동화 편향 경고**: "이 판단이 틀릴 수 있는 3가지 이유" 출력
- **손실 회피 대응**: 기회비용 고려한 리밸런싱
- **악마의 대변인**: 부정적 회의론자 에이전트

**현재 시스템:**
- ✅ AI 프롬프트에 "주요 리스크 3가지 이상" 명시 요구
- ❌ 악마의 대변인 패턴 미구현
- ❌ 대안 시나리오 자동 생성 미구현

**적용 가능성:**
- ✅ **고우선순위**: AI 프롬프트 개선으로 즉시 적용 가능
- 멀티에이전트 도입 시 더욱 효과적

---

## 3. 우선순위별 개선 방안

### 🔴 즉시 적용 (High Priority)

#### 3.1 펀더멘털 지표 확장
```python
# skills/stock_analyzer.py에 추가
def get_fundamental_metrics(ticker: str) -> Dict[str, float]:
    """ROE, 영업이익률, 부채비율, 유동비율 등"""
    stock = yf.Ticker(ticker)
    financials = stock.financials
    balance = stock.balance_sheet

    return {
        "roe": stock.info.get("returnOnEquity", 0) * 100,  # %
        "operating_margin": stock.info.get("operatingMargins", 0) * 100,
        "debt_to_equity": stock.info.get("debtToEquity", 0),
        "current_ratio": stock.info.get("currentRatio", 0),
        "eps_growth": stock.info.get("earningsQuarterlyGrowth", 0) * 100
    }
```

**예상 효과:**
- ✅ Bottom-Up 분석 테이블 80% 충족
- ✅ 투자 메모 작성 시 정량적 근거 강화

---

#### 3.2 기술적 지표 추가 (ADX, MFI, SAR)
```python
# skills/technical_indicators.py에 추가
def calculate_adx(df: pd.DataFrame, period=14) -> pd.DataFrame:
    """ADX (Average Directional Index) 계산"""
    # +DI, -DI, ADX 계산
    ...

def calculate_mfi(df: pd.DataFrame, period=14) -> pd.DataFrame:
    """MFI (Money Flow Index) 계산"""
    # Typical Price * Volume 기반
    ...

def calculate_parabolic_sar(df: pd.DataFrame) -> pd.DataFrame:
    """Parabolic SAR (Stop and Reverse) 계산"""
    # 트레일링 스톱 포인트
    ...
```

**예상 효과:**
- ✅ 강세장 과매수 구간 대응력 향상
- ✅ 추세 전환 조기 감지

---

#### 3.3 AI 프롬프트 개선 (악마의 대변인)
```markdown
# .claude/prompts/stock-analyst.md 수정

## 5️⃣ 주요 리스크
1. **[리스크 유형]**: 구체적 설명과 확률
2. **[리스크 유형]**: 구체적 설명과 확률
3. **[리스크 유형]**: 구체적 설명과 확률

## 6️⃣ 반대 의견 (Devil's Advocate)
**만약 이 분석이 틀렸다면?**
- 간과한 리스크 1:
- 간과한 리스크 2:
- 대안 시나리오:
```

**예상 효과:**
- ✅ 확인 편향 방지
- ✅ 투자 의사결정 품질 향상

---

### 🟡 중기 적용 (Medium Priority)

#### 3.4 종목 분석용 멀티에이전트 시스템
```python
# agents/crewai_agents/stock_agents.py (신규)

class FundamentalAnalystAgent:
    """재무제표, 실적 분석 전문"""
    def analyze(self, ticker: str) -> Dict:
        # ROE, 부채비율, EPS 성장률 분석
        ...

class SentimentAnalystAgent:
    """뉴스, 심리 분석 전문"""
    def analyze(self, ticker: str) -> Dict:
        # 뉴스 감성 분석 (NewsAPI or GPT-4o)
        ...

class ValuationAnalystAgent:
    """밸류에이션, 기술적 분석 전문"""
    def analyze(self, ticker: str) -> Dict:
        # PER 밴드, 기술적 지표 종합
        ...

class StockAnalysisCrew:
    """3개 에이전트 협업 및 토론"""
    def run_analysis(self, ticker: str) -> str:
        # 1. 각 에이전트 독립 분석
        # 2. 교차 검토 (5라운드)
        # 3. 합의 도출
        ...
```

**예상 효과:**
- ✅ 다각도 분석으로 정확도 향상
- ✅ 환각 현상 감소

---

#### 3.5 뉴스 감성 분석 추가
```python
# skills/sentiment_analyzer.py (신규)

def fetch_news_sentiment(ticker: str) -> Dict[str, Any]:
    """NewsAPI or Finnhub 활용 뉴스 감성 분석"""
    # Positive/Neutral/Negative 점수
    # 최근 7일 헤드라인 분석
    ...
```

**예상 효과:**
- ✅ Bottom-Up 분석 테이블 100% 충족
- ✅ 단기 모멘텀 판단에 유용

---

### 🔵 장기 적용 (Low Priority)

#### 3.6 섹터 로테이션 분석
- 포트폴리오 레벨에서 Top-Down 분석 시 도입
- 11개 섹터 ETF (XLK, XLE, XLF 등) 추적

#### 3.7 MCP 기반 데이터 통합
- 한국 주식 (KIS API) 통합 시 고려
- OpenDART (한국 공시) 연동

---

## 4. 결론 및 제안

### 현재 시스템 평가

| 항목 | 점수 | 평가 |
|:---|:---:|:---|
| 기술적 분석 | ⭐⭐⭐⭐ (4/5) | MA, RSI, MACD 충실, ADX/MFI 추가 필요 |
| 펀더멘털 분석 | ⭐⭐ (2/5) | PER/PBR만, ROE/부채비율 등 누락 |
| 감성 분석 | ⭐ (1/5) | 미구현 |
| 리스크 관리 | ⭐⭐⭐ (3/5) | 기본 리스크 명시, 트레일링 스톱 없음 |
| 토큰 최적화 | ⭐⭐⭐⭐⭐ (5/5) | 프롬프트 캐싱, 데이터 분리 완벽 |

**종합 점수: 3.0/5.0**

### 추천 개선 순서

**Phase 1 (즉시, 1-2일)**
1. ✅ 펀더멘털 지표 확장 (ROE, 영업이익률, 부채비율, EPS 성장률)
2. ✅ 기술적 지표 추가 (ADX, MFI, 파라볼릭 SAR)
3. ✅ AI 프롬프트 개선 (악마의 대변인 섹션)

**Phase 2 (중기, 1주)**
4. 🟡 종목 분석용 멀티에이전트 시스템 구축
5. 🟡 뉴스 감성 분석 추가

**Phase 3 (장기, 1개월+)**
6. 🔵 섹터 로테이션 분석
7. 🔵 MCP 기반 데이터 통합

---

## 5. "주식 투자 시스템 설계 방법론.md" 적용도

| 문서 주요 내용 | 현재 적용도 | 우선순위 |
|:---|:---:|:---:|
| MFI 자금 흐름 지표 | 0% | 🔴 High |
| 섹터 로테이션 | 0% | 🔵 Low |
| MCP 프로토콜 | 0% | 🔵 Low |
| 멀티에이전트 (종목용) | 0% | 🟡 Medium |
| ADX + SAR | 0% | 🔴 High |
| 행동 편향 제어 | 30% | 🔴 High |

**문서 활용 가치: ⭐⭐⭐⭐⭐ (5/5)**
- 매우 포괄적이고 체계적인 가이드
- 현재 시스템의 로드맵으로 활용 가능
- 즉시 적용 가능한 부분(ADX, MFI, 편향 제어)과 장기 과제(MCP, 섹터 분석) 명확히 구분됨

---

**작성일**: 2026-01-25
**버전**: 1.0
**다음 리뷰**: Phase 1 완료 후
