# Spec: OMNI Reporting Engine (v1.0)

## 1. 개요 (Overview)
마스터의 자산 현황 및 종목 분석 결과를 전문가급 PDF 리포트로 자동 생성하여 의사결정을 지원한다. `Prism Insight`의 템플릿 엔진 로직을 경량화하여 이식한다.

## 2. 핵심 컴포넌트 (Components)

### 2.1 Report Template (`skills/templates/`)
- **Format**: Jinja2 Markdown Template.
- **Sections**:
    - **Header**: 마스터 인사말 및 리포트 생성 시각.
    - **Quant Score**: OMNI Score 및 팩터 상세 (RSI, Vol Surge 등).
    - **Market Context**: 최근 관련 뉴스 및 시장 심리.
    - **AI Verdict**: 최종 투자 가이드.

### 2.2 Reporting Engine (`skills/reporting_engine.py`)
- **`generate_report(data: dict) -> str`**: 데이터를 받아 Markdown 텍스트 생성.
- **`export_to_pdf(md_text: str) -> bytes`**: Markdown을 PDF 바이너리로 변환.

## 3. 기술 스택
- **Template**: `Jinja2`
- **Conversion**: `markdown-pdf` (Lightweight & Pure Python)
- **Interface**: Streamlit `st.download_button`

## 4. 검증 시나리오
- **UT-REP-01**: Jinja2 템플릿에 데이터가 누락 없이 주입되는지 확인.
- **UT-REP-02**: 결과물이 유효한 PDF 매직 넘버(`%PDF-`)를 포함하는지 확인.

## 5. 승인 요청
마스터, 위 설계대로 '종목 분석 리포트' 기능을 구축해도 되겠습니까?
