# Spec: Intelligence Upgrade (Real-time News & Quant Reports)

## 1. 개요 (Overview)
본 설계서는 OMNI 시스템에 실시간 시장 인텔리전스(Exa 기반 뉴스)와 종목별 심층 리서치 리포트 기능을 통합하기 위한 명세이다.

## 2. 실시간 뉴스 분석 (Market News Intelligence)
- **Module**: `skills/news_manager.py`
- **Data Source**: `exa.web_search_exa`
- **Search Query**: "current global stock market key events and economic indicators"
- **LLM Role**: 
    - 10개 이상의 뉴스 기사를 읽고 중복 제거.
    - 마스터의 포트폴리오 섹터와 관련된 뉴스 우선순위 배정.
    - 시장 심리(Sentiment)를 'Fear/Neutral/Greed'로 수치화.

## 3. 통합 리서치 리포트 (Unified Research Report)
- **Module**: `skills/research_engine.py`
- **Data Source**: `exa.company_research_exa` + `DataOrchestrator.read_state()`
- **Report Structure**:
    1. **Quant Snapshot**: RSI, Vol Surge, MA 추세 (from Orchestrator).
    2. **Business Context**: 주요 비즈니스 모델 및 최근 실적 요약 (from Exa).
    3. **AI Verdict**: 퀀트 점수와 뉴스를 종합한 최종 투자 의견.

## 4. 검증 계획 (Step 2 & 4)
- **UT-INT-01**: `exa` 검색 결과가 성공적으로 파이썬 객체로 변환되는지 확인.
- **UT-INT-02**: 퀀트 데이터와 뉴스 텍스트가 하나의 프롬프트에 정상 주입되는지 확인.

## 5. 배포 전략
- `Market Overview` 페이지에 뉴스 브리핑 우선 배포.
- `Stock Analysis` 페이지에 종목 리포트 버튼 배포.
