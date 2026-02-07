# [GEM: OMNI] - The Life Operating System
> **"Agent for the Happy Me (행복한 나를 위한 에이전트)"**

## 1. 프로젝트 비전 (Project Vision)
OMNI는 단순한 앱이 아닙니다. 마스터의 삶을 구성하는 8대 영역을 최적화하고 조율하여 **'행복한 나'**라는 궁극적 목표를 실현하는 **개인용 인공지능 운영체제(Life OS)**입니다.

우리는 **만다라트(Mandalart)** 구조를 통해 삶의 각 영역을 전문 에이전트가 관리하게 하며, 현재 그 첫 번째 기둥인 **[Finance: 재정]** 에이전트를 구축 중입니다.

상세 비전: `docs/planning/001_OMNI_VISION_MANDALART.md`

---

## 2. 핵심 모듈: Finance Agent (Wealth Commander)
재정 에이전트는 마스터의 경제적 자유를 지탱하는 두 개의 엔진으로 구성됩니다.

### 📈 The Quant Engine (퀀트 엔진)
- **Velocity of Wealth**: 기관 투자자 수준의 데이터 분석으로 자산 증식 속도를 극대화합니다.
- **Tools**: 실시간 마켓 스크리너, 섹터 로테이션 분석, 포트폴리오 최적화.

### 🏠 The Life Steward (라이프 집사)
- **Support for Happiness**: 불어난 자산을 삶의 다른 목표(건강, 관계, 즐거움)와 연결하여 최적의 예산을 제안합니다.

상세 기획: `docs/planning/002_FINANCE_AGENT_MASTER_PRD.md`

---

## 3. 엔지니어링 원칙 (Engineering Standards)
우리는 **Google Software Engineering (SwE) Principles**를 엄격히 준수합니다.

- **Design Before Code**: `Design Doc` 승인 없이 코드를 작성하지 않는다. (`rules/000`)
- **Single Source of Truth**: 모든 데이터는 `Data Orchestrator`를 통해서만 유통된다. (`rules/200`)
- **Test-Driven Confidence**: 테스트 코드가 없는 코드는 부서진 코드로 간주한다.
- **Deterministic Logic**: AI의 추론과 파이썬의 계산을 엄격히 분리한다.

---

## 4. 프로젝트 구조 (Project Structure)

```text
GEM_OMNI/
├── core/               # 시스템 헌법 및 최상위 제어 엔진
├── data/               # [State] 단일 진실 공급원 (SSOT) 및 로그
├── docs/               # [Design] PRD, Spec, Test Plan 저장소
├── pages/              # [UI] Streamlit 기반 인터페이스
├── rules/              # [Law] 구글 엔지니어링 표준 및 도메인 규약
├── scripts/            # 유틸리티 및 시스템 관리 도구
├── skills/             # [Tools] 순수 계산기(Calculator) 모음
├── tests/              # [Gate] 하드 게이트 (pytest)
├── app.py              # 시스템 엔트리 포인트
└── requirements.txt    # 의존성 패키지
```

---

## 5. 빠른 시작 (Quick Start)

### 1) 환경 구축
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2) 실행
```bash
streamlit run app.py
```

---

## 6. 개발 상태 (Current Status)
- [x] **Core Vision**: '행복한 나' 만다라트 체계 확립
- [x] **Infrastructure**: Google SwE 규칙 및 폴더 구조 정비
- [⏳] **Phase 1**: `Data Orchestrator` (SSOT) 설계 및 구현 중
- [ ] **Phase 2**: `Market Screener` & `Quant Engine` 개발 예정

---
**마지막 업데이트**: 2026-02-06
**상태**: Infra Refactoring & Phase 1 Development