# GEM: OMNI - 이슈 해결 가이드

## 📌 보고된 이슈 (2026-01-25)

### 1. Core/Satellite 차트 비중 오류 🔴
**증상**: Core 1%, Satellite 99%로 비정상적 표시
**원인**: 키워드 기반 분류 로직이 실제 포트폴리오 종목과 불일치
**우선순위**: 높음

### 2. 신규 섹터 누락 🟡
**증상**: AI 분석에서 로봇, 전력/에너지 섹터 언급 없음
**원인**: 투자 전략 프롬프트에 해당 섹터 정의 누락
**우선순위**: 중간

### 3. 불필요한 차트 🟢
**증상**: 종목 수익률 차트가 표와 중복
**판단**: 사용자 피드백 반영 → 제거 또는 탭 축소
**우선순위**: 낮음

---

## 🔧 해결 방안

### 이슈 1: Core/Satellite 분류 로직 개선

#### 현재 코드 (app.py:286-315, 448-469)
```python
# 문제점: 하드코딩된 키워드 리스트
core_keywords = ['SPY', 'VOO', 'QQQ', 'VTI', 'SCHD', 'VYM', 'MSFT', 'AAPL', 'JNJ', 'PG', 'KO']
satellite_keywords = ['NVDA', 'AMD', 'TSM', 'TSMC', 'SMCI', 'PLTR', ...]

# 티커가 리스트에 없으면 카테고리로 fallback
if any(kw in ticker for kw in core_keywords):
    return 'Core'
elif any(kw in ticker for kw in satellite_keywords):
    return 'Satellite'
else:
    # 카테고리 기반 (너무 단순함)
    if 'etf' in category.lower():
        return 'Core'
    else:
        return 'Satellite'  # 대부분 Satellite로 분류됨 (문제!)
```

#### 해결책 A: 카테고리 기반 분류 강화 (권장)

**장점**:
- Google Sheets에서 카테고리만 정확히 입력하면 자동 분류
- 유지보수 용이 (종목 추가 시 코드 수정 불필요)

**구현**:
```python
def classify_asset_v2(ticker: str, category: str, name: str) -> str:
    """
    개선된 Core/Satellite 분류 로직

    우선순위:
    1. 명시적 카테고리 키워드 (가장 신뢰성 높음)
    2. 티커 기반 (유명 종목)
    3. 종목명 기반 (ETF 이름 패턴)
    """
    cat_lower = str(category).lower()
    ticker_upper = str(ticker).upper()
    name_lower = str(name).lower()

    # 1단계: 카테고리 기반 분류 (최우선)
    core_categories = [
        'etf', 'index', 'sp500', 's&p500', 'nasdaq100', 'qqq',
        '배당', 'dividend', '인덱스', 'core', '채권', 'bond',
        '미국 대형주', 'large-cap', 'blue chip'
    ]

    satellite_categories = [
        'ai', '반도체', 'semiconductor', 'chip',
        '바이오', 'biotech', 'healthcare', 'gene editing',
        '성장주', 'growth', 'high growth',
        '한국', 'korea', 'kospi',
        'satellite', '테크', 'tech',
        '로봇', 'robotics', 'automation',
        '전력', 'energy', 'renewable', '신재생'
    ]

    for keyword in core_categories:
        if keyword in cat_lower:
            return 'Core'

    for keyword in satellite_categories:
        if keyword in cat_lower:
            return 'Satellite'

    # 2단계: 티커 기반 (유명 Core/Satellite 종목)
    core_tickers = {
        'SPY', 'VOO', 'VTI', 'IVV', 'QQQ', 'VIG', 'SCHD', 'VYM', 'DIA',
        'MSFT', 'AAPL', 'GOOGL', 'GOOG', 'JNJ', 'PG', 'KO', 'PEP', 'WMT'
    }

    satellite_tickers = {
        'NVDA', 'AMD', 'TSM', 'ASML', 'SMCI', 'PLTR', 'AVGO',
        'CRSP', 'EDIT', 'BEAM', 'NTLA', 'VRTX',
        'ARKK', 'SMH', 'SOXX', 'BOTZ',
        '005930', '000660', '035720', '207940'  # 삼성전자, SK하이닉스, 카카오, 삼성바이오
    }

    if ticker_upper in core_tickers:
        return 'Core'
    if ticker_upper in satellite_tickers:
        return 'Satellite'

    # 3단계: 종목명 패턴 (ETF 이름)
    if any(word in name_lower for word in ['index', 'dividend', 's&p', 'nasdaq 100']):
        return 'Core'

    if any(word in name_lower for word in ['ai', 'semiconductor', 'biotech', 'genomics', 'robotics']):
        return 'Satellite'

    # 4단계: 기본값 (알 수 없는 경우 Satellite로 분류)
    # 이유: 공격적 전략이므로 모호한 종목은 Satellite로 간주
    return 'Satellite'
```

#### 해결책 B: Google Sheets에 명시적 컬럼 추가 (가장 확실)

**Google Sheets 스키마 변경**:
| 종목명 | 티커코드 | 카테고리 | **자산분류** | 수량 | 평균매수가 | 계좌 |
|--------|----------|----------|--------------|------|------------|------|
| 엔비디아 | NVDA | AI/반도체 | **Satellite** | 50 | $120 | ISA |
| S&P 500 ETF | SPY | 인덱스 ETF | **Core** | 10 | $450 | 연금저축 |

**코드 수정**:
```python
def classify_asset_v3(row: pd.Series) -> str:
    """Google Sheets에 '자산분류' 컬럼이 있으면 우선 사용"""
    if '자산분류' in row and pd.notna(row['자산분류']):
        asset_type = str(row['자산분류']).strip().lower()
        if asset_type in ['core', 'c']:
            return 'Core'
        elif asset_type in ['satellite', 's', 'sat']:
            return 'Satellite'

    # fallback: 자동 분류
    return classify_asset_v2(row['티커코드'], row['카테고리'], row['종목명'])
```

#### 권장 조치 (단계별)

**즉시 (1시간 이내)**:
1. `app.py`의 `classify_asset` 함수를 `classify_asset_v2`로 교체
2. 로컬 테스트: `streamlit run app.py`
3. Core/Satellite 차트 확인

**단기 (1주일 이내)**:
1. Google Sheets에 '자산분류' 컬럼 추가
2. 기존 종목에 Core/Satellite 수동 입력 (정확도 100%)
3. `classify_asset_v3` 적용

---

### 이슈 2: 신규 섹터 추가 (로봇, 전력/에너지)

#### 현재 프롬프트 (investment-analyst.md:160-167)
```markdown
#### Satellite 자산 (40-50%) - 공격
- AI/반도체 (25%), 바이오/헬스케어 (10%), 한국 성장주 (10%)
```

#### 개선된 프롬프트
```markdown
#### Satellite 자산 (40-50%) - 공격
- **AI/반도체** (20-25%): NVDA, AMD, TSM, SMCI - 데이터센터, AI 칩셋
- **바이오/헬스케어** (5-10%): CRSP, EDIT, VRTX - 유전자 편집, 면역치료
- **로봇/자동화** (5-10%): BOTZ, TSLA, ABB - 산업용 로봇, AI 로보틱스
- **전력/에너지** (5-10%): ENPH, FSLR, NEE - 태양광, 풍력, 신재생 에너지
- **한국 성장주** (5-10%): 삼성전자, SK하이닉스 - 반도체, 2차전지
```

#### 수정 파일
1. `.claude/prompts/investment-analyst.md` (153-167번 줄)
2. `CLAUDE.md` (투자 철학 섹션)

#### AI 분석 프롬프트 업데이트
```python
# app.py:348-382 user_prompt 수정
user_prompt = f"""# 포트폴리오 분석 요청

## 📊 포트폴리오 요약
...

## 🚀 신규 성장 섹터 고려사항
다음 섹터들이 포트폴리오에 반영되어 있는지 확인:
1. **로봇/자동화**: 산업용 로봇, AI 로보틱스 (예: BOTZ, TSLA)
2. **전력/에너지**: 신재생 에너지, 태양광, 풍력 (예: ENPH, FSLR, NEE)
3. **AI/반도체**: 기존 주력 섹터 (예: NVDA, AMD)
4. **바이오/헬스케어**: 유전자 편집, 면역치료 (예: CRSP, EDIT)

위 섹터 중 누락된 부분이 있다면, **구체적 추천 종목과 매수 타이밍**을 제시하세요.

...
"""
```

---

### 이슈 3: 차트 UI 간소화

#### 현재 차트 탭 (app.py:472)
```python
chart_tabs = st.tabs(["📊 Core-Satellite", "🎯 수익률", "🏦 계좌별", "📈 섹터별"])
```

#### 개선안 A: 종목 수익률 차트 제거 (권장)
```python
chart_tabs = st.tabs(["📊 Core-Satellite", "🏦 계좌별", "📈 섹터별"])

# Tab 1: Core-Satellite (유지)
with chart_tabs[0]:
    # 도넛 차트 + 목표 비중 비교
    ...

# Tab 2: 계좌별 (유지)
with chart_tabs[1]:
    # 막대 차트
    ...

# Tab 3: 섹터별 (유지)
with chart_tabs[2]:
    # 수평 막대 차트
    ...
```

**이유**:
- 수익률은 하단 데이터 테이블에서 충분히 확인 가능
- 차트보다 표가 정확한 수치 전달에 유리
- UI 복잡도 감소

#### 개선안 B: 수익률을 표로 대체 (절충안)
```python
with chart_tabs[1]:
    st.markdown("### 종목별 수익률 Top 10")

    # 상위 5개
    top_5 = result_df.nlargest(5, '수익률(%)')[['종목명', '수익률(%)', '평가금액(KRW)']]
    st.dataframe(top_5, use_container_width=True)

    # 하위 5개
    bottom_5 = result_df.nsmallest(5, '수익률(%)')[['종목명', '수익률(%)', '손익(KRW)']]
    st.dataframe(bottom_5, use_container_width=True)
```

---

## 🎯 우선순위 실행 계획

### Phase 1: 긴급 수정 (1-2시간)
1. ✅ **Core/Satellite 분류 로직 개선** (`classify_asset_v2` 적용)
2. ✅ **신규 섹터 프롬프트 추가** (로봇, 전력/에너지)
3. ✅ **종목 수익률 차트 제거** (UI 간소화)

### Phase 2: 검증 (1일)
1. 로컬 테스트 → Core/Satellite 비중 확인
2. AI 분석 실행 → 신규 섹터 언급 확인
3. UI 피드백 수집

### Phase 3: 배포 (1일)
1. GitHub 커밋 & 푸시
2. Streamlit Cloud 배포
3. 프로덕션 환경 테스트

---

## 📝 테스트 체크리스트

### Core/Satellite 분류 검증
```python
# 테스트 스크립트
from skills.gsheet_loader import load_data_from_gsheet

df, _, _ = load_data_from_gsheet("GEM_Finance_Portfolio")

# classify_asset_v2 적용
df['자산분류'] = df.apply(
    lambda row: classify_asset_v2(row['티커코드'], row['카테고리'], row['종목명']),
    axis=1
)

# 비중 계산
total_value = df['평가금액(KRW)'].sum()
core_pct = (df[df['자산분류'] == 'Core']['평가금액(KRW)'].sum() / total_value * 100)
sat_pct = (df[df['자산분류'] == 'Satellite']['평가금액(KRW)'].sum() / total_value * 100)

print(f"Core: {core_pct:.1f}%")
print(f"Satellite: {sat_pct:.1f}%")

# 목표: Core 50-60%, Satellite 40-50%
assert 40 <= core_pct <= 70, f"Core 비중 이상: {core_pct:.1f}%"
assert 30 <= sat_pct <= 60, f"Satellite 비중 이상: {sat_pct:.1f}%"
```

### AI 분석 검증
1. "Run AI Analysis" 버튼 클릭
2. AI 출력에서 다음 키워드 확인:
   - ✅ "로봇" 또는 "robotics"
   - ✅ "전력" 또는 "에너지" 또는 "energy"
   - ✅ "BOTZ", "ENPH", "FSLR" 등 구체적 티커

### 차트 검증
1. Core-Satellite 도넛 차트 비중 확인
2. 계좌별 차트 데이터 정확성 확인
3. 섹터별 차트 합계 = 총 평가금액

---

## 🚀 Quick Fix 명령어

```bash
# 1. 코드 수정 (이 가이드 기반)
# app.py, .claude/prompts/investment-analyst.md 수정

# 2. 로컬 테스트
streamlit run app.py

# 3. 배포
git add app.py .claude/prompts/investment-analyst.md ISSUES_FIX.md
git commit -m "Fix: Core/Satellite 분류 개선 & 신규 섹터 추가"
git push origin master

# 4. Streamlit Cloud 자동 배포 대기 (2-5분)
```

---

**작성일**: 2026-01-25
**상태**: 🟡 수정 대기
**예상 소요 시간**: 2-3시간 (테스트 포함)
