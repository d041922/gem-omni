# [PRD] Finance Agent: The Wealth Commander (v2.0)

## 1. 개요 (Overview)
**Finance Agent**는 마스터의 자산 증식 속도(Velocity of Wealth)를 극대화하고, 불어난 자산을 만다라트의 다른 삶의 영역(관계, 건강 등)으로 적절히 배분하는 **Life-Centric Quant 에이전트**이다.

---

## 2. 💎 데이터 및 UX 표준 (Core Standards) - **CRITICAL**
본 에이전트의 모든 모듈은 다음의 '구글급' 엔지니어링 표준을 반드시 준수해야 한다.

### 2.1 Data Integrity (데이터 무결성)
- **Dynamic FX**: 환율 하드코딩은 절대 금지한다. 매 세션/동기화 시 `USDKRW=X` 실시간 데이터를 조회한다.
- **Precision Control**: 모든 수치 데이터는 저장 및 출력 시 **소수점 2자리**(`round(v, 2)`)로 제한하여 노이즈를 제거한다.
- **SSOT**: 모든 데이터는 `DataOrchestrator`를 거쳐 `world_state.json`에 기록된 값만 사용한다.

### 2.2 UX Localization (현지화 표준)
- **Korean Formatting**: 1억 원 이상의 큰 숫자는 한국 정서에 맞게 **'조, 억, 만'** 단위(예: ₩1조 2,300억)로 표기한다.
- **Currency Symbols**: 종목별 통화에 맞춰 `₩`(KRW), `$`(USD) 기호를 자동 구분하여 표시한다.
- **Localized Signals**: `Oversold` -> `🔵 과매도(저점)`와 같이 영문 퀀트 용어를 한글/배지 UI로 변환한다.

---

## 3. 핵심 기능 상세 (Key Features)

### 3.1 Data Orchestrator (The Vault)
- **Active Sync**: 구글 시트 원장과 실시간 시장가를 결합하여 `world_state.json`을 최신화한다.
- **Atomic Write**: 파일 손상 방지를 위해 임시 파일 생성 후 교체하는 원자적 쓰기 방식을 사용한다.

### 3.2 Advanced Quant Engine (The Hunter)
- **Factor Library**: Technical(RSI, MACD), Fundamental(PER, PBR), Flow(Vol Surge) 등 다각도 분석.
- **Normalization**: 데이터 일부 누락 시에도 가중치를 재분배하여 안정적인 스코어링 제공.

### 3.3 Intelligence Briefing (The Steward)
- **Step 1 (Current)**: 데이터 기반의 Rule-based 요약 브리핑.
- **Step 2 (Next)**: LLM이 `world_state.json`을 심층 분석하여 "지금 엔비디아를 팔아 선물 예산으로 옮기세요"와 같은 전략적 제안 수행.

---

## 4. 로드맵 및 진행 상황 (Roadmap)

### Phase 1: Foundation (Infra & UI) ✅ 완료
- [x] Data Orchestrator (SSOT & Real-time FX) 구현.
- [x] Mandalart Control Center UI (app.py) 리뉴얼.
- [x] Wealth Master Control UI (wealth_home.py) 구축.

### Phase 2: Intelligence (Analysis) 🚀 진행 중
- [ ] **Task 2.1**: `Market Screener` 지표 확장 (8대 핵심 지표 완비).
- [ ] **Task 2.2**: LLM 기반 심층 포트폴리오 분석 리포트 자동 생성.
- [ ] **Task 2.3**: 섹터 로테이션(Money Flow) 분석 엔진 탑재.

### Phase 3: Connect (Life Linking) 🔜 예정
- [ ] **Task 3.1**: 만다라트 영역별 예산 할당 및 지출 시뮬레이션.
- [ ] **Task 3.2**: 삶의 이벤트(생일, 여행 등)와 재정 데이터 연동.

---

## 5. 성공 지표 (Metrics)
- **Accuracy**: UI 표시 수치와 실제 자산 가치 오차 0.1% 미만.
- **Velocity**: 시장 지수(S&P 500) 대비 연간 5% 이상의 Alpha 달성 지원.
- **Satisfaction**: 마스터의 자산 현황 파악 시간이 일일 1분 이내로 단축.