# Spec: Technical Chart Interpreter (v1.0)

## 1. 개요 (Overview)
`FactorEngine`이 산출한 수치형 데이터를 입력받아, 트레이더가 이해할 수 있는 자연어 진단 및 행동 가이드를 생성한다.

## 2. 해석 알고리즘 (Interpretation Rules)

### 2.1 추세 해석 (Trend Analysis)
- **Input**: MA Ribbon (MA5 ~ MA200)
- **Rules**:
    - `All Bullish` -> "🟢 **초강력 상승 추세** | 모든 이평선이 정배열 상태입니다. 조정 시 매수 관점이 유효합니다."
    - `Short Bullish (5,10,20) & Long Bearish (200)` -> "🟡 **단기 반등세** | 장기 하락 추세 속 기술적 반등 구간입니다. 저항선 돌파 여부를 확인하십시오."
    - `All Bearish` -> "🔴 **하락 추세 지속** | 역배열 상태가 심화되고 있습니다. 섣불리 바닥을 예단하지 마십시오."

### 2.2 위치 및 강도 해석 (Momentum Analysis)
- **Input**: RSI, Bollinger Bands, Pivot Points
- **Rules**:
    - `Price > Bollinger Upper` -> "⚠️ **과매수 경고** | 볼린저 밴드 상단을 돌파했습니다. 단기 차익 실현 매물이 출회될 수 있습니다."
    - `Price < Pivot S2` -> "📉 **낙폭 과대** | 2차 지지선까지 하향 돌파했습니다. 투매가 투매를 부르는 패닉 구간입니다."
    - `RSI > 50 & Rising` -> "📈 **모멘텀 강화** | 매수세가 매도세를 압도하며 상승 동력을 키우고 있습니다."

## 3. 구현 계획
- **`skills/chart_tools.py`** 내부에 `ChartInterpreter` 클래스 신설.
- **`pages/stock_analysis.py`**에서 `st.info` 대신 이 해석기의 출력을 강조 박스(Success/Warning/Error)로 표시.

## 4. 승인 요청
마스터, 위 규칙대로 차트를 '읽어주는' 기능을 탑재해도 되겠습니까?
