# System Spec: Wealth Master Control v4.0 (Bento & Glass Edition)

## 1. 디자인 컨셉 (Design Concept)
- **Style**: Glassmorphism (Deep Dark Theme)
- **Layout**: Bento Grid (Modular Information Architecture)
- **Colors**: 
    - Accent: `#3182F6` (OMNI Blue)
    - Profit: `#FF4B4B` (Dynamic Red)
    - Loss: `#1C7ED6` (Soft Blue)
    - Card BG: `rgba(22, 27, 34, 0.7)` with `backdrop-filter: blur(10px)`

## 2. 레이아웃 명세 (Bento Architecture)

### 2.1 [Row 1] Strategic Insight (Height: 150px)
- **Component**: AI Briefing Glass Card
- **Content**: 마스터를 위한 일일 자산 한마디 + 현금 비중 경고 배지.

### 2.2 [Row 2] Vital Metrics (3 Columns)
- **Card A**: Net Worth (Total Assets)
- **Card B**: Daily Performance (P/L with Sparkline)
- **Card C**: Mandalart Contribution (Goal Progress %)

### 2.3 [Row 3] Analysis Deep-Dive (Height: 500px)
- **Left (2/3)**: Tabbed Multi-Chart Container
    - Tab 1: **Account Donut** (계좌별 점유율)
    - Tab 2: **Strategy Stacked Bar** (계좌 내 티어 구성)
    - Tab 3: **Asset Treemap** (종목별 덩어리 확인)
- **Right (1/3)**: **Hot Momentum Badge List**
    - 스크리너 결과를 클릭 없이 한눈에 볼 수 있는 요약 카드 형태.

## 3. 기술적 구현 (Technical Implementation)
- **CSS**: `pages/style_utils.py` 내에 `.glass-card`, `.bento-grid` 클래스 정의.
- **Charts**: `plotly.graph_objects`를 사용하여 Streamlit 테마와 완벽 통합.
- **Micro-Interactions**: 호버 시 보더 라이트 효과 적용.

## 4. 검증 계획
- **Visual Audit**: 모든 해상도(Responsive)에서 Bento 그리드 유지 여부.
- **Data Integrity**: 차트 호버 시 실제 종목명과 금액이 일치하는지 확인.
