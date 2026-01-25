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
    
                    # Prepare detailed holdings info for AI (전체 종목)
                    from skills.news_analyzer import get_analyst_ratings
                    holdings_detail = []
                    for _, row in result_df.iterrows():
                        name = row.get(name_col, 'N/A')
                        ticker = row.get('티커코드', row.get('종목코드', 'N/A'))
                        returns = row.get('수익률(%)', 0)
                        cost = row.get('매수금액(KRW)', 0)
                        value = row.get('평가금액(KRW)', 0)
                        profit = row.get('손익(KRW)', 0)
                        value_pct = (value / total_value * 100) if total_value > 0 else 0
                        qty = row.get('수량', 0)
                        avg_price = row.get('평균매수가', 0)
                        current_price = row.get('현재가', 0)
                        category = row.get('카테고리', 'N/A')
                        account = row.get('계좌', 'N/A')
                        
                        # Fetch upside (Analyst consensus)
                        ratings = get_analyst_ratings(ticker)
                        upside = ratings.get('upside_pct', 0) if (ratings and ratings.get('status') != 'error') else 0

                        holdings_detail.append({
                            "name": name,
                            "ticker": ticker,
                            "account": account,
                            "category": category,
                            "quantity": float(qty),
                            "avg_price": float(avg_price),
                            "current_price": float(current_price),
                            "cost_krw": float(cost),
                            "value_krw": float(value),
                            "profit_krw": float(profit),
                            "return_pct": float(returns or 0),
                            "portfolio_weight_pct": float(value_pct or 0),
                            "upside_pct": float(upside or 0)
                        })

                    holdings_text = '\n'.join([
                        f"- {h['name']} ({h['ticker']}) [{h['account']}]:\n"
                        f"  수익률 {h['return_pct']:.1f}%, 비중 {h['portfolio_weight_pct']:.1f}%, **상승여력 {h['upside_pct']:.1f}%**\n"
                        f"  평가 ₩{h['value_krw']/1e6:.1f}백만, 수량 {h['quantity']:.0f}주"
                        for h in holdings_detail
                    ])
    
                    # Calculate risk metrics
                    from skills.finance_core_lib import calculate_portfolio_risk_metrics
                    risk_metrics = calculate_portfolio_risk_metrics(result_df)
    
                    # Sector/Category analysis
                    sector_summary = ""
                    if '카테고리' in result_df.columns:
                        sector_dist = result_df.groupby('카테고리')['평가금액(KRW)'].sum()
                        sector_pct = (sector_dist / total_value * 100).round(1)
                        sector_summary = '\n'.join([f"- {cat}: {pct:.1f}%" for cat, pct in sector_pct.items()])
                    
                    # Account distribution
                    account_summary = ""
                    if '계좌' in result_df.columns:
                        account_dist = result_df.groupby('계좌')['평가금액(KRW)'].sum()
                        account_pct = (account_dist / total_value * 100).round(1)
                        account_summary = '\n'.join([f"- {acc}: {pct:.1f}%" for acc, pct in account_pct.items()])
    
                    # Core/Satellite 자동 분류 (통합 유틸리티 사용)
                    from skills.asset_classifier import AssetClassifier
                    import json

                    # USER_PROFILE의 전략 로드 (현재: balanced)
                    classifier = AssetClassifier(strategy='balanced')

                    core_value = 0
                    satellite_value = 0

                    for h in holdings_detail:
                        asset_type = classifier.classify(
                            h['ticker'],
                            h.get('category', ''),
                            h['name']
                        )
                        h['asset_type'] = asset_type

                        if asset_type == 'Core':
                            core_value += h['value_krw']
                        else:
                            satellite_value += h['value_krw']

                    core_pct = (core_value / total_value * 100) if total_value > 0 else 0
                    satellite_pct = (satellite_value / total_value * 100) if total_value > 0 else 0
    
                    # Load system prompt from file (for caching)
                    from pathlib import Path
                    prompt_file = Path(__file__).parent / ".claude" / "prompts" / "investment-analyst.md"

                    if prompt_file.exists():
                        with open(prompt_file, 'r', encoding='utf-8') as f:
                            system_prompt = f.read()
                    else:
                        system_prompt = "당신은 CFA 자격을 보유한 포트폴리오 매니저입니다."

                    # Load USER_PROFILE for context
                    user_profile_path = Path(__file__).parent / "USER_PROFILE.md"
                    user_profile_context = ""
                    if user_profile_path.exists():
                        with open(user_profile_path, 'r', encoding='utf-8') as f:
                            user_profile_context = f.read()

                    # Create detailed user prompt with FULL data
                    user_prompt = f"""# 포트폴리오 정밀 분석 요청

## 📊 전체 자산 현황
- 총 투자금: ₩{total_cost/1e8:.2f}억원
- 총 평가금액: ₩{total_value/1e8:.2f}억원
- 총 수익률: {return_pct:.2f}%
- Core 비중: {core_pct:.1f}% (목표 50-60%) / Satellite 비중: {satellite_pct:.1f}% (목표 40-50%)

## 🏦 계좌별 비중
{account_summary}

## 🔍 종목별 상세 현황 (수익률, 비중, 애널리스트 상승여력 포함)
{holdings_text}

## 📋 전략적 액션 제안 (반드시 포함할 내용)

1. **계좌별 전략**: 각 계좌(ISA, 연금, 일반 등)의 목적에 맞는 포지션 조정안
2. **Bottom-Up 종목 액션**: 
   - **추가 매수(Buy more)**: 상승여력은 높은데 비중이 적거나 단가가 매력적인 종목
   - **수익 실현(Sell/Rebalance)**: 수익률은 높으나 상승여력이 소진된 종목, 혹은 비중이 너무 커진 종목
   - **보유 지속(Hold)**: 추세가 견고하고 상승여력이 충분한 종목
3. **구체적 수치**: "X주 매도 후 Y종목으로 이동" 또는 "₩XXX만원 추가 투입" 등 실행 가능한 가이드

마스터를 위해 매우 정교하고 실행 가능한 분석을 한국어로 제공하세요."""

                    full_prompt = f"{system_prompt}\n\n# 사용자 투자 전략\n{user_profile_context}\n\n---\n\n{user_prompt}"
    
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
