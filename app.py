import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from core.memory import MemorySystem
from agents.crews.finance_crew import FinanceCrew
from pages.stock_analysis import render_stock_analysis_page
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
    options=["🏠 Home", "📊 Portfolio Dashboard", "🌍 시장 정보", "🔍 Stock Analysis"],
    index=0  # Default to Home
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
# Handle navigation from quick actions
if 'nav_target' in st.session_state:
    target = st.session_state.nav_target
    if target == "portfolio":
        page = "📊 Portfolio Dashboard"
    elif target == "stock_analysis":
        page = "🔍 Stock Analysis"
    elif target == "market":
        page = "🌍 시장 정보"
    del st.session_state.nav_target

if page == "🏠 Home":
    # Render Home Page
    from pages.home import render_home_page
    render_home_page()

elif page == "🌍 시장 정보":
    # Render Market Overview Page
    from pages.market_overview import render_market_overview_page
    render_market_overview_page()

elif page == "🔍 Stock Analysis":
    render_stock_analysis_page()

else:
    # Render Portfolio Dashboard
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
                            "return_pct": float(returns),
                            "portfolio_weight_pct": float(value_pct)
                        })

                    holdings_text = '\n'.join([
                        f"- {h['name']} ({h['ticker']}) [{h['account']}]:\n"
                        f"  비중 {h['portfolio_weight_pct']:.1f}%, 수익률 {h['return_pct']:.1f}%, "
                        f"수량 {h['quantity']:.0f}주, 평가 ₩{h['value_krw']/1e6:.1f}백만"
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
                    user_prompt = f"""# 포트폴리오 분석 요청

## 📊 포트폴리오 요약
- 총 종목: {len(result_df)}개
- 총 투자금: ₩{total_cost/1e8:.2f}억원
- 총 평가금액: ₩{total_value/1e8:.2f}억원
- 총 수익률: {return_pct:.2f}%
- **Core 비중: {core_pct:.1f}%** (목표: 50-60%)
- **Satellite 비중: {satellite_pct:.1f}%** (목표: 40-50%)

## 🏦 계좌별 & 종목별 상세 내역

{holdings_text}

## 📈 섹터 분산
{sector_summary}

## ⚠️ 리스크 지표
- 최대 종목 비중: {risk_metrics.get('max_position_pct', 0):.1f}%
- 상위 3종목 집중도: {risk_metrics.get('concentration_risk', 0):.1f}%
- 포트폴리오 변동성: {risk_metrics.get('volatility', 0):.2f}%

## 🚀 신규 성장 섹터 고려사항
다음 섹터들이 포트폴리오에 반영되어 있는지 확인:
1. **AI/반도체** (20-25%): 데이터센터, AI 칩셋 - NVDA, AMD, TSM
2. **바이오/헬스케어** (5-10%): 유전자 편집, 면역치료 - CRSP, EDIT, VRTX
3. **로봇/자동화** (5-10%): 산업용 로봇, AI 로보틱스 - BOTZ, TSLA, ABB
4. **전력/에너지** (5-10%): 신재생 에너지, 태양광, 풍력 - ENPH, FSLR, NEE
5. **한국 성장주** (5-10%): 반도체, 2차전지 - 삼성전자, SK하이닉스

위 섹터 중 누락되거나 과소평가된 부분이 있다면, **구체적 추천 종목과 매수 타이밍**을 제시하세요.

## 📋 분석 요청
위 **실제 데이터**를 바탕으로 다음을 제공하세요:

1. **Core-Satellite 균형 평가**:
   - 현재 Core {core_pct:.1f}%, Satellite {satellite_pct:.1f}%가 목표 범위(50-60% / 40-50%)에 있는지
   - 리밸런싱 필요 여부

2. **Bottom-Up 실행 액션** (최대 3개):
   - **계좌명 필수**: "ISA 계좌" / "연금저축" / "IRP" 등
   - **정확한 티커와 종목명**: 예) "NVDA (엔비디아)"
   - **구체적 금액과 수량**: 예) "₩855만원 (약 50주)" 또는 "보유량의 50%"
   - **Core/Satellite 분류**: 각 종목의 자산 분류 명시
   - **근거**: 단순 "비중 초과"가 아닌, **펀더멘털/성장성/추세** 기반 판단
   - **중요**: 좋은 Satellite 종목(AI 성장 스토리, 강한 추세)은 비중이 높아도 보유 유지 가능

3. **리밸런싱 제안**:
   - Satellite 익절 → Core 이동 시나리오 (구체적 금액)
   - 또는 Core 추가 매수 방안

**중요 원칙**:
- 비중 초과는 경고일 뿐, 매도 근거가 아님
- Satellite는 초과 수익 알파를 내야 하므로, 성장성 좋은 종목은 집중 투자 유지
- 섹터 집중도 40%까지 허용 (특히 AI/반도체)
- 단순 규칙이 아닌 데이터 기반 판단 필수

500자 이내, 실행 가능한 내용만."""

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
