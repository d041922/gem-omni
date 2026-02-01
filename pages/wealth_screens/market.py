import streamlit as st
from core.data_manager import DataManager
from pages.style_utils import metric_card

def render_market_screen():
    st.title("🌐 Market Intelligence")
    
    # 1. Market Overview Indices
    indices = DataManager.get_market_indices()
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        d = indices.get("S&P 500", {})
        metric_card("S&P 500", f"{d.get('value', 0):,.1f}", f"{d.get('change', 0):+.2f}%")
    with m2:
        d = indices.get("NASDAQ", {})
        metric_card("NASDAQ", f"{d.get('value', 0):,.1f}", f"{d.get('change', 0):+.2f}%")
    with m3:
        d = indices.get("KOSPI", {})
        metric_card("KOSPI", f"{d.get('value', 0):,.1f}", f"{d.get('change', 0):+.2f}%")
    with m4:
        d = indices.get("VIX", {})
        metric_card("VIX", f"{d.get('value', 0):.2f}", "Volatility")

    st.markdown("---")
    
    # 2. News and Trends
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("🔥 Market Hot News")
        st.info("실시간 시장 뉴스 수집 중...")
        
    with c2:
        st.subheader("📅 Earnings Calendar")
        st.info("이번 주 주요 실적 발표 예정 기업...")

def render_market_snapshot():
    """Simple widget for sidebar or home"""
    indices = DataManager.get_market_indices()
    for name, d in indices.items():
        st.sidebar.text(f"{name}: {d.get('value', 0):,.1f} ({d.get('change', 0):+.2f}%)")
