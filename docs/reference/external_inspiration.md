# External Inspiration & Best Practices

본 문서는 외부 우수 사례(Prism Insight, Wikidocs 등)에서 영감을 얻은 기술적 포인트들을 정리한다.

## 1. Data Architecture
- **Separation of Concerns**: Crawler(수집), Processor(정제/가공), Orchestrator(공급)의 역할을 엄격히 분리한다.
- **Vector Search Ready**: 모든 텍스트 데이터(뉴스, 리포트)는 향후 RAG 적용을 위해 임베딩 친화적인 포맷으로 저장한다.

## 2. Quantitative Logic
- **Data Sanitization**: `NaN` 처리, 아웃라이어 제거 로직을 `Data Orchestrator`의 필수 단계로 포함한다.
- **Factor Pipeline**: `pandas-ta`를 활용하여 모멘텀, 변동성 지표를 표준화된 스키마로 생성한다.
- **Atomic File Replacement**: `os.replace`를 사용한 파일 쓰기 무결성 보장.

## 3. UI/UX Strategies
- **Delta-Centric Metrics**: 단순 수치보다 '전일 대비', '목표 대비' 변동폭(Delta)을 강조한다.
- **Mandalart Linkage**: 재정 수치가 만다라트의 다른 영역(관계, 즐거움)에 미치는 영향을 시각적으로 표현한다.
- **Dynamic Charting**: Plotly 기반의 인터랙티브 차트를 기본으로 한다.

## 4. References
- [Prism Insight GitHub](https://github.com/dragon1086/prism-insight)
- [금융 데이터 분석 Wikidocs](https://wikidocs.net/274803)
