import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.data_manager import DataManager
from pages.style_utils import load_custom_css, metric_card, format_krw

def render_wealth_home():
    """GEM: OMNI-Core [Wealth-Pilot 4.0]"""
    try:
        st.set_page_config(page_title="GEM: OMNI Wealth Pilot", layout="wide")
    except Exception:
        pass
        
    load_custom_css()

    # 1. Data Loading
    dm = DataManager()
    portfolio = dm.get_portfolio_data()
    macro = portfolio.macro
    df = pd.DataFrame(portfolio.holdings)

    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/diamond.png", width=60)
        st.title("GEM: OMNI")
        st.subheader("Wealth-Pilot v4.0")
        if st.button("🔄 Data Force Sync", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.divider()
        if st.button("🏠 Core Home", use_container_width=True):
            st.session_state.current_domain = "home"
            st.rerun()

    # --- SECTION A: MACRO COMMAND CENTER ---
    st.title("🏛️ Wealth Master Control")
    
    if macro:
        # 가독성을 높인 매크로 보드
        cols = st.columns(5)
        metrics = [
            ("USD/KRW", f"₩{macro.usd_krw:,.1f}", None),
            ("US 10Y Yield", f"{macro.us_10y_yield:.2f}%", None),
            ("NASDAQ", f"{macro.nasdaq_change:+.2f}%", "red" if macro.nasdaq_change > 0 else "blue"),
            ("VIX (Fear)", f"{macro.vix:.1f}", "blue" if macro.vix < 20 else "red"),
            ("Bitcoin", f"${macro.btc_price:,.0f}", None)
        ]
        for i, (label, val, color) in enumerate(metrics):
            with cols[i]:
                st.markdown(f"""
                <div style='text-align: center; background-color: #161B22; padding: 15px; border-radius: 15px; border: 1px solid #30363D;'>
                    <p style='color: #8B949E; font-size: 0.8rem; margin-bottom: 5px;'>{label}</p>
                    <h3 style='color: {"#F85149" if color=="red" else "#58A6FF" if color=="blue" else "#FFFFFF"}; margin: 0;'>{val}</h3>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()

    # --- SECTION B: AI STRATEGIC REPORT (Full-Width) ---
    st.markdown(f"""
    <div style="background-color: #161B22; padding: 25px; border-radius: 24px; border: 1px solid #3182F6; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(49, 130, 246, 0.1);">
        <div style="display:flex; align-items:center; margin-bottom:15px;">
            <span style="font-size:1.5rem; margin-right:10px;">🛡️</span>
            <span style="color: #3182F6; font-size: 1rem; font-weight: 800; letter-spacing: 1px;">WEALTH-PILOT INTELLIGENCE</span>
        </div>
        <p style="color: #E6EDF3; font-size: 1.25rem; line-height: 1.6; font-weight: 500;">{portfolio.daily_insight}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- SECTION C: PORTFOLIO PERFORMANCE ---
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("Net Worth", f"₩{format_krw(portfolio.total_net_worth_krw)}")
    with k2:
        perf_color = "red" if portfolio.profit_krw > 0 else "blue"
        metric_card("Total P/L", f"₩{format_krw(portfolio.profit_krw)}", delta=f"{portfolio.return_pct:+.2f}%", color=perf_color)
    with k3:
        metric_card("Liquidity", f"₩{format_krw(portfolio.cash_krw)}", delta=f"Ratio: {(portfolio.cash_krw/portfolio.total_net_worth_krw*100):.1f}%")
    with k4:
        progress = (portfolio.total_net_worth_krw / portfolio.goal_amount_krw) * 100
        metric_card("Mandalart Progress", f"{progress:.1f}%", delta=f"Target: {format_krw(portfolio.goal_amount_krw)}")

    # --- SECTION D: STRATEGIC MIX & OPPORTUNITIES ---
    st.divider()
    left_col, right_col = st.columns([1.6, 1])

    with left_col:
        st.subheader("📊 Strategic Asset Mix")
        if not df.empty:
            # 종목명이 있으면 종목명으로 표시
            df['display_name'] = df['종목명'].fillna(df['종목코드'])
            fig = go.Figure(data=[go.Pie(
                labels=df['display_name'], 
                values=df['평가금액(KRW)'], 
                hole=.6,
                textinfo='label+percent',
                marker=dict(colors=['#3182F6', '#00C6FF', '#50E3C2', '#B8E986', '#F5A623', '#D0021B'])
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#8B949E", size=12),
                margin=dict(t=0, b=0, l=0, r=0), height=450,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("⚡ Tactical Action Center")
        st.markdown("<div style='background-color:#161B22; border-radius:24px; padding:25px; border:1px solid #30363D;'>", unsafe_allow_html=True)
        if st.button("🚀 Execute AI Deep Audit", use_container_width=True, type="primary"):
            with st.spinner("Analyzing with Investment Charter..."):
                from agents.crews.finance_crew import run_portfolio_audit
                report = run_portfolio_audit(df, portfolio.cash_krw, {"macro": macro})
                st.markdown(f"<div style='background-color:#0D1117; padding:20px; border-radius:15px; margin-top:20px; border:1px solid #30363D; color:#E6EDF3;'>{report}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.subheader("🔍 Alpha Sector Hunter")
        from skills.market_screener import get_sector_hunter
        hunter = get_sector_hunter()
        opportunities = hunter.hunt_opportunities()
        for opp in opportunities:
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid #30363D;'>
                <div>
                    <span style='font-weight:bold; color:#FFFFFF; font-size:1.1rem;'>{opp['ticker']}</span><br>
                    <span style='color:#8B949E; font-size:0.8rem;'>{opp['sector']}</span>
                </div>
                <div style='text-align:right;'>
                    <span style='color:#3EAF7C; font-weight:bold; font-size:1.1rem;'>+{opp['weekly_change']}%</span><br>
                    <span style='color:#8B949E; font-size:0.8rem;'>${opp['price']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- SECTION E: MASTER INVENTORY (Clean Table) ---
    st.divider()
    st.subheader("📜 Master Asset Inventory")
    if not df.empty:
        # 가독성 극대화: 억/만 단위 적용 및 색상 입힘
        inventory_df = df[['종목명', '수량', '매수금액(KRW)', '평가금액(KRW)', '수익률(%)']].copy()
        
        def style_positive_negative(val):
            color = '#F85149' if val > 0 else '#58A6FF'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            inventory_df.style.format({
                '매수금액(KRW)': '{:,.0f}',
                '평가금액(KRW)': '{:,.0f}',
                '수익률(%)': '{:+.2f}%',
                '수량': '{:,.2f}'
            }).applymap(style_positive_negative, subset=['수익률(%)']),
            use_container_width=True, 
            hide_index=True
        )

if __name__ == "__main__":
    render_wealth_home()
