# Spec: Professional Report Template Deepening (v2.0)

## 1. 개요 (Overview)
`Prism Insight`의 전문가용 보고서 형식을 OMNI에 이식하여, 마스터가 리포트 한 장으로 종목의 기술적/기본적/심리적 상태를 완벽히 파악하도록 개선한다.

## 2. 리포트 구조 및 데이터 매핑 (Data Mapping)

| 섹션 (Section) | 포함 데이터 (Fields) | 시각적 스타일 |
|:---|:---|:---|
| **0. Executive Summary** | `verdict`, `score`, 핵심 요약 문장 | OMNI Blue 테두리 박스 |
| **1. Technical Pulse** | `rsi`, `vol_surge`, `ma_alignment`, `52w_high_dist` | 정밀 수치 테이블 |
| **2. Business Vitality** | `market_cap`, `dividend_yield`, `pe_ratio` | 가로형 요약 리스트 |
| **3. Market Sentiment** | `market_news` (Top 3), `sentiment_score` | 감성 배지(Color Badge) |
| **4. Strategic Verdict** | `reason`, `action_plan` | 굵은 인용문 (Blockquote) |

## 3. 템플릿 로직 개선 (Jinja2 Logic)
- **Safe Rendering**: 특정 지표 누락 시 "데이터 수집 중"으로 자동 대체.
- **Conditional Highlighting**: 수익률이나 점수가 특정 임계치를 넘을 경우 강조색(`Red/Blue`) 적용.

## 4. 구현 태스크 분할 (Atomic Tasks)
- **Task 7.3.1**: `MarketScreener`에 추가 지표(`52w_high`, `dividend` 등) 수집 로직 추가.
- **Task 7.3.2**: `skills/templates/report_template.md` 전면 개편.
- **Task 7.3.3**: `ResearchEngine`에서 신규 지표를 템플릿에 주입하는 로직 보강.

## 5. 승인 요청
마스터, 위 설계대로 '종이 조각'이 아닌 '진짜 리포트'를 만들어도 되겠습니까?
