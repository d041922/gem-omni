# Spec: Screener UI Intelligence Integration (v1.0)

## 1. 개요 (Overview)
`MarketScreener`가 발굴한 원천 데이터를 `AnalysisManager`를 통해 정제하고, 마스터의 투자 원칙과 과거 경험이 반영된 **'최종 전략'**을 화면에 출력한다.

## 2. 데이터 처리 흐름 (Data Flow)
1. **Discovery**: `MarketScreener`가 500개 종목 중 모멘텀 상위 종목 추출.
2. **Refinement**: 추출된 종목을 `AnalysisManager.analyze_candidate()`에 투입.
3. **Filtering**: 마스터의 `investment_principles`(금지 섹터 등)에 걸리는 종목은 'Filtered' 처리.
4. **Scoring**: 퀀트(50%) + 기억(30%) + 뉴스(20%) 가중치로 `final_score` 산출.

## 3. UI 컴포넌트 명세
### 3.1 전략적 요약 테이블 (Main Table)
| 컬럼명 | 내용 | 스타일 |
|:---|:---|:---|
| **티커** | 종목 코드 | Bold |
| **최종 점수** | `final_score` | Progress Bar 또는 Heatmap |
| **전략 의견** | `verdict` | 색상 배지 (Red: Buy, Green: Strong Buy, Gray: Watch) |
| **분석 근거** | `reason` | 한글 텍스트 요약 |

### 3.2 원칙 가드 (Principle Guard)
- 필터링된 종목은 별도의 '추천 제외' 섹션에 사유와 함께 노출 (투명성 확보).

## 4. 검증 계획
- **UT-SCR-01**: 스크리너 결과가 `AnalysisManager`를 거쳐 `final_score`를 포함한 딕셔너리로 변환되는지 확인.
- **UT-SCR-02**: UI 테이블에 '전략 의견' 컬럼이 정상적으로 렌더링되는지 확인.

## 5. 승인 요청
마스터, 위 설계대로 스크리너 화면에 '에이전트의 판단력'을 이식해도 되겠습니까?
