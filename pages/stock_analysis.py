"""
Single Stock Analysis Page (한글 버전)
Token-optimized deep analysis for individual stocks
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, Dict, Any
from skills.stock_analyzer import analyze_stock, generate_ai_analysis
from agents.crews.stock_analysis_crew import run_stock_analysis
from skills.portfolio_utils import check_portfolio_holding


@st.cache_data(ttl=1800)
def cached_analyze_stock(ticker: str, period: str):
    return analyze_stock(ticker, period)


def render_stock_analysis_page():
    """Render single stock analysis page"""
    st.markdown("<p class='panel-header'>🔍 개별 종목 심층 분석</p>", unsafe_allow_html=True)

    from skills.popular_stocks import get_all_popular_stocks, get_ticker_display_name
    col_in, col_pe = st.columns([3, 1])

    with col_in:
        in_mode = st.radio("입력 방식", ["인기 종목 선택", "직접 입력"], horizontal=True, key='in_mode')
    with col_pe:
        period = st.selectbox("분석 기간", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3, key='st_period')

    ticker_input = ""
    if in_mode == "인기 종목 선택":
        all_stocks = get_all_popular_stocks()
        stock_options = [""] + [f"{t} - {n}" for t, n in sorted(all_stocks.items())]
        selected = st.selectbox("종목 선택", options=stock_options, key='st_select')
        if selected: ticker_input = selected.split(" - ")[0].strip()
    else:
        ticker_input = st.text_input("티커 직접 입력", value=st.session_state.get('last_ticker', ''), placeholder="AAPL, NVDA, 005930.KS").upper().strip()

    analyze_button = st.button("🚀 종목 분석", width="stretch", type="primary")

    if not analyze_button and 'current_stock_analysis' not in st.session_state:
        st.info("👆 종목 티커를 입력하고 '종목 분석' 버튼을 클릭하세요")
        return

    if analyze_button and ticker_input:
        with st.spinner(f"📊 {ticker_input} 분석 중..."):
            res = cached_analyze_stock(ticker_input, period)
            if res.get("success"):
                st.session_state.current_stock_analysis = res
                st.session_state.last_ticker = ticker_input
                if 'ai_stock_analysis' in st.session_state: del st.session_state.ai_stock_analysis
            else:
                st.error(f"❌ {res.get('error', '분석 실패')}"); return

    if 'current_stock_analysis' not in st.session_state: return
    
    res = st.session_state.current_stock_analysis
    summary = res["summary"]
    df = res["dataframe"]
    ticker = res["ticker"]

    # --- Header ---
    st.divider()
    c_n, c_p, c_c = st.columns([2, 1, 1])
    with c_n:
        port_info = check_portfolio_holding(ticker)
        st.markdown(f"## {summary['name']} {'🎯' if port_info else ''}")
        if port_info:
            st.caption(f"⭐ 포트폴리오 보유 중 | 수익률: {port_info['return_pct']:+.1f}% | 가치: ₩{port_info['current_value']/1e6:.1f}M")
    with c_p:
        st.metric("현재가", f"${summary['current_price']:.2f}", f"{summary['price_change_pct']:+.2f}%")
    with c_c:
        st.metric("52주 위치", f"{summary['position_52w_pct']:.1f}%", f"최고: ${summary['52week_high']:.2f}")

    # --- Content ---
    t1, t2, t3, t4 = st.tabs(["📈 차트/지표", "💼 펀더멘털", "📰 리서치/뉴스", "🧠 AI 분석"])
    
    with t1:
        col_c, col_i = st.columns([2, 1])
        with col_c: render_price_chart(df, ticker)
        with col_i: render_technical_indicators(summary)
        
    with t2:
        render_fundamentals(summary)
        st.divider()
        render_earnings_analysis(ticker)
        st.divider()
        render_valuation_analysis(ticker)
        
    with t3:
        render_optional_sections(ticker)

    with t4:
        render_ai_section(res)


def render_optional_sections(ticker: str):
    """Render sections only if data is significant"""
    from skills.news_analyzer import get_company_news, get_analyst_ratings, get_insider_transactions
    
    # Analyst Ratings
    ratings = get_analyst_ratings(ticker)
    if ratings.get('status') != 'error' and ratings.get('target_mean'):
        st.divider()
        st.markdown("### 💼 애널리스트 의견")
        c1, c2, c3 = st.columns(3)
        c1.metric("컨센서스", ratings.get('consensus', 'N/A'))
        c2.metric("목표가 (평균)", f"${ratings.get('target_mean', 0):,.2f}")
        c3.metric("상승 여력", f"{ratings.get('upside_pct', 0):+.1f}%")

    # News
    news_items = get_company_news(ticker, limit=5)
    if news_items:
        st.divider()
        st.markdown("### 📰 최근 뉴스")
        for item in news_items:
            st.markdown(f"**[{item.get('title')}]({item.get('link')})**")
            st.caption(f"{item.get('publisher')} | {item.get('timestamp').strftime('%Y-%m-%d') if item.get('timestamp') else ''}")

    # Insider (Only if significant)
    insider = get_insider_transactions(ticker)
    if insider.get('status') == 'success' and (insider.get('buy_count', 0) > 0 or insider.get('sell_count', 0) > 0):
        st.divider()
        st.markdown("### 🔐 내부자 거래")
        st.info(f"내부자 심리: {insider.get('sentiment')} | {insider.get('recent_summary')}")


def render_ai_section(res: dict):
    # Display previous result if it exists
    if 'ai_stock_analysis' in st.session_state:
        st.markdown(st.session_state.ai_stock_analysis)
        st.divider()
        st.caption("다른 방식으로 다시 분석하시겠습니까?")

    # Always show analysis options or show them when no result is present
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🪄 빠른 AI 분석 (Gemini)", width="stretch", key="btn_gemini"):
            with st.spinner("Gemini가 분석 중..."):
                ai_res = generate_ai_analysis(res)
                st.session_state.ai_stock_analysis = ai_res
                st.rerun()
    with col2:
        if st.button("🤖 에이전트 토론 분석 (CrewAI)", width="stretch", type="primary", key="btn_crewai"):
            with st.spinner("4인의 에이전트가 심층 토론 중 (약 30-60초)..."):
                # 4인 에이전트 실행 (Analyst, Strategy, Risk, Data Sync)
                from agents.crews.stock_analysis_crew import run_stock_analysis
                
                # Prepare arguments
                ticker = res['ticker']
                analysis_data = res['summary']
                
                # Temporary file path
                import os
                data_file_path = os.path.join("tmp", "cache", f"{ticker}_full.json")
                
                ai_res = run_stock_analysis(
                    ticker=ticker,
                    analysis_data=analysis_data,
                    data_file_path=data_file_path
                )
                st.session_state.ai_stock_analysis = ai_res
                
                # Update Home Activity Log
                st.session_state.ai_insights = f"[{res['ticker']}] CrewAI 심층 분석 완료"
                st.rerun()

# --- Utility Renderers (Simplified) ---
def render_price_chart(df, ticker):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='gray', opacity=0.5), row=2, col=1)
    fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

def render_technical_indicators(summary):
    tech = summary.get('technical_indicators', {})
    st.metric("RSI (14)", f"{tech.get('rsi', 0):.1f}")
    st.metric("MACD", f"{tech.get('macd', 0):.2f}")
    st.metric("MFI (자금흐름)", f"{tech.get('mfi', 0):.1f}")

def render_fundamentals(summary):
    fund = summary.get('fundamentals', {})
    
    # Row 1: Basic
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("섹터", fund.get('sector', 'N/A'))
    c2.metric("시가총액", f"${fund.get('market_cap', 0)/1e9:.1f}B")
    c3.metric("P/E (PER)", f"{fund.get('pe_ratio', 0):.1f}")
    c4.metric("P/B (PBR)", f"{fund.get('price_to_book', 0):.2f}")
    
    # Row 2: Profitability & Growth
    st.divider()
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("ROE", f"{fund.get('roe', 0):.1f}%")
    c6.metric("영업이익률", f"{fund.get('operating_margin', 0):.1f}%")
    c7.metric("매출 성장률", f"{fund.get('revenue_growth', 0):+.1f}%")
    c8.metric("EPS 성장률", f"{fund.get('eps_growth', 0):+.1f}%")
    
    # Row 3: Health & Others
    st.divider()
    c9, c10, c11, c12 = st.columns(4)
    c9.metric("부채비율", f"{fund.get('debt_to_equity', 0):.1f}")
    c10.metric("유동비율", f"{fund.get('current_ratio', 0):.2f}")
    c11.metric("배당수익률", f"{fund.get('dividend_yield', 0):.1f}%" if fund.get('dividend_yield') else "0.0%")
    c12.metric("Beta (변동성)", f"{fund.get('beta', 0):.2f}")

def render_earnings_analysis(ticker):
    try:
        from skills.earnings_analyzer import analyze_earnings_trend
        res = analyze_earnings_trend(ticker)
        if 'error' not in res:
            st.markdown(f"**📊 실적 추세**: {res.get('revenue_trend', {}).get('summary', '데이터 없음')}")
            st.caption(f"실적 품질 스코어: {res.get('quality_score', 0)}/10")
    except: st.caption("실적 분석 데이터 로드 실패")

def render_valuation_analysis(ticker: str):
    try:
        from skills.valuation_engine import calculate_valuation_metrics
        res = calculate_valuation_metrics(ticker)
        if 'error' not in res:
            st.markdown(f"### ⚖️ 밸류에이션: **{res.get('style')}**")
            st.info(res.get('summary', ''))
            key_m = res.get('style_analysis', {}).get('key_metrics', {})
            if key_m:
                cols = st.columns(len(key_m))
                for i, (k, v) in enumerate(key_m.items()): cols[i].metric(k, v)
    except: st.error("밸류에이션 분석 중 오류 발생")