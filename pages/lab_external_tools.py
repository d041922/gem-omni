"""
Lab: External Tools Integration
Leveraging TradingView Widgets for professional-grade visualization and data.
This page relies on external iframes, reducing code complexity and bugs.
"""
import streamlit as st
import streamlit.components.v1 as components

def render_lab_page():
    st.set_page_config(layout="wide") # Force wide layout for charts
    
    st.markdown("### 🧪 실험실: TradingView & External Tools")
    st.caption("외부 전문 도구(TradingView)를 직접 연결하여 데이터 신뢰도와 시각화 품질을 극대화합니다.")

    # --- Sidebar Inputs ---
    with st.sidebar:
        st.header("설정")
        symbol = st.text_input("티커 입력 (예: AAPL, KRWUSD, BTCUSD)", value="NASDAQ:AAPL").upper()
        theme = st.selectbox("테마", ["dark", "light"], index=0)
        
        st.info("""
        **팁:** 
        - 한국 주식: `KRX:005930` (삼성전자)
        - 미국 주식: `NASDAQ:AAPL`
        - 코인: `BINANCE:BTCUSD`
        - 환율: `FX_IDC:USDKRW`
        """)

    # Layout: Chart (Top)
    st.markdown("#### 1. Advanced Real-time Chart")
    
    # TradingView Advanced Chart Widget
    chart_code = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
      {{
      "width": "100%",
      "height": "600",
      "symbol": "{symbol}",
      "interval": "D",
      "timezone": "Asia/Seoul",
      "theme": "{theme}",
      "style": "1",
      "locale": "kr",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "calendar": false,
      "support_host": "https://www.tradingview.com"
    }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(chart_code, height=600)

    st.divider()

    # Layout: Technicals & Fundamentals (Bottom)
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("#### 2. Technical Analysis (Gauge)")
        # Technical Analysis Widget
        tech_code = f"""
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
          {{
          "interval": "1m",
          "width": "100%",
          "isTransparent": false,
          "height": "450",
          "symbol": "{symbol}",
          "showIntervalTabs": true,
          "displayMode": "single",
          "locale": "kr",
          "colorTheme": "{theme}"
        }}
          </script>
        </div>
        <!-- TradingView Widget END -->
        """
        components.html(tech_code, height=450)

    with c2:
        st.markdown("#### 3. Company Profile & News")
        # Company Profile Widget
        profile_code = f"""
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-profile.js" async>
          {{
          "width": "100%",
          "height": "450",
          "colorTheme": "{theme}",
          "isTransparent": false,
          "symbol": "{symbol}",
          "locale": "kr"
        }}
          </script>
        </div>
        <!-- TradingView Widget END -->
        """
        components.html(profile_code, height=450)

    st.divider()
    
    st.markdown("#### 4. Real-time Market News")
    # Timeline Widget
    news_code = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
      {{
      "feedMode": "symbol",
      "symbol": "{symbol}",
      "colorTheme": "{theme}",
      "isTransparent": false,
      "displayMode": "regular",
      "width": "100%",
      "height": "400",
      "locale": "kr"
    }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(news_code, height=400)

if __name__ == "__main__":
    render_lab_page()
