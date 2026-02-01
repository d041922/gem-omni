"""
GEM: OMNI System Home - Mandalart UI Edition
The philosophy: "System revolves around Me."
Central Core: OMNI (User Status)
Surrounding Cells: Domains & Tools
"""
import streamlit as st
from datetime import datetime
from pages.style_utils import load_custom_css

# --- Page Config ---
st.set_page_config(
    page_title="GEM: OMNI",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded" # 사이드바를 기본으로 표시
)

# --- Initialize Session State ---
if "current_domain" not in st.session_state:
    st.session_state.current_domain = "home"

# --- Load Styles ---
load_custom_css()

# --- Helper: Navigation ---
def navigate_to(domain):
    st.session_state.current_domain = domain
    st.rerun()

# --- Sidebar: Admin Tools ---
with st.sidebar:
    st.title("💎 OMNI Center")
    st.divider()
    if st.button("🏠 OMNI Home", use_container_width=True):
        navigate_to("home")
    
    st.sidebar.markdown("<br><br>" * 5, unsafe_allow_html=True)
    st.sidebar.divider()
    st.sidebar.caption("Administrator Tools")
    if st.button("🚧 Dev-Construction Site", use_container_width=True, type="secondary"):
        navigate_to("dev_site")

# --- Custom Card Style for Mandalart ---
def mandalart_card(icon, title, desc, status="active", key=None, on_click=None):
    bg_color = "#1E2530" if status == "active" else "#161B22"
    border_color = "#3182F6" if status == "active" else "#30363D"
    opacity = "1.0" if status == "active" else "0.5"
    text_color = "#FFFFFF" if status == "active" else "#8B949E"
    
    st.markdown(f"""
    <div style='
        background-color: {bg_color};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 20px;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        opacity: {opacity};
    '>
        <div style='font-size: 2.5rem; margin-bottom: 10px;'>{icon}</div>
        <div style='font-size: 1.1rem; font-weight: bold; color: {text_color};'>{title}</div>
        <div style='font-size: 0.8rem; color: #8B949E; margin-top: 5px;'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if status == "active":
        st.button("Enter", key=key, on_click=on_click, use_container_width=True)
    else:
        st.button("Locked", key=key, disabled=True, use_container_width=True)

# --- Main Layout ---
def render_system_home():
    c1, c2 = st.columns([1, 1])
    with c1:
        st.caption("GEMINI: OMNI SYSTEM v2.1")
    with c2:
        st.markdown(f"<div style='text-align:right; color:#666;'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Mandalart Grid (3x3)
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        mandalart_card("🧠", "KNOWLEDGE", "Second Brain", "inactive", "btn_know")
    with r1c2:
        mandalart_card("💪", "HEALTH", "Bio & Fitness", "inactive", "btn_health")
    with r1c3:
        mandalart_card("📅", "SCHEDULE", "Calendar & Tasks", "inactive", "btn_sched")

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        def go_wealth():
            navigate_to("wealth")
        mandalart_card("💰", "WEALTH", "Asset Management", "active", "btn_wealth", on_click=go_wealth)
    with r2c2:
        st.markdown("<div style='text-align:center; padding: 20px; background: linear-gradient(135deg, #3182F6 0%, #00C6FF 100%); border-radius: 50%; width: 180px; height: 180px; margin: 0 auto; box-shadow: 0 0 30px rgba(49, 130, 246, 0.4); display: flex; flex-direction: column; justify-content: center; align-items: center;'><div style='font-size: 3rem;'>💎</div><div style='color: white; font-weight: bold; font-size: 1.2rem;'>OMNI</div></div>", unsafe_allow_html=True)
    with r2c3:
        mandalart_card("🤖", "AGENTS", "Crew Status", "inactive", "btn_agents")

    r3c1, r3c2, r3c3 = st.columns(3)
    with r3c1:
        mandalart_card("📝", "LOGS", "Daily Report", "inactive", "btn_logs")
    with r3c2:
        mandalart_card("⚙️", "SYSTEM", "Configuration", "active", "btn_settings")
    with r3c3:
        mandalart_card("🔄", "SYNC", "Data Refresh", "active", "btn_sync")

# --- Routing Logic ---
if st.session_state.current_domain == "home":
    render_system_home()
elif st.session_state.current_domain == "wealth":
    from pages.wealth_home import render_wealth_home
    render_wealth_home()
elif st.session_state.current_domain == "dev_site":
    from pages.dev_construction_site import render_construction_site
    render_construction_site()
else:
    st.error(f"Unknown Domain: {st.session_state.current_domain}")
    if st.button("Return to Home"):
        navigate_to("home")