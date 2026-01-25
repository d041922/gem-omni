# GEM: OMNI 시스템 개선 계획서

## 📋 현재 문제점 분석

### 1. 대시보드 구조 문제
**현상**:
- 시장 정보 / 포트폴리오 / 종목 분석이 각각 독립적으로 AI 분석 수행
- 페이지 간 통합이 없고 정보 연계가 부족
- 사용자 입장에서 전체적인 투자 전략이 파편화되어 보임

**근본 원인**:
- 각 페이지가 독립적으로 설계됨
- Master AI Orchestrator가 없음
- Context 공유 메커니즘 부재

### 2. 시장 정보 위치 문제
**현상**:
- 시장 정보가 포트폴리오 대시보드 상단에 고정
- 스크리닝이 단순 모멘텀 상위만 표시 (실제 매수 추천 없음)

**근본 원인**:
- 정보 아키텍처 설계 미흡
- 시장 정보와 개인 포트폴리오가 혼재

### 3. 코어/위성 비중 선정 기준 불명확
**현상**:
- 너무 공격적이라 방어적으로 조정해야 하는데 거부감
- 분류 기준이 코드에 하드코딩됨 (app.py:399-459행, 621-678행 중복)

**근본 원인**:
- 사용자 설정 가능한 전략 옵션 없음
- 공통 유틸리티로 분리되지 않음

### 4. 종목 분석 데이터 누락 및 불일치
**현상**:
- PEG, 경쟁사 정보가 안 보이는 경우 있음
- 포트폴리오 종목 확인 불일치 (UI는 "보유 중", AI는 "없는 종목")

**근본 원인**:
- 에러 핸들링이 단순함 (skills/peer_comparison.py, valuation_engine.py)
- 포트폴리오 체크 로직이 두 곳에서 다르게 구현됨:
  - stock_analysis.py:20-57 (check_portfolio_holding)
  - stock_analysis_crew.py:119-150 (portfolio_context)

### 5. 코드 중복
**현상**:
- classify_asset 로직이 app.py에 두 번 나옴
- 포트폴리오 데이터 로딩, 가격 조회가 여러 곳에서 반복
- Google Sheets 로딩, yfinance 호출 등 중복

**근본 원인**:
- 공통 유틸리티 라이브러리 부재
- 리팩토링 필요

---

## 🎯 개선 방안

### Phase 1: 대시보드 구조 재설계 (우선순위: 높음)

#### Option A: 3-Layer 계층 구조 (추천)
```
┌─────────────────────────────────────────┐
│  L1: Market Overview (시장 정보)         │
│  - 글로벌 지수, 섹터 로테이션            │
│  - AI 기반 "오늘의 매수 추천"            │
│  - 마켓 심리 분석                        │
└─────────────────────────────────────────┘
           ↓ (마켓 컨텍스트 제공)
┌─────────────────────────────────────────┐
│  L2: Portfolio Command Center (메인)     │
│  - 전체 포트폴리오 건강도                │
│  - Master AI Orchestrator                │
│  - Core-Satellite 균형, 리밸런싱 제안    │
└─────────────────────────────────────────┘
           ↓ (종목별 드릴다운)
┌─────────────────────────────────────────┐
│  L3: Stock Deep Dive (개별 종목)         │
│  - 기술적/펀더멘털/밸류에이션 분석       │
│  - Multi-Agent 투자 의견                 │
└─────────────────────────────────────────┘
```

**구현 방법**:
1. `pages/market_overview.py` 신규 생성
   - fetch_market_data() 이동
   - load_market_intelligence() 확장
   - AI 기반 매수 추천 로직 추가 (skills/market_recommender.py)

2. `app.py` (Portfolio Command Center) 재구성
   - Master AI Orchestrator 추가
   - L1(시장 정보) + L3(개별 종목 분석) 통합 의견 제시
   - 예: "현재 시장은 AI 섹터 강세 → 포트폴리오의 NVDA 비중 적절 → PLTR 추가 매수 고려"

3. `pages/stock_analysis.py` 개선
   - 포트폴리오 연계 강화
   - "이 종목을 포트폴리오에 추가하면?" 시뮬레이션

#### Option B: 통합 대시보드 페이지 추가 (대안)
- 새로운 "통합 대시보드" 페이지 생성
- 시장 + 포트폴리오 + 개별 종목을 한눈에 표시
- Master AI가 전체 조율

**권장: Option A (계층 구조가 명확하고 확장 가능)**

---

### Phase 2: 시장 정보 페이지 분리 (우선순위: 높음)

#### 새로운 `pages/market_overview.py` 생성
```python
"""
Market Overview Page
Global market intelligence and buy recommendations
"""

# 섹션 1: 글로벌 지수 (기존 fetch_market_data)
# 섹션 2: 섹터 로테이션 히트맵 (기존 load_market_intelligence)
# 섹션 3: AI 기반 "오늘의 매수 추천" (신규)
#   - 단순 모멘텀 상위가 아님
#   - 펀더멘털 + 기술적 지표 + 밸류에이션 종합
#   - "매수 신호", "매수 타이밍", "목표가", "리스크" 포함
# 섹션 4: Fear & Greed Index, VIX 분석
```

#### 신규 스킬: `skills/market_recommender.py`
```python
def generate_buy_recommendations(
    screener_data: List[Dict],
    user_portfolio: pd.DataFrame,
    market_context: Dict
) -> List[Dict]:
    """
    Generate AI-powered buy recommendations

    Returns:
        [
            {
                'ticker': 'NVDA',
                'signal': 'Strong Buy',
                'entry_price': 125.5,
                'target_price': 145.0,
                'rationale': 'AI 데이터센터 수요 강세, ADX 30 추세 강함',
                'risk_level': 'Medium',
                'portfolio_fit': 'Satellite - 5% 추가 매수 가능'
            }
        ]
    """
    pass
```

---

### Phase 3: 코어/위성 분류 개선 (우선순위: 중간)

#### 신규 유틸리티: `skills/asset_classifier.py`
```python
"""
Core-Satellite Asset Classifier
Unified asset classification logic
"""

class AssetClassifier:
    STRATEGIES = {
        'aggressive': {
            'core_target': (40, 50),      # 40-50%
            'satellite_target': (50, 60),  # 50-60%
            'default_class': 'Satellite'
        },
        'balanced': {
            'core_target': (50, 60),
            'satellite_target': (40, 50),
            'default_class': 'Satellite'
        },
        'defensive': {
            'core_target': (60, 70),
            'satellite_target': (30, 40),
            'default_class': 'Core'
        }
    }

    def __init__(self, strategy: str = 'balanced'):
        """
        Args:
            strategy: 'aggressive', 'balanced', 'defensive'
        """
        self.strategy = self.STRATEGIES[strategy]

    def classify(self, ticker: str, category: str, name: str) -> str:
        """
        Classify asset as Core or Satellite

        우선순위:
        1. 카테고리 키워드
        2. 티커 매칭
        3. 종목명 패턴
        4. 기본값 (전략에 따라)
        """
        # ... (기존 classify_asset_improved 로직 이동)
        pass

    def get_rebalancing_target(self, current_core_pct: float) -> Dict:
        """
        현재 Core 비중에 따른 리밸런싱 목표 제시
        """
        target_min, target_max = self.strategy['core_target']

        if current_core_pct < target_min:
            return {
                'action': 'increase_core',
                'target_pct': target_min,
                'adjustment_needed': target_min - current_core_pct
            }
        elif current_core_pct > target_max:
            return {
                'action': 'decrease_core',
                'target_pct': target_max,
                'adjustment_needed': current_core_pct - target_max
            }
        else:
            return {'action': 'maintain', 'status': 'balanced'}
```

#### USER_PROFILE.md 업데이트
```markdown
## 투자 전략 설정

### 현재 전략: [aggressive/balanced/defensive]

- **aggressive**: Core 40-50%, Satellite 50-60% (7-10년 내 경제적 자유)
- **balanced**: Core 50-60%, Satellite 40-50% (안정적 성장)
- **defensive**: Core 60-70%, Satellite 30-40% (자본 보전 우선)

설정 변경 방법:
```python
from skills.asset_classifier import AssetClassifier
classifier = AssetClassifier(strategy='balanced')
```
```

#### app.py, stock_analysis_crew.py 리팩토링
```python
# Before (중복 코드)
def classify_asset_improved(...):
    # 400줄 코드 중복

# After (공통 유틸 사용)
from skills.asset_classifier import AssetClassifier

classifier = AssetClassifier(strategy='balanced')  # USER_PROFILE에서 로드
asset_type = classifier.classify(ticker, category, name)
```

---

### Phase 4: 종목 분석 데이터 누락 개선 (우선순위: 중간)

#### 4-1. PEG, 경쟁사 정보 에러 핸들링 강화

**현재 문제** (stock_analysis.py:626-627):
```python
if 'error' in result:
    st.info(f"경쟁사 데이터를 불러올 수 없습니다. 주요 종목만 지원됩니다.")
    return
```

**개선안**:
```python
if 'error' in result:
    error_msg = result.get('error', 'Unknown')

    # Fallback: yfinance로 기본 정보라도 표시
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info

        st.warning("⚠️ 상세 경쟁사 데이터 없음 (기본 정보만 표시)")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("PER", f"{info.get('trailingPE', 0):.1f}")
        col2.metric("PEG", f"{info.get('pegRatio', 0):.2f}")
        col3.metric("섹터", info.get('sector', 'N/A'))
        col4.metric("산업", info.get('industry', 'N/A'))

        st.caption(f"💡 상세 경쟁사 분석은 주요 종목(NVDA, AAPL, TSLA 등)만 지원됩니다.")
        st.caption(f"🔍 오류 상세: {error_msg}")
    except:
        st.error(f"데이터를 불러올 수 없습니다: {error_msg}")

    return
```

**skills/peer_comparison.py, valuation_engine.py 개선**:
- 데이터 없을 때 yfinance fallback 로직 추가
- 최소한의 정보라도 표시

#### 4-2. 포트폴리오 종목 확인 불일치 해결

**현재 문제**:
- `stock_analysis.py:20-57` (check_portfolio_holding)
- `stock_analysis_crew.py:119-150` (portfolio_context)
- 두 곳에서 다르게 구현됨 → 결과 불일치

**해결 방법**: 공통 유틸리티로 통합

**신규 파일**: `skills/portfolio_utils.py`
```python
"""
Portfolio Utility Functions
Unified portfolio data access and checks
"""

def load_portfolio_from_session() -> Optional[pd.DataFrame]:
    """
    Load portfolio from session state

    Returns:
        Portfolio DataFrame or None
    """
    import streamlit as st

    if 'calculated_portfolio' in st.session_state:
        return st.session_state.calculated_portfolio
    elif 'raw_portfolio_df' in st.session_state:
        return st.session_state.raw_portfolio_df
    else:
        return None


def check_portfolio_holding(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Check if ticker is in user's portfolio (UNIFIED VERSION)

    Returns:
        Dict with holding info or None if not found
    """
    portfolio_df = load_portfolio_from_session()

    if portfolio_df is None:
        return None

    # Normalize ticker column name
    ticker_col = None
    for col in ['종목코드', '티커코드', 'ticker']:
        if col in portfolio_df.columns:
            ticker_col = col
            break

    if ticker_col is None:
        return None

    # Normalize ticker for comparison
    portfolio_df['_normalized_ticker'] = portfolio_df[ticker_col].astype(str).str.upper().str.strip()
    ticker_normalized = ticker.upper().strip()

    match = portfolio_df[portfolio_df['_normalized_ticker'] == ticker_normalized]

    if match.empty:
        return None

    row = match.iloc[0]
    return {
        'ticker': ticker,
        'name': row.get('종목명', row.get('name', ticker)),
        'quantity': float(row.get('수량', 0)),
        'avg_price_usd': float(row.get('평균 단가(USD)', 0)),
        'avg_price_krw': float(row.get('평균 단가(KRW)', 0)),
        'current_value': float(row.get('평가금액(KRW)', 0)),
        'profit_loss': float(row.get('손익(KRW)', 0)),
        'return_pct': float(row.get('수익률(%)', 0)),
        'sector': row.get('카테고리', 'Unknown'),
        'account': row.get('계좌', 'Unknown')
    }


def get_portfolio_context_for_ai(ticker: str) -> str:
    """
    Generate portfolio context text for AI agents (UNIFIED VERSION)
    Used by stock_analysis_crew.py
    """
    portfolio_df = load_portfolio_from_session()

    if portfolio_df is None:
        return "\n## 📊 현재 포트폴리오 정보\n- 포트폴리오 데이터 없음\n"

    holdings = []
    total_value = portfolio_df['평가금액(KRW)'].sum() if '평가금액(KRW)' in portfolio_df.columns else 0

    # Calculate sector concentration
    sector_dist = {}
    for _, row in portfolio_df.iterrows():
        sector = row.get('카테고리', 'Unknown')
        value = row.get('평가금액(KRW)', 0)
        value_pct = (value / total_value * 100) if total_value > 0 else 0

        sector_dist[sector] = sector_dist.get(sector, 0) + value_pct

        holdings.append({
            'ticker': row.get('종목코드', row.get('티커코드', '')),
            'name': row.get('종목명', ''),
            'sector': sector,
            'value_pct': value_pct
        })

    # Check if ticker exists
    existing_position = check_portfolio_holding(ticker)

    context = f"""
## 📊 현재 포트폴리오 정보
- 총 보유 종목: {len(holdings)}개
- 총 평가금액: ₩{total_value/1e8:.2f}억원
- {ticker} 기존 보유: {'있음 ('+f"{existing_position['return_pct']:.1f}% 수익률, {existing_position['current_value']/1e6:.0f}백만원"+')' if existing_position else '없음'}

### 섹터 분산 현황
{chr(10).join([f"- {sector}: {pct:.1f}%" for sector, pct in sorted(sector_dist.items(), key=lambda x: -x[1])])}

### Top 5 보유 종목
{chr(10).join([f"- {h['name']} ({h['ticker']}): {h['value_pct']:.1f}%" for h in sorted(holdings, key=lambda x: -x['value_pct'])[:5]])}
"""

    return context
```

**stock_analysis.py 리팩토링**:
```python
# Before
def check_portfolio_holding(ticker: str) -> Optional[Dict[str, Any]]:
    # 40줄 중복 코드

# After
from skills.portfolio_utils import check_portfolio_holding
```

**stock_analysis_crew.py 리팩토링**:
```python
# Before
portfolio_context = f"""
## 📊 현재 포트폴리오 정보
...
"""  # 30줄 중복 코드

# After
from skills.portfolio_utils import get_portfolio_context_for_ai

portfolio_context = get_portfolio_context_for_ai(ticker)
```

---

### Phase 5: 코드 중복 제거 (우선순위: 낮음)

#### 5-1. 포트폴리오 데이터 로딩 통합
**신규 파일**: `skills/data_loader_unified.py`
```python
"""
Unified Data Loader
Central hub for all data loading operations
"""

@st.cache_data(ttl=600)  # 10분 캐싱
def load_portfolio_with_prices(
    spreadsheet_name: str = "GEM_Finance_Portfolio",
    exchange_rate: float = 1450
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Load portfolio from Google Sheets and fetch current prices

    Returns:
        (calculated_df, current_prices)
    """
    from skills.gsheet_loader import load_data_from_gsheet
    from skills.finance_core_lib import calculate_portfolio_metrics
    import yfinance as yf

    # Load from Google Sheets
    portfolio_df, watchlist_df, cash_df = load_data_from_gsheet(spreadsheet_name)

    # Fetch current prices
    current_prices = {}
    ticker_col = '종목코드' if '종목코드' in portfolio_df.columns else '티커코드'

    if ticker_col in portfolio_df.columns:
        tickers = portfolio_df[ticker_col].dropna().unique()
        for ticker in tickers:
            try:
                stock = yf.Ticker(str(ticker))
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_prices[ticker] = float(hist['Close'].iloc[-1])
            except:
                pass

    # Calculate metrics
    calculated_df = calculate_portfolio_metrics(portfolio_df, current_prices, exchange_rate)

    return calculated_df, current_prices


@st.cache_data(ttl=300)  # 5분 캐싱
def load_market_data() -> Dict[str, Dict]:
    """
    Unified market data loader (indices, VIX, etc.)
    """
    # ... (기존 fetch_market_data 로직)
    pass
```

**app.py 리팩토링**:
```python
# Before
try:
    from skills.gsheet_loader import load_data_from_gsheet
    portfolio_df, watchlist_df, cash_df = load_data_from_gsheet("GEM_Finance_Portfolio")

    # ... 30줄 가격 조회 로직 ...

    calculated_df = calculate_portfolio_metrics(portfolio_df, current_prices, 1450)
    st.session_state.calculated_portfolio = calculated_df
except Exception as e:
    st.error(f"Failed to load Google Sheets data: {e}")

# After
from skills.data_loader_unified import load_portfolio_with_prices

try:
    calculated_df, current_prices = load_portfolio_with_prices()
    st.session_state.calculated_portfolio = calculated_df
    st.session_state.current_prices = current_prices
except Exception as e:
    st.error(f"Failed to load portfolio data: {e}")
```

---

## 🚀 구현 우선순위

### Priority 1 (즉시 실행)
1. **코어/위성 분류 통합** (Phase 3)
   - `skills/asset_classifier.py` 생성
   - app.py 중복 코드 제거
   - 예상 시간: 1-2시간

2. **포트폴리오 체크 로직 통합** (Phase 4-2)
   - `skills/portfolio_utils.py` 생성
   - stock_analysis.py, stock_analysis_crew.py 리팩토링
   - 예상 시간: 1시간

### Priority 2 (단기 - 1주일 내)
3. **시장 정보 페이지 분리** (Phase 2)
   - `pages/market_overview.py` 생성
   - AI 기반 매수 추천 로직 추가
   - 예상 시간: 3-4시간

4. **종목 분석 에러 핸들링 개선** (Phase 4-1)
   - PEG, 경쟁사 정보 fallback 로직
   - 예상 시간: 1-2시간

### Priority 3 (중기 - 2주일 내)
5. **대시보드 구조 재설계** (Phase 1)
   - 3-Layer 계층 구조 구현
   - Master AI Orchestrator 추가
   - 예상 시간: 5-8시간

6. **코드 중복 제거** (Phase 5)
   - 데이터 로딩 통합
   - 예상 시간: 2-3시간

---

## 📊 개선 후 예상 효과

### 사용자 경험
- ✅ 명확한 정보 계층 (시장 → 포트폴리오 → 개별 종목)
- ✅ 일관된 AI 분석 의견 (Master Orchestrator)
- ✅ 사용자 맞춤 전략 설정 (공격적/중립/방어적)
- ✅ 데이터 누락 최소화 (fallback 로직)

### 개발자 경험
- ✅ 코드 중복 제거 (유지보수성 향상)
- ✅ 공통 유틸리티 라이브러리 (재사용성 증가)
- ✅ 명확한 책임 분리 (각 모듈의 역할 명확)

### 성능 개선
- ✅ 데이터 로딩 최적화 (중복 호출 제거)
- ✅ 캐싱 전략 통합 (일관된 TTL 관리)
- ✅ 토큰 사용량 절감 (불필요한 중복 AI 호출 제거)

---

## ❓ 다음 액션

사용자 피드백 요청:
1. **대시보드 구조**: Option A (3-Layer) vs Option B (통합 대시보드) 중 선호하는 방식?
2. **투자 전략**: 현재 'aggressive' 전략을 'balanced' 또는 'defensive'로 변경하시겠습니까?
3. **구현 우선순위**: Priority 1부터 순차적으로 진행? 아니면 특정 기능 우선?

**즉시 시작 가능**: Priority 1 항목 (코어/위성 분류 통합, 포트폴리오 체크 로직 통합)
