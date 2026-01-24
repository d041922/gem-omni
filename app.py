import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from core.memory import MemorySystem
from agents.portfolio_manager import PortfolioManager
from agents.finance import FinanceAgent

# --- 1. Page Config ---
st.set_page_config(page_title="GEM: OMNI Command Center", page_icon="💎", layout="wide", initial_sidebar_state="collapsed")

# --- 2. Custom CSS (Unified Professional Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0D1117; }
    div[data-testid="stMetric"] {
        background-color: #161B22; padding: 15px; border-radius: 10px; border: 1px solid #30363D;
    }
    .panel-header {
        font-size: 0.9rem; font-weight: 800; color: #8B949E; margin-bottom: 15px;
        text-transform: uppercase; letter-spacing: 1px; border-left: 3px solid #58A6FF; padding-left: 10px;
    }
    .ai-card {
        background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Init ---
if 'memory' not in st.session_state: st.session_state.memory = MemorySystem()
if 'pm' not in st.session_state: st.session_state.pm = PortfolioManager(st.session_state.memory)
if 'agent' not in st.session_state: st.session_state.agent = FinanceAgent(memory=st.session_state.memory)

# --- 4. Top Bar (Global Market Pulse) ---
st.markdown("<p class='panel-header'>Global Market Pulse</p>", unsafe_allow_html=True)
m1, m2, m3, m4, m5 = st.columns(5)
# (간소화를 위해 임시 수치, 추후 MarketAgent에서 실시간 수급)
m1.metric("USD/KRW", "1,450.2", "+2.5")
m2.metric("S&P 500", "5,842.1", "-0.2%")
m3.metric("Nasdaq", "18,520.4", "-0.8%")
m4.metric("VIX", "18.42", "Normal")
m5.metric("BTC", "$102,450", "+4.2%")

st.divider()

# --- 5. Main Content ---
profile = st.session_state.memory.user_profile
df = pd.DataFrame(profile.get('portfolio', []))

if not df.empty:
    col_health, col_intel, col_action = st.columns([0.25, 0.5, 0.25])

    # [좌측: Health]
    with col_health:
        st.markdown("<p class='panel-header'>🛡️ Portfolio Health</p>", unsafe_allow_html=True)
        if st.button("🔍 Run Full Audit", use_container_width=True):
            with st.spinner("Analyzing Team Report..."):
                report, risk_data = st.session_state.pm.get_full_command_report(st.session_state.agent)
                st.session_state.full_report = report
                st.session_state.risk_data = risk_data
        
        if 'risk_data' in st.session_state:
            rd = st.session_state.risk_data
            st.metric("Portfolio Beta", f"{rd.get('beta', 0):.2f}")
            st.progress(rd.get('risk_score', 0) / 100)
            st.caption(f"Risk Index: {rd.get('risk_score', 0)}/100")
            
            if rd.get('correlation') is not None:
                fig_corr = px.imshow(rd['correlation'], text_auto=".2f", color_continuous_scale="RdBu_r", aspect="auto")
                fig_corr.update_layout(height=300, margin=dict(t=0,b=0,l=0,r=0), showlegend=False)
                st.plotly_chart(fig_corr, use_container_width=True)

    # [중앙: Intelligence]
    with col_intel:
        st.markdown("<p class='panel-header'>🧠 AI Strategy Intelligence</p>", unsafe_allow_html=True)
        if 'full_report' in st.session_state:
            rep = st.session_state.full_report
            st.markdown(f"### {rep.headline}")
            st.info(f"**Verdict:** {rep.ai_verdict}")
            st.markdown(rep.summary)
            with st.expander("Detailed Risk Analysis"):
                st.write(rep.risk_analysis)
            
            # Allocation Chart
            fig_pie = px.pie(df, values='total_evaluation_value', names='category', hole=0.6)
            fig_pie.update_layout(height=300, margin=dict(t=30,b=0,l=0,r=0), template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("사령부 보고서를 생성하려면 좌측의 [Run Full Audit]을 클릭하십시오.")

    # [우측: Action]
    with col_action:
        st.markdown("<p class='panel-header'>🚀 Action Center</p>", unsafe_allow_html=True)
        if 'full_report' in st.session_state:
            rep = st.session_state.full_report
            for item in rep.action_plan:
                with st.container(border=True):
                    st.markdown(f"**{item.action} {item.ticker}** ({item.amount})")
                    st.caption(item.reason)
            
            st.markdown("---")
            st.markdown("**⚠️ Macro Alerts**")
            for alert in rep.macro_alerts:
                st.warning(alert)

    # --- 6. Bottom Table ---
    st.divider()
    st.markdown("<p class='panel-header'>📑 Asset Inventory</p>", unsafe_allow_html=True)
    
    gb = GridOptionsBuilder.from_dataframe(df[['name', 'ticker', 'amount', 'total_evaluation_value', 'profit_pct', 'category']])
    gb.configure_column("total_evaluation_value", header_name="VALUE (KRW)", valueFormatter="'₩' + x.toLocaleString()")
    
    jscode = JsCode("""
    function(params) {
        if (params.value > 0) { return {'color': '#3FB950', 'backgroundColor': 'rgba(63, 185, 80, 0.1)'}; }
        else if (params.value < 0) { return {'color': '#F85149', 'backgroundColor': 'rgba(248, 81, 73, 0.1)'}; }
        return null;
    }
    """)
    gb.configure_column("profit_pct", header_name="RETURN (%)", cellStyle=jscode)
    
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, theme='alpine', height=400, allow_unsafe_jscode=True)

else:
    st.warning("데이터가 없습니다. 사이드바에서 동기화를 진행하십시오.")
    if st.sidebar.button("🔄 First Sync"):
        st.session_state.pm.sync_all()
        st.rerun()
