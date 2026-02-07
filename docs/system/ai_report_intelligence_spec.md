# Spec: AI Research Report Intelligence Augmentation (v1.3)

## 1. 개요 (Overview)
종목 분석 리포트(PDF)가 수집된 모든 기술적/기본적 지표를 유기적으로 해석하여, 마스터에게 '상황 인지적(Situation-Aware)' 투자 전략을 제안하도록 보강한다.

## 2. 지능형 해석 로직 (Inference Logic)

### 2.1 기술적 상황 판단 (Technical Context)
- **Support Awareness**: `Current Price <= S1` (1차 지지선 근접) 시 "하방 경직성 확보 및 반등 기대 구간" 텍스트 자동 생성.
- **Resistance Warning**: `Current Price >= R1` (1차 저항선 근접) 시 "단기 고점 매물대 소화 필요" 경고 주입.
- **Trend Alignment**: MA5, 10, 20이 모두 `Bullish`일 경우 "단기 정배열 진입으로 공격적 매수 가능" 판정.

### 2.2 전략적 결합 (Strategic Unification)
- **Verdict Mapping**:
    - (Score >= 80) + (MA Ribbon 4개 이상 Bullish) -> **"STRONG BUY (추세 추종)"**
    - (Score <= 40) + (Price < S2) -> **"BUY THE DIP (낙폭 과대)"**
    - 그 외 상황에 맞는 맞춤형 'Action Plan' 문장 템플릿 10종 구축.

## 3. 구현 태스크 (Implementation Tasks)
- **Task 1**: `ResearchEngine._generate_dynamic_summary`에 기술 분석 데이터 반영 로직 추가.
- **Task 2**: `pages/stock_analysis.py`에서 리포트 생성 시 Pivot/MA 데이터를 함께 전달하도록 수정.

## 4. 승인 요청
마스터, 리포트가 '맥락'을 이해하게 만드는 이 설계를 승인하시겠습니까?
