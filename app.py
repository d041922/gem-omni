import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from core.memory import MemorySystem
from agents.crews.finance_crew import FinanceCrew
from pages.stock_analysis import render_stock_analysis_page
from skills.finance_tools import fetch_market_data
import yfinance as yf
from datetime import datetime, timedelta

# --- 1. Page Config ---
st.set_page_config(page_title="GEM: OMNI Command Center", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

# --- Authentication Logic ---
def check_password():
    """Returns True if the user had the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Show login form
    st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; padding-top: 50px; flex-direction: column;'>
            <h1 style='color: #58A6FF;'>💎 GEM: OMNI</h1>
            <p style='color: #8B949E;'>Master, please verify your identity.</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Check for both 'password' and 'APP_PASSWORD' (case-insensitive fallback)
            target_password = st.secrets.get("password") or st.secrets.get("APP_PASSWORD")
            
            if target_password is None:
                st.warning("Warning: Password key not found in secrets. Using default.")
                target_password = "admin1234"
            
            if password == str(target_password):
                st.session_state.authenticated = True
                st.success("Identity verified. Loading system...")
                st.rerun()
            else:
                st.error("Invalid password. Access denied.")
    
    return False

if not check_password():
    st.stop()  # Stop execution until authenticated

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
if 'memory' not in st.session_state:
    st.session_state.memory = MemorySystem()
if 'finance_crew' not in st.session_state:
    st.session_state.finance_crew = FinanceCrew(
        memory_system=st.session_state.memory,
        spreadsheet_name="GEM_Finance_Portfolio"
    )

# --- 3.6 Global Data Loading ---
from skills.portfolio_utils import load_portfolio_data
if 'calculated_portfolio' not in st.session_state:
    load_portfolio_data()

# --- 3.5 Sidebar Navigation ---
st.sidebar.title("💎 GEM: OMNI")
st.sidebar.markdown("---")

def clear_analysis_state():
    if 'current_stock_analysis' in st.session_state: del st.session_state.current_stock_analysis
    if 'ai_stock_analysis' in st.session_state: del st.session_state.ai_stock_analysis

page = st.sidebar.radio(
    "메뉴 선택",
    options=["🏠 홈 대시보드", "📊 포트폴리오 관리", "🌍 글로벌 시장 정보", "🔍 종목 심층 분석"],
    index=0,
    on_change=clear_analysis_state
)

st.sidebar.markdown("---")
st.sidebar.caption("토큰 최적화 AI 분석 엔진")
st.sidebar.caption("Powered by Gemini & CrewAI")

# --- 4. Top Bar (Global Market Pulse) ---

# --- 5. Page Router ---
if 'nav_target' in st.session_state:
    target = st.session_state.nav_target
    if target == "portfolio": page = "📊 포트폴리오 관리"
    elif target == "stock_analysis": page = "🔍 종목 심층 분석"
    elif target == "market": page = "🌍 글로벌 시장 정보"
    del st.session_state.nav_target

# Top bar render (Always show unless in Market page)
if page != "🌍 글로벌 시장 정보":
    market_data = fetch_market_data()
    st.session_state.market_data_cache = market_data # Cache for briefing engine
    st.markdown("<p class='panel-header'>🌍 Global Market Pulse</p>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    # S&P 500
    sp500 = market_data.get("S&P 500", {})
    m1.metric("S&P 500", f"{sp500.get('value', 0):,.1f}", f"{sp500.get('change', 0):+.2f}%")

    # NASDAQ
    nasdaq = market_data.get("NASDAQ", {})
    m2.metric("NASDAQ", f"{nasdaq.get('value', 0):,.1f}", f"{nasdaq.get('change', 0):+.2f}%")

    # KOSPI
    kospi = market_data.get("KOSPI", {})
    m3.metric("KOSPI", f"{kospi.get('value', 0):,.1f}", f"{kospi.get('change', 0):+.2f}%")

    # VIX
    vix = market_data.get("VIX", {})
    vix_val = vix.get('value', 0)
    st_v = "Low" if vix_val < 15 else "Normal" if vix_val < 25 else "High"
    m4.metric("VIX", f"{vix_val:.2f}", st_v, delta_color="off")

    st.divider()

# --- 5. Page Router ---
if page == "🏠 홈 대시보드":
    from pages.home import render_home_page
    render_home_page()

elif page == "🌍 글로벌 시장 정보":
    from pages.market_overview import render_market_overview_page
    render_market_overview_page()

elif page == "🔍 종목 심층 분석":
    render_stock_analysis_page()

else:
    # 📊 포트폴리오 관리
    from skills.portfolio_utils import load_portfolio_data
    df, _ = load_portfolio_data()
    
    if not df.empty:
        col_health, col_intel, col_action = st.columns([0.25, 0.5, 0.25])
    
        # [좌측: Health]
        with col_health:
            st.markdown("<p class='panel-header'>🛡️ Portfolio Health</p>", unsafe_allow_html=True)
            if st.button("🔍 Run AI Analysis", width="stretch", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
    
                try:
                    # Use already calculated data
                    result_df = st.session_state.calculated_portfolio
    
                    # Generate AI insights
                    status_text.info("⏳ Generating AI insights...")
                    progress_bar.progress(30)
    
                    # Get unified context from skills
                    from skills.portfolio_utils import get_full_portfolio_analysis_context
                    portfolio_context = get_full_portfolio_analysis_context()
    
                    from google import genai
                    import os
                    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
                    # Prepare prompt for deep analysis
                    prompt = f"""
                    You are a professional investment strategist (CIO level).
                    Analyze the following portfolio and provide strategic insights:
                    
                    {portfolio_context}
                    
                    Focus on:
                    1. Risk concentration
                    2. Performance attribution
                    3. Actionable rebalancing advice
                    4. Macro alignment
                    
                    Respond in Korean. Use markdown formatting.
                    """
                    
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-exp",
                        contents=prompt
                    )
                    
                    st.session_state.ai_insights = response.text
    
                    progress_bar.progress(100)
                    status_text.success("✅ AI Analysis completed!")
                    st.balloons()
    
                except Exception as e:
                    status_text.error(f"❌ Error: {str(e)}")
                    st.exception(e)
    
            # Display risk metrics
            st.divider()
            st.markdown("**📊 Risk Metrics**")
            if 'calculated_portfolio' in st.session_state:
                from skills.finance_core_lib import calculate_portfolio_risk_metrics
                risk_metrics = calculate_portfolio_risk_metrics(st.session_state.calculated_portfolio)
    
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("Max Position", f"{risk_metrics.get('max_position_pct', 0):.1f}%",
                             "⚠️ High" if risk_metrics.get('max_position_pct', 0) > 15 else "✅ OK")
                col_r2.metric("Top 3 Concentration", f"{risk_metrics.get('concentration_risk', 0):.1f}%",
                             "⚠️ High" if risk_metrics.get('concentration_risk', 0) > 40 else "✅ OK")
    
                st.metric("Portfolio Volatility", f"{risk_metrics.get('volatility', 0):.2f}%")
                st.caption(f"Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 0):.2f}")
    
        # [중앙: Intelligence]
        with col_intel:
            st.markdown("<p class='panel-header'>🧠 AI Insights</p>", unsafe_allow_html=True)
    
            # Summary metrics (always show from calculated data)
            if 'calculated_portfolio' in st.session_state:
                result_df = st.session_state.calculated_portfolio
    
                col1, col2, col3 = st.columns(3)
                total_cost = result_df['매수금액(KRW)'].sum()
                total_value = result_df['평가금액(KRW)'].sum()
                total_profit = result_df['손익(KRW)'].sum()
                return_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0
    
                col1.metric("Total Cost", f"₩{total_cost/1e8:.1f}억", f"{return_pct:.1f}%")
                col2.metric("Total Value", f"₩{total_value/1e8:.1f}억")
                col3.metric("Profit/Loss", f"₩{total_profit/1e6:.0f}백만")
    
            # AI insights (show only after button click)
            if 'ai_insights' in st.session_state:
                st.markdown("### 💡 AI Insights")
                st.markdown(st.session_state.ai_insights)
            else:
                st.info("👆 Click 'Run AI Analysis' to get AI-powered insights")
    
            # Charts with tabs
            st.divider()
            if 'calculated_portfolio' in st.session_state:
                result_df = st.session_state.calculated_portfolio

                # Calculate Core/Satellite classification (통합 유틸리티 사용)
                from skills.asset_classifier import AssetClassifier

                classifier_chart = AssetClassifier(strategy='balanced')

                result_df['asset_type'] = result_df.apply(
                    lambda row: classifier_chart.classify(
                        row.get('티커코드', row.get('종목코드', '')),
                        row.get('카테고리', ''),
                        row.get('종목명', '')
                    ), axis=1
                )

                # Create tabs for different charts
                chart_tabs = st.tabs(["📊 Core-Satellite", "🏦 계좌별", "📈 섹터별"])

                # Tab 1: Core vs Satellite
                with chart_tabs[0]:
                    cs_data = result_df.groupby('asset_type')['평가금액(KRW)'].sum().reset_index()
                    total_val = cs_data['평가금액(KRW)'].sum()
                    cs_data['비중%'] = (cs_data['평가금액(KRW)'] / total_val * 100).round(1)

                    fig_cs = go.Figure(data=[go.Pie(
                        labels=cs_data['asset_type'],
                        values=cs_data['평가금액(KRW)'],
                        hole=0.5,
                        marker=dict(colors=['#58A6FF', '#FF6B6B']),
                        text=cs_data['비중%'].apply(lambda x: f'{x:.1f}%'),
                        textposition='inside',
                        textinfo='label+text'
                    )])
                    fig_cs.update_layout(
                        title="Core vs Satellite 비중",
                        height=280,
                        margin=dict(t=40,b=0,l=0,r=0),
                        template="plotly_dark",
                        showlegend=False
                    )
                    st.plotly_chart(fig_cs, use_container_width=True)

                    # Show target vs actual
                    core_pct = cs_data[cs_data['asset_type'] == 'Core']['비중%'].values[0] if 'Core' in cs_data['asset_type'].values else 0
                    sat_pct = cs_data[cs_data['asset_type'] == 'Satellite']['비중%'].values[0] if 'Satellite' in cs_data['asset_type'].values else 0

                    col_cs1, col_cs2 = st.columns(2)
                    col_cs1.metric("Core", f"{core_pct:.1f}%",
                                  "✅ OK" if 50 <= core_pct <= 60 else "⚠️ 조정 필요")
                    col_cs2.metric("Satellite", f"{sat_pct:.1f}%",
                                  "✅ OK" if 40 <= sat_pct <= 50 else "⚠️ 조정 필요")
                    st.caption("목표: Core 50-60%, Satellite 40-50%")

                # Tab 2: By account
                with chart_tabs[1]:
                    if '계좌' in result_df.columns:
                        account_data = result_df.groupby('계좌')['평가금액(KRW)'].sum().reset_index()
                        account_data = account_data.sort_values('평가금액(KRW)', ascending=False)

                        fig_acc = go.Figure(data=[go.Bar(
                            x=account_data['계좌'],
                            y=account_data['평가금액(KRW)'] / 1e6,
                            marker_color='#58A6FF',
                            text=account_data['평가금액(KRW)'].apply(lambda x: f'₩{x/1e6:.0f}M'),
                            textposition='outside'
                        )])
                        fig_acc.update_layout(
                            title="계좌별 자산 분산",
                            yaxis_title="평가금액 (백만원)",
                            height=280,
                            template="plotly_dark",
                            margin=dict(t=40,b=20,l=0,r=0),
                            showlegend=False
                        )
                        st.plotly_chart(fig_acc, use_container_width=True)
                    else:
                        st.info("계좌 정보가 없습니다")

                # Tab 3: By sector
                with chart_tabs[2]:
                    if '카테고리' in result_df.columns:
                        sector_data = result_df.groupby('카테고리')['평가금액(KRW)'].sum().reset_index()
                        sector_data = sector_data.sort_values('평가금액(KRW)', ascending=True)

                        fig_sector = go.Figure(data=[go.Bar(
                            y=sector_data['카테고리'],
                            x=sector_data['평가금액(KRW)'] / 1e6,
                            orientation='h',
                            marker_color='#FF6B6B',
                            text=sector_data['평가금액(KRW)'].apply(lambda x: f'₩{x/1e6:.0f}M'),
                            textposition='outside'
                        )])
                        fig_sector.update_layout(
                            title="섹터별 자산 분산",
                            xaxis_title="평가금액 (백만원)",
                            height=280,
                            template="plotly_dark",
                            margin=dict(t=40,b=20,l=0,r=0),
                            showlegend=False
                        )
                        st.plotly_chart(fig_sector, use_container_width=True)
    
        # [우측: Quick Stats]
        with col_action:
            st.markdown("<p class='panel-header'>📊 Portfolio Summary</p>", unsafe_allow_html=True)
    
            total_positions = len(df)
            st.metric("Total Positions", total_positions)
    
            if '카테고리' in df.columns:
                categories = df['카테고리'].value_counts()
                st.markdown("**By Category:**")
                for cat, count in categories.items():
                    st.caption(f"• {cat}: {count} positions")
    
            st.divider()
            st.caption(f"💾 Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    
        # --- 6. Bottom Table ---
        st.divider()
        st.markdown("<p class='panel-header'>📑 Portfolio Holdings</p>", unsafe_allow_html=True)
    
        # Show calculated portfolio data
        if 'calculated_portfolio' in st.session_state:
            result_df = st.session_state.calculated_portfolio

            # Add asset_type if not present
            if 'asset_type' not in result_df.columns:
                from skills.asset_classifier import AssetClassifier
                classifier = AssetClassifier(strategy='balanced')
                result_df['asset_type'] = result_df.apply(
                    lambda row: classifier.classify(
                        row.get('티커코드', row.get('종목코드', '')),
                        row.get('카테고리', ''),
                        row.get('종목명', '')
                    ), axis=1
                )

            # Get available columns dynamically
            cols_to_show = []
            col_mapping = {
                '종목명': '종목명',
                '티커코드': '티커코드',
                'asset_type': '자산유형',
                '카테고리': '카테고리',
                '수량': '수량',
                '매수금액(KRW)': '매수금액(KRW)',
                '평가금액(KRW)': '평가금액(KRW)',
                '손익(KRW)': '손익(KRW)',
                '수익률(%)': '수익률(%)'
            }

            for col in col_mapping.keys():
                if col in result_df.columns:
                    cols_to_show.append(col)

            if cols_to_show:
                display_df = result_df[cols_to_show].copy()

                # Rename asset_type to Korean
                if 'asset_type' in display_df.columns:
                    display_df = display_df.rename(columns={'asset_type': '자산유형'})

                # Sort by return percentage (descending)
                if '수익률(%)' in display_df.columns:
                    # Sort before formatting
                    display_df = display_df.sort_values('수익률(%)', ascending=False)

                # Format currency columns
                for col in ['매수금액(KRW)', '평가금액(KRW)', '손익(KRW)']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"₩{x:,.0f}")

                if '수익률(%)' in display_df.columns:
                    display_df['수익률(%)'] = display_df['수익률(%)'].apply(lambda x: f"{x:.2f}%")

                st.dataframe(display_df, width="stretch", height=400)
            else:
                st.dataframe(result_df, width="stretch", height=400)
        else:
            # Fallback to raw data
            st.dataframe(df, width="stretch", height=400)
    
    else:
        st.warning("📊 No portfolio data loaded yet.")
        st.info("Click the button below to run your first analysis with FinanceCrew (CrewAI)")
    
        if st.button("🚀 Run First Analysis", width="stretch"):
            with st.spinner("Running FinanceCrew..."):
                result = st.session_state.finance_crew.generate_full_report()
    
                if result['success']:
                    st.success("✅ Analysis completed! Refresh page to view results.")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
