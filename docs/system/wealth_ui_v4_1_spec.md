# Design Doc: Wealth UI v4.1 (Refinement & Polish)

## 1. 개요 (Overview)
v4.0 배포 후 발견된 레이아웃 버그(빈 카드)를 수정하고, 마스터의 선호도에 맞춰 전략(Strategy) 시각화 방식을 도넛 차트로 통일한다.

## 2. 수정 명세 (Technical Fix)

### 2.1 빈 카드 제거 (Empty Section Cleanup)
- **Problem**: HTML 래퍼(`glass-card`)가 데이터 존재 여부와 관계없이 렌더링됨.
- **Solution**: Python 단에서 `if holdings:` 조건을 카드 렌더링 함수 전체에 적용하여 데이터 부재 시 섹션 자체를 숨김.

### 2.2 차트 시스템 재편 (Chart Harmonization)
- **Strategy Chart Update**:
    - **AS-IS**: 계좌별 Stacked Bar (가독성 저하).
    - **TO-BE**: **Tier Donut Chart** (Core/Scale/Option 비중).
    - **Layout**: 왼쪽(Account Donut) | 오른쪽(Tier Donut)으로 배치하여 포트폴리오의 양대 축을 한눈에 비교.

### 2.3 스크리너 요약 강화 (Screener Polish)
- 카드 내부의 불필요한 공백을 줄이고, 배지(Badge) 색상을 더 선명하게 조정.

## 3. 구현 규칙 (Rules)
- `pages/style_utils.py`는 현재 완벽하므로 수정하지 않는다.
- `pages/wealth_home.py`의 렌더링 로직만 원자적으로 수정한다.

## 4. 승인 요청
마스터, "도넛 차트의 통일감"과 "클린한 레이아웃"을 적용해도 되겠습니까?
