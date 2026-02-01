"""
Market Overview Page [GEM: OMNI]
Global indices and market sentiment using Central Data Manager.
"""
import streamlit as st
from core.data_manager import DataManager
from pages.style_utils import load_custom_css, metric_card

def render_market_overview_page():
    load_custom_css()
    st.markdown("### 🌍 Global Market Intelligence")
    
    # Use DataManager instead of legacy finance_tools
    market_data = DataManager.get_market_indices()
    
    # Layout
    m1, m2, m3, m4 = st.columns(4)
    indices = [
        ("S&P 500", "top_sp_ov"),
        ("NASDAQ", "top_nas_ov"),
        ("KOSPI", "top_kos_ov"),
        ("VIX", "top_vix_ov")
    ]
    
    cols = [m1, m2, m3, m4]
    for i, (name, key) in enumerate(indices):
        data = market_data.get(name, {})
        with cols[i]:
            if name == "VIX":
                metric_card(name, f"{data.get('value', 0):.2f}", description="Volatility", key=key)
            else:
                metric_card(name, f"{data.get('value', 0):,.1f}", delta=f"{data.get('change', 0):+.2f}%", key=key)

    st.divider()
    st.info("💡 실시간 시장 데이터는 중앙 데이터 매니저를 통해 5분 간격으로 동기화됩니다.")