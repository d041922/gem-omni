import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from core.memory import MemorySystem
from agents.crews.finance_crew import FinanceCrew
from pages.stock_analysis import render_stock_analysis_page
from pages.settings import render_settings_page
import yfinance as yf
from datetime import datetime, timedelta

# --- 1. Page Config ---
st.set_page_config(page_title="GEM: OMNI Command Center", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

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

# --- 3.5 Sidebar Navigation ---
st.sidebar.title("💎 GEM: OMNI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    options=["📊 Portfolio Dashboard", "🔍 Stock Analysis", "⚙️ Settings"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.caption("Token-Optimized AI Analysis")
st.sidebar.caption("Powered by Gemini & CrewAI")

# --- 4. Top Bar (Global Market Pulse) ---
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_market_data():
    """Fetch real-time market data from yfinance"""
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "KOSPI": "^KS11",
        "VIX": "^VIX"
    }

    market_data = {}
    for name, ticker in indices.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='2d')

            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                change_pct = ((current - previous) / previous) * 100

                market_data[name] = {
                    'value': current,
                    'change': change_pct
                }
            else:
                market_data[name] = {'value': 0, 'change': 0}
        except:
            market_data[name] = {'value': 0, 'change': 0}

    return market_data

# Fetch market data
market_data = fetch_market_data()

# Market pulse banner
st.markdown("<p class='panel-header'>🌍 Global Market Pulse</p>", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)

# S&P 500
sp500 = market_data.get("S&P 500", {})
m1.metric(
    "S&P 500",
    f"{sp500.get('value', 0):,.1f}",
    f"{sp500.get('change', 0):+.2f}%",
    delta_color="normal"
)

# NASDAQ
nasdaq = market_data.get("NASDAQ", {})
m2.metric(
    "NASDAQ",
    f"{nasdaq.get('value', 0):,.1f}",
    f"{nasdaq.get('change', 0):+.2f}%",
    delta_color="normal"
)

# KOSPI
kospi = market_data.get("KOSPI", {})
m3.metric(
    "KOSPI",
    f"{kospi.get('value', 0):,.1f}",
    f"{kospi.get('change', 0):+.2f}%",
    delta_color="normal"
)

# VIX (Volatility Index)
vix = market_data.get("VIX", {})
vix_value = vix.get('value', 0)
vix_status = "Low" if vix_value < 15 else "Normal" if vix_value < 25 else "High"
m4.metric(
    "VIX",
    f"{vix_value:.2f}",
    vix_status,
    delta_color="off"
)

# Market summary message
avg_change = (sp500.get('change', 0) + nasdaq.get('change', 0) + kospi.get('change', 0)) / 3
if avg_change > 1:
    market_mood = "📈 시장 강세 - 위험자산 선호"
elif avg_change > 0:
    market_mood = "➡️ 시장 안정 - 완만한 상승"
elif avg_change > -1:
    market_mood = "↘️ 시장 약세 - 조정 국면"
else:
    market_mood = "📉 시장 하락 - 리스크 회피"

st.caption(f"**시장 상황**: {market_mood} | 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

st.divider()

# --- 5. Page Router ---
if page == "🔍 Stock Analysis":
    render_stock_analysis_page()

elif page == "⚙️ Settings":
    render_settings_page()

else:
    # Render Portfolio Dashboard (Default)
    # --- 5. Main Content ---
    # Load real data from Google Sheets and auto-calculate metrics
    try:
        from skills.gsheet_loader import load_data_from_gsheet
        portfolio_df, watchlist_df, cash_df = load_data_from_gsheet("GEM_Finance_Portfolio")
    
        # Store raw data in session state
        if 'raw_portfolio_df' not in st.session_state:
            st.session_state.raw_portfolio_df = portfolio_df
    
        # Auto-calculate metrics on load (only once per session)
        if 'calculated_portfolio' not in st.session_state:
            with st.spinner("⏳ Loading portfolio and calculating metrics..."):
                import yfinance as yf
                from skills.finance_core_lib import calculate_portfolio_metrics
    
                current_prices = {}
                ticker_col = '종목코드'
    
                if ticker_col in portfolio_df.columns:
                    tickers = portfolio_df[ticker_col].dropna().unique()
                    for ticker in tickers:
                        try:
                            stock = yf.Ticker(str(ticker))
                            hist = stock.history(period='1d')
                            if not hist.empty:
                                price = hist['Close'].iloc[-1]
                                current_prices[ticker] = float(price)
                        except:
                            pass
    
                # Calculate and store
                calculated_df = calculate_portfolio_metrics(portfolio_df, current_prices, 1450)
                st.session_state.calculated_portfolio = calculated_df
                st.session_state.current_prices = current_prices
    
        # Use calculated data
        df = st.session_state.calculated_portfolio
    
    except Exception as e:
        st.error(f"Failed to load Google Sheets data: {e}")
        profile = st.session_state.memory.user_profile
        df = pd.DataFrame(profile.get('portfolio', []))
    
    if not df.empty:
        col_health, col_intel, col_action = st.columns([0.25, 0.5, 0.25])
    
        # [좌측: Health]
        with col_health:
            st.markdown("<p class='panel-header'>🛡️ Portfolio Health</p>", unsafe_allow_html=True)
            if st.button("🔍 Run AI Analysis", use_container_width=True, type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
    
                try:
                    # Use already calculated data
                    result_df = st.session_state.calculated_portfolio
    
                    # Generate AI insights
                    status_text.info("⏳ Generating AI insights...")
                    progress_bar.progress(30)
    
                    from google import genai
                    import os
                    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
                    # Prepare portfolio summary
                    total_cost = result_df['매수금액(KRW)'].sum()
                    total_value = result_df['평가금액(KRW)'].sum()
                    total_profit = result_df['손익(KRW)'].sum()
                    return_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0
    
                    # Top performers
                    top_3 = result_df.nlargest(3, '수익률(%)')
                    bottom_3 = result_df.nsmallest(3, '수익률(%)')
    
                    name_col = '종목명' if '종목명' in result_df.columns else 'name'
                    top_performers = '\n'.join([f"- {row[name_col]}: {row['수익률(%)']:.1f}%" for _, row in top_3.iterrows()])
                    bottom_performers = '\n'.join([f"- {row[name_col]}: {row['수익률(%)']:.1f}%" for _, row in bottom_3.iterrows()])
    
                    # Prepare detailed holdings info for AI
                    holdings_detail = []
                    for _, row in result_df.iterrows():
                        name = row.get(name_col, 'N/A')
                        ticker = row.get('티커코드', row.get('종목코드', 'N/A'))
                        returns = row.get('수익률(%)', 0)
                        cost = row.get('매수금액(KRW)', 0)
                        profit = row.get('손익(KRW)', 0)
                        holdings_detail.append(f"- {name} ({ticker}): 수익률 {returns:.1f}%, 투자금 ₩{cost/1e6:.1f}백만, 손익 ₩{profit/1e6:.1f}백만")
    
                    holdings_text = '\n'.join(holdings_detail[:10])  # Top 10 for context
    
                    # Calculate risk metrics
                    from skills.finance_core_lib import calculate_portfolio_risk_metrics
                    risk_metrics = calculate_portfolio_risk_metrics(result_df)
    
                    # Sector/Category analysis
                    sector_summary = ""
                    if '카테고리' in result_df.columns:
                        sector_dist = result_df.groupby('카테고리')['평가금액(KRW)'].sum()
                        sector_pct = (sector_dist / total_value * 100).round(1)
                        sector_summary = '\n'.join([f"- {cat}: {pct:.1f}%" for cat, pct in sector_pct.items()])
    
                    # Save portfolio snapshot to file (token optimization)
                    import json
                    import tempfile
                    snapshot_data = {
                        "summary": {
                            "total_positions": len(result_df),
                            "total_cost": float(total_cost),
                            "total_value": float(total_value),
                            "total_return_pct": float(return_pct)
                        },
                        "risk_metrics": {
                            "max_position_pct": float(risk_metrics.get('max_position_pct', 0)),
                            "concentration_risk": float(risk_metrics.get('concentration_risk', 0)),
                            "volatility": float(risk_metrics.get('volatility', 0))
                        },
                        "sectors": sector_summary,
                        "top_holdings": holdings_text.split('\n')[:5]  # Top 5 only
                    }
    
                    snapshot_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8')
                    json.dump(snapshot_data, snapshot_file, ensure_ascii=False, indent=2)
                    snapshot_file.close()
    
                    # Load system prompt from file (for caching)
                    from pathlib import Path
                    prompt_file = Path(__file__).parent / ".claude" / "prompts" / "investment-analyst.md"
    
                    if prompt_file.exists():
                        with open(prompt_file, 'r', encoding='utf-8') as f:
                            system_prompt = f.read()
                    else:
                        system_prompt = "당신은 CFA 자격을 보유한 포트폴리오 매니저입니다."
    
                    # Replace placeholders
                    system_prompt = system_prompt.replace('[DATA_FILE_PATH]', snapshot_file.name)
    
                    # Create concise user prompt (< 500 tokens)
                    user_prompt = f"""포트폴리오 데이터 파일: {snapshot_file.name}
    
    ## 요약 정보
    - 총 종목: {len(result_df)}개
    - 총 수익률: {return_pct:.2f}%
    - 최대 종목 비중: {risk_metrics.get('max_position_pct', 0):.1f}%
    - 상위 3종목 집중도: {risk_metrics.get('concentration_risk', 0):.1f}%
    
    ## 분석 요청
    위 데이터를 바탕으로 다음을 제공하세요:
    1. Top-Down 평가 (2-3문장)
    2. Bottom-Up 실행 액션 (최대 3개, 종목명+금액+조건 필수)
    3. 리밸런싱 제안 (구체적 금액 명시)
    
    500자 이내, 실행 가능한 내용만."""
    
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=full_prompt
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
    
            # Charts
            st.divider()
            if 'calculated_portfolio' in st.session_state:
                result_df = st.session_state.calculated_portfolio

                # Sector pie chart
                if '카테고리' in result_df.columns:
                    sector_data = result_df.groupby('카테고리')['평가금액(KRW)'].sum().reset_index()
                    fig_pie = px.pie(sector_data, names='카테고리', values='평가금액(KRW)',
                                    title="섹터 분산", hole=0.5)
                    fig_pie.update_layout(height=280, margin=dict(t=40,b=0,l=0,r=0), template="plotly_dark")
                    st.plotly_chart(fig_pie, use_container_width=True)

                # Top 10 bar chart
                if '종목명' in result_df.columns:
                    top_10 = result_df.nlargest(10, '평가금액(KRW)')
                    colors = ['#FF6B6B' if x < 0 else '#4ECDC4' for x in top_10.get('수익률(%)', [0]*len(top_10))]
                    fig_bar = go.Figure(go.Bar(x=top_10['종목명'], y=top_10['평가금액(KRW)']/1e6,
                                              marker_color=colors,
                                              text=[f"{x:.1f}%" for x in top_10.get('수익률(%)', [0]*len(top_10))],
                                              textposition='outside'))
                    fig_bar.update_layout(title="Top 10 종목", yaxis_title="백만원",
                                         height=280, template="plotly_dark",
                                         margin=dict(t=40,b=0,l=0,r=0), showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
    
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
    
            # Get available columns dynamically
            cols_to_show = []
            col_mapping = {
                '종목명': '종목명',
                '티커코드': '티커코드',
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
    
                # Format currency columns
                for col in ['매수금액(KRW)', '평가금액(KRW)', '손익(KRW)']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"₩{x:,.0f}")
    
                if '수익률(%)' in display_df.columns:
                    display_df['수익률(%)'] = display_df['수익률(%)'].apply(lambda x: f"{x:.2f}%")
    
                st.dataframe(display_df, use_container_width=True, height=400)
            else:
                st.dataframe(result_df, use_container_width=True, height=400)
        else:
            # Fallback to raw data
            st.dataframe(df, use_container_width=True, height=400)
    
    else:
        st.warning("📊 No portfolio data loaded yet.")
        st.info("Click the button below to run your first analysis with FinanceCrew (CrewAI)")
    
        if st.button("🚀 Run First Analysis", use_container_width=True):
            with st.spinner("Running FinanceCrew..."):
                result = st.session_state.finance_crew.generate_full_report()
    
                if result['success']:
                    st.success("✅ Analysis completed! Refresh page to view results.")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
