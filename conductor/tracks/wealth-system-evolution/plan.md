# Implementation Plan: WICC 4.0 Rebuild

## Phase 1: Data & Model Reconstruction (The Root)
- [ ] `core/models.py`: 거시 지표 및 프로필 필드 확장
- [ ] `core/data_manager.py`: Macro 데이터 수집 및 종목명 매핑 로직 구현
- [ ] `skills/gsheet_loader.py`: 계좌/분류 정보 로드 최적화
- [ ] **Audit**: `Pilot Audit` (Integrity Check) 실행

## Phase 2: Intelligence & Strategy (The Brain)
- [ ] `agents/crews/finance_crew.py`: 마스터 투자 헌장 주입 및 분석가 추가
- [ ] `skills/market_screener.py`: 섹터별 유망 종목 리서치 기능 강화
- [ ] **Audit**: AI 응답 정형화 테스트

## Phase 3: Interface Transformation (The Face)
- [ ] `pages/wealth_home.py`: 전면적인 레이아웃 및 UX 개편
- [ ] `pages/style_utils.py`: 가시성(색상, 단위) 개선
- [ ] **Audit**: 최종 실행 무결성 확인 및 ruff 정화

## Phase 4: Delivery
- [ ] 완성 보고 및 대시보드 시연 가이드 제출