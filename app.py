"""
GEM: OMNI System Home - The Central Hub (v4.0)
The 4-Stage Finance Intelligence Funnel
"""
import streamlit as st
from dotenv import load_dotenv
from skills.data_orchestrator import DataOrchestrator
from pages.style_utils import load_custom_css

# --- Initialize ---
load_dotenv()
orchestrator = DataOrchestrator()

# --- Page Config ---
st.set_page_config(page_title="GEM: OMNI", page_icon="💎", layout="wide", initial_sidebar_state="expanded")
load_custom_css()

# --- Auto Sync Guard ---
try:
    if orchestrator.is_expired("portfolio", ttl_seconds=3600): # 1시간마다 자동 싱크
        orchestrator.sync_portfolio()
except Exception:
    pass

state = orchestrator.read_state()

# --- Formatters ---
def format_korean_currency(v: float) -> str:
    if v == 0:
        return "₩0"
    v_calc = abs(v)
    res = ""
    if v_calc >= 1e12:
        res += f"{int(v_calc // 1e12)}조 "
        v_calc %= 1e12
    if v_calc >= 1e8:
        res += f"{int(v_calc // 1e8)}억 "
        v_calc %= 1e8
    if v_calc >= 1e4:
        res += f"{int(v_calc // 1e4)}만"
    return f"₩{res.strip()}" if res else f"₩{abs(v):,.0f}"

# --- Navigation & Sidebar ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

with st.sidebar:
    st.title("💎 OMNI Center")
    st.divider()
    if st.button("🏠 전체 홈 (Dashboard)", use_container_width=True): 
        st.session_state.current_page = "home"
        st.rerun()
    if st.button("🌍 시장 현황 (Overview)", use_container_width=True):
        st.session_state.current_page = "market"
        st.rerun()
    if st.button("🎯 종목 발굴 (Screener)", use_container_width=True):
        st.session_state.current_page = "screener"
        st.rerun()
    if st.button("🔍 종목 분석 (Analysis)", use_container_width=True):
        st.session_state.current_page = "analysis"
        st.rerun()
    
    st.divider()
    if st.button("🔄 데이터 수동 동기화", use_container_width=True):
        with st.spinner("Syncing..."):
            orchestrator.sync_portfolio()
            st.rerun()

# --- Router ---
if st.session_state.current_page == "home":
    from pages.wealth_home import render_wealth_home
    render_wealth_home()
elif st.session_state.current_page == "market":
    from pages.market_overview import render_market_overview
    render_market_overview()
elif st.session_state.current_page == "screener":
    from pages.screener import render_screener
    render_screener()
elif st.session_state.current_page == "analysis":
    from pages.stock_analysis import render_stock_analysis
    render_stock_analysis()
else:
    st.error("페이지를 찾을 수 없습니다.")