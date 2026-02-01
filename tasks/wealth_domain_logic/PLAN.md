# TASK: Wealth Domain Logic & Data Integration Overhaul
> "Investing.com의 정밀함과 Toss의 직관성을 통합하는 재정 에이전트 핵심 로직 설계"

## 1. Objective (목표)
- 데이터 파편화 해결: 여러 소스(yfinance, KIS, Exa)에서 오는 데이터를 하나의 표준 모델로 통합.
- 분석 신뢰도 확보: 마스터가 "데이터를 잘 몰라도 근거는 눈으로 볼 수 있게" 시각적 증거(Rationale) 자동 생성.
- 자동화 기반 구축: 수동 동기화를 최소화하는 이벤트 기반 데이터 엔진 설계.

## 2. Technical Specification (기술 명세)
### A. Unified Data Model (정규화)
- `core/models.py`: 모든 자산 데이터를 `Asset` 객체로 정의 (단위 환산, 수익률 계산식 통일).
### B. Intelligence Pipeline
- `Input`: KIS API (잔고) + yfinance (실시간가) + Exa (리포트).
- `Think`: `Finance Crew`가 리스크와 기회비용을 4개 레이어로 분석.
- `Output`: [GEM: OMNI] 표준 리포트 양식 및 액션 가이드.

## 3. Implementation Steps (수정 단계)
1. **[Foundation]** `scripts/health_check.py`를 통해 현재 시스템 무결성 진단.
2. **[Logic]** `core/data_manager.py`를 정규화 모델 기반으로 업그레이드.
3. **[Brain]** `finance_crew.py`에 리서치된 리스크 엔진(4개 레이어) 이식.
4. **[Verify]** 통합 테스트 스크립트로 데이터 흐름 최종 검증.

## 4. Success Criteria (성공 기준)
- 모든 페이지에서 주가/환율 데이터가 1원 단위까지 일치함.
- AI 리포트에 "왜 이 종목을 사야/팔아야 하는지"에 대한 수치적 근거가 3개 이상 포함됨.
- 마스터님이 수동으로 코드를 디버깅할 필요가 전혀 없음.
