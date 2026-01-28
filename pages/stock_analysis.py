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
    from skills.stock_analyzer import get_technical_insight, get_fundamental_insight
    
    t1, t2, t3 = st.tabs(["📈 차트/기술적", "💼 펀더멘털/리서치", "🧠 AI 심층분석"])
    
    with t1:
        # Technical Insight
        tech_insight = get_technical_insight(summary)
        st.info(f"🤖 **AI 기술적 요약**: {tech_insight}")
        
        col_c, col_i = st.columns([2, 1])
        with col_c: render_price_chart(df, ticker)
        with col_i: render_technical_indicators(summary)
        
    with t2:
        # Fundamental Insight
        fund_insight = get_fundamental_insight(summary)
        st.info(f"🤖 **AI 펀더멘털 요약**: {fund_insight}")

        # 1. Analyst Ratings (Moved Up)
        render_analyst_ratings(ticker)
        
        st.divider()

        # 2. Fundamentals Table
        render_fundamentals(summary)
        st.divider()
        
        # 3. Research & Valuation
        st.markdown("### 📝 리서치 & 실적")
        render_earnings_analysis(ticker)
        st.divider()
        render_valuation_analysis(ticker)
        
        # 4. Other Optional Sections
        render_insider_trading(ticker)
        
    with t3:
        render_ai_section(res)


def render_analyst_ratings(ticker: str):
    """Render Analyst Ratings with color coding"""
    from skills.news_analyzer import get_analyst_ratings
    ratings = get_analyst_ratings(ticker)
    
    if ratings.get('status') == 'error' or not ratings.get('target_mean'):
        return

    st.markdown("### 💼 애널리스트 의견")
    c1, c2, c3 = st.columns(3)
    
    # Consensus Color
    cons = ratings.get('consensus', 'N/A')
    
    # Delta for color coding
    cons_delta = None
    if 'Buy' in cons or 'Outperform' in cons: 
        cons_delta = "+Good" # Green
    elif 'Sell' in cons or 'Underperform' in cons: 
        cons_delta = "-Bad" # Red
    elif 'Hold' in cons:
        cons_delta = "Neutral" # Gray
    
    c1.metric("컨센서스", cons, delta=cons_delta, delta_color="normal")
    c2.metric("목표가 (평균)", f"${ratings.get('target_mean', 0):,.2f}")
    
    # Upside Color
    upside = ratings.get('upside_pct', 0)
    # Use +Good/-Bad instead of repeating number
    upside_delta = None
    if upside > 0: upside_delta = "+Good"
    elif upside < 0: upside_delta = "-Bad"

    c3.metric("상승 여력", f"{upside:+.1f}%", delta=upside_delta, delta_color="normal")

def render_insider_trading(ticker: str):
    """Render Insider Trading (Moved from optional_sections)"""
    from skills.news_analyzer import get_insider_transactions
    insider = get_insider_transactions(ticker)
    if insider.get('status') == 'success' and (insider.get('buy_count', 0) > 0 or insider.get('sell_count', 0) > 0):
        st.divider()
        st.markdown("### 🔐 내부자 거래")
        st.info(f"내부자 심리: {insider.get('sentiment')} | {insider.get('recent_summary')}")

def render_fundamentals(summary):
    fund = summary.get('fundamentals', {})
    
    def format_metric(label, value, suffix="", good_thresh=None, bad_thresh=None, higher_is_better=True, help_text=None):
        """Helper to render metric with color coding based on thresholds"""
        
        delta_val = None
        if good_thresh is not None and bad_thresh is not None:
            is_good = value >= good_thresh if higher_is_better else value <= good_thresh
            is_bad = value <= bad_thresh if higher_is_better else value >= bad_thresh
            
            if is_good: 
                # Use + for Green in 'normal' mode
                delta_val = "+Good"
            elif is_bad: 
                # Use - for Red in 'normal' mode
                delta_val = "-Caution"
        
        # Display
        display_val = f"{value:,.1f}{suffix}" if isinstance(value, (int, float)) else value
        if value is None or value == 0:
             display_val = "-"
             delta_val = None

        st.metric(label, display_val, delta=delta_val, delta_color="normal", help=help_text)

    # Row 1: Valuation & PEG
    st.markdown("##### 💎 밸류에이션 & 성장 (PEG)")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("시가총액", f"${fund.get('market_cap', 0)/1e9:.1f}B")
    with c2:
        pe = fund.get('pe_ratio', 0)
        format_metric("P/E (PER)", pe, good_thresh=15, bad_thresh=30, higher_is_better=False)
    with c3:
        # PEG Logic
        peg = fund.get('peg_ratio', 0)
        peg_label = "PEG (성장가치)"
        
        # Calculate PEG if missing and data available
        if (peg is None or peg == 0) and fund.get('eps_growth', 0) > 0 and fund.get('pe_ratio', 0) > 0:
            peg = fund.get('pe_ratio') / fund.get('eps_growth')
            peg_label = "PEG (추정)"
        
        if peg is not None and peg > 0:
            format_metric(peg_label, peg, good_thresh=1.0, bad_thresh=2.0, higher_is_better=False, help_text="< 1.0: 저평가, > 2.0: 고평가")
        else:
            st.metric(peg_label, "N/A", help="데이터 부족으로 계산 불가")
        
    with c4:
        format_metric("EPS 성장률", fund.get('eps_growth', 0), "%", good_thresh=10, bad_thresh=0)

    st.divider()

    # Row 2: Profitability
    st.markdown("##### 💰 수익성 (Profitability)")
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        format_metric("ROE (자기자본이익률)", fund.get('roe', 0), "%", good_thresh=15, bad_thresh=5)
    with c6:
        format_metric("영업이익률", fund.get('operating_margin', 0), "%", good_thresh=10, bad_thresh=0)
    with c7:
        format_metric("순이익률", fund.get('profit_margin', 0), "%", good_thresh=10, bad_thresh=0)
    with c8:
         format_metric("매출 성장률", fund.get('revenue_growth', 0), "%", good_thresh=10, bad_thresh=0)

    st.divider()

    # Row 3: Financial Health
    st.markdown("##### 🛡️ 재무 건전성 (Health)")
    c9, c10, c11, c12 = st.columns(4)
    with c9:
        format_metric("부채비율", fund.get('debt_to_equity', 0), "%", good_thresh=100, bad_thresh=200, higher_is_better=False)
    with c10:
        format_metric("유동비율", fund.get('current_ratio', 0), "", good_thresh=1.5, bad_thresh=1.0)
    with c11:
        div = fund.get('dividend_yield', 0)
        st.metric("배당수익률", f"{div:.1f}%" if div else "-")
    with c12:
        st.metric("Beta (변동성)", f"{fund.get('beta', 0):.2f}")


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

# --- Utility Renderers (Simplified) ---
def render_price_chart(df, ticker):
    # 포트폴리오 보유 정보 확인
    from skills.portfolio_utils import check_portfolio_holding
    port_info = check_portfolio_holding(ticker)
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)

    # 1. Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Price', showlegend=False
    ), row=1, col=1)

    # 2. Moving Averages (MA20, MA60)
    if 'ma20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ma20'], name='MA 20',
            line=dict(color='orange', width=1), opacity=0.8
        ), row=1, col=1)
    if 'ma60' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ma60'], name='MA 60',
            line=dict(color='green', width=1), opacity=0.8
        ), row=1, col=1)

    # 3. Bollinger Bands
    if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_upper'], name='BB Upper',
            line=dict(color='gray', width=0), showlegend=False
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['bb_lower'], name='BB Lower',
            line=dict(color='gray', width=0), fill='tonexty', fillcolor='rgba(128, 128, 128, 0.1)',
            showlegend=False
        ), row=1, col=1)

    # 4. Avg Buy Price Line (If held)
    if port_info:
        # Determine correct average price based on ticker (KRW for Korean stocks, USD for others)
        if ticker.endswith('.KS') or ticker.endswith('.KQ'):
            avg_price = port_info.get('avg_price_krw', 0)
        else:
            avg_price = port_info.get('avg_price_usd', 0)
            
        if avg_price > 0:
            fig.add_hline(y=avg_price, line_dash="dash", line_color="yellow", annotation_text="My Avg", row=1, col=1)

    # 5. Volume
    colors = ['red' if row['Open'] - row['Close'] >= 0 else 'green' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], name='Volume', marker_color=colors, opacity=0.5
    ), row=2, col=1)

    # Layout Updates
    fig.update_layout(
        height=550, 
        template='plotly_dark', 
        xaxis_rangeslider_visible=False, 
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_technical_indicators(summary):
    tech = summary.get('technical_indicators', {})
    st.metric("RSI (14)", f"{tech.get('rsi', 0):.1f}")
    st.metric("MACD", f"{tech.get('macd', 0):.2f}")
    st.metric("MFI (자금흐름)", f"{tech.get('mfi', 0):.1f}")