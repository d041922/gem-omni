# Spec: Market Screener Optimization & UI Tab Recovery (v3.2)

## 1. 개요 (Overview)
본 설계서는 스크리너의 속도를 혁신적으로 개선하고, 손실된 대시보드의 다차원 분석(Tabs) 기능을 완벽하게 복구하는 것을 목표로 한다.

## 2. 기술 명세 (Technical Spec)

### 2.1 Market Screener (Optimization)
- **Constraint**: `yf.Ticker.info` 사용을 전면 중단한다.
- **Implementation**:
    - `price`, `prev_close`, `market_cap` 등은 `yf.Ticker.fast_info` 속성으로 직접 접근한다.
    - `rsi`, `ma` 계산을 위한 시계열 데이터는 `history(period="60d")`를 사용한다.
    - `eps_growth` 등 `fast_info`에 없는 팩터는 **'Optional'**로 처리하며, 데이터 부재 시 가중치 재분배(Normalization) 로직을 활성화한다.

### 2.2 Wealth Home UI (Tab Recovery)
- **Goal**: [계좌], [티어], [종목] 3개 관점의 시각화 복구.
- **Structure**:
    - **Tab 1 (계좌별)**: `px.sunburst(path=['account', 'tier', 'name'])`
    - **Tab 2 (전략별)**: `px.sunburst(path=['tier', 'account', 'name'])`
    - **Tab 3 (자산별)**: `px.treemap(path=['name'])`
- **Utility**: `format_korean_currency` 함수를 `pages/style_utils.py`로 이동하여 공용화한다.

## 3. 테스트 시나리오 (Verification)
- **Test-Screener-Speed**: 5개 종목 스크리닝이 2초 이내 완료되는지 확인.
- **Test-UI-Consistency**: 3개 탭이 정상적으로 생성되고 각기 다른 차트 객체를 포함하는지 확인.

## 4. 승인 요청
마스터, 위 설계대로 진행하여 시스템의 성능과 UX를 동시에 회복해도 되겠습니까?