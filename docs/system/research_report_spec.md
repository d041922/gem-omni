# Spec: Unified Investment Research Report (v1.0)

## 1. 개요 (Overview)
`ResearchEngine`을 통해 퀀트 데이터(Screener)와 정성적 뉴스(Exa)를 결합하여, 마스터의 최종 의사결정을 돕는 **A4 1장 분량의 고밀도 투자 보고서**를 생성한다.

## 2. 리포트 구조 (Structure)

### 2.1 Header: Asset Identity
- 종목명 (Ticker)
- 현재가 및 등락률
- 생성 시각 (UTC)

### 2.2 Section 1: Quantitative Health (정량 분석)
- **Trend**: MA 정배열 여부, 52주 신고가 대비 위치.
- **Momentum**: RSI (과매수/과매도), MACD 시그널.
- **Flow**: 거래량 급증 배수 (Volume Surge Ratio).

### 2.3 Section 2: Market Context (정성 분석)
- **News Summary**: 최근 24시간 내 핵심 뉴스 3줄 요약.
- **Sector Sentiment**: 해당 섹터(Tech, Bio 등)의 시장 분위기.

### 2.4 Section 3: AI Strategic Verdict (결론)
- **Rating**: Strong Buy / Buy / Hold / Sell
- **Action Plan**: "현재 RSI 35로 과매도 구간이나, 뉴스 심리가 부정적이므로 분할 매수 권장."

## 3. 기술 구현 (Implementation)
- **Engine**: `skills/research_engine.py`
- **Template**: `skills/templates/report_template.md` (Jinja2)
- **Data Flow**: 
    1. `MarketScreener.screen_stocks([ticker])` -> 퀀트 데이터 확보.
    2. `NewsManager` (or Exa direct) -> 뉴스 데이터 확보.
    3. `LLM Synthesis` -> Verdict 생성.
    4. `MarkdownPdf` -> PDF 변환.

## 4. 검증 계획
- **UT-REP-01**: 데이터가 모두 있을 때 PDF 생성 성공 여부.
- **UT-REP-02**: 뉴스 데이터가 없을 때("No News")도 리포트가 깨지지 않고 생성되는지 확인.

## 5. 승인 요청
마스터, 위 설계대로 리포트 엔진을 구현하여 `Stock Analysis` 페이지에 탑재해도 되겠습니까?
