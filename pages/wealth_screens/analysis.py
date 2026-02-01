import streamlit as st
from core.data_manager import DataManager
from pages.style_utils import metric_card, format_krw, render_tv_chart, render_tv_technicals, render_tv_news

def render_analysis_screen():
    st.title("🔬 Deep Stock Analysis")
    
    ticker = st.text_input("Ticker 입력 (예: AAPL, PLTR, 005930.KS)", value="PLTR").upper()
    
    if 'calculated_portfolio' in st.session_state:
        df = st.session_state['calculated_portfolio']
        holding = df[df['ticker'].str.upper() == ticker].iloc[0] if not df[df['ticker'].str.upper() == ticker].empty else None
        
        if holding is not None:
            c_holdings, _ = st.columns([2, 1])
            qty = holding.get('quantity', 0)
            ret = holding.get('return_pct', 0.0)
            with c_holdings:
                st.success(f"현재 보유 중: {qty}주 ({ret:+.1f}%)")

    if not ticker:
        st.info("티커를 입력하면 상세 분석이 시작됩니다.")
        return

    with st.spinner(f"{ticker} 데이터 분석 중..."):
        res = DataManager.get_stock_data(ticker)
        if not res["success"]:
            st.error(f"데이터를 불러오지 못했습니다: {res['error']}")
            return
        
        summary = res["summary"]
        
    # 1. Overview Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("현재가", f"{summary.get('unit', '$')}{summary.get('current_price', 0):,.2f}", f"{summary.get('price_change_pct', 0):+.2f}%")
    with m2:
        metric_card("52주 최고", f"{summary.get('unit', '$')}{summary.get('fifty_two_week_high', 0):,.2f}", "Upper Limit")
    with m3:
        metric_card("거래량", f"{summary.get('volume', 0):,.0f}", "Shares")
    with m4:
        metric_card("시가총액", format_krw(summary.get('market_cap', 0)), "Market Cap")

    # 2. Tabs for different views
    tab_chart, tab_fund, tab_val, tab_peer, tab_sim = st.tabs(["📈 Pro Chart", "📊 펀더멘털", "💎 가치평가", "👥 경쟁사 비교", "🎲 시뮬레이션"])
    
    with tab_chart:
        render_tv_chart(ticker)
        c1, c2 = st.columns(2)
        with c1:
            render_tv_technicals(ticker)
        with c2:
            render_tv_news(ticker)
            
    with tab_fund:
        st.subheader("Financial Health")
        st.json(summary.get("financials", {}))
        
    with tab_val:
        st.subheader("Valuation Assessment")
        # To be implemented with ValuationEngine
        st.info("Valuation Engine 연동 중...")

    with tab_peer:
        st.subheader("Peer Group Comparison")
        st.info("경쟁사 데이터 분석 중...")
        
    with tab_sim:
        st.subheader("Monte Carlo Simulation")
        st.info("시뮬레이션 모듈 준비 중...")
