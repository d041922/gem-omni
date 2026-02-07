"""
Earnings Calendar [GEM: OMNI] - Model Compatible Edition
Fixes 'Portfolio' object attribute errors.
"""
import streamlit as st
import pandas as pd
from core.data_manager import DataManager
from pages.style_utils import load_custom_css

def render_earnings_page():
    load_custom_css()
    st.markdown("## 📅 Earnings Calendar")
    st.caption("Upcoming and Recent Corporate Earnings Announcements")
    st.divider()

    # --- 1. Control Bar ---
    c1, c2 = st.columns([3, 1])
    with c1:
        st.radio("Display Mode", ["Calendar View", "List View"], horizontal=True, label_visibility="collapsed")
    with c2:
        filter_mine = st.toggle("My Portfolio Only", value=False)

    # --- 2. Data Fetch via Portfolio Model ---
    portfolio = DataManager.get_portfolio_data()
    monitored_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "005930.KS", "000660.KS"]
    
    # Correctly check for holdings in the Portfolio object
    if portfolio and portfolio.holdings:
        # Extract tickers from holdings list
        port_tickers = [h.get('종목코드') for h in portfolio.holdings if h.get('종목코드')]
        monitored_tickers = list(set(monitored_tickers + port_tickers))

    if 'earnings_cache' not in st.session_state:
        st.session_state.earnings_cache = []

"""
Earnings Calendar [GEM: OMNI] - SSOT Compliant Edition
"""
import streamlit as st
import pandas as pd
from core.data_manager import DataManager
from skills.data_orchestrator import DataOrchestrator
from pages.style_utils import load_custom_css

def render_earnings_page():
    load_custom_css()
    orchestrator = DataOrchestrator()
    st.markdown("## 📅 Earnings Calendar")
    st.caption("Upcoming and Recent Corporate Earnings Announcements")
    st.divider()

    # (중략: UI 로직...)
    
    if st.button("🔄 Sync Earnings Data", use_container_width=True, key="btn_sync_earnings"):
        events = []
        prog = st.progress(0)
        status = st.empty()
        
        for i, ticker in enumerate(monitored_tickers):
            status.text(f"Syncing {ticker} via Orchestrator...")
            # [SSOT] 오케스트레이터를 통한 통합 데이터 호출
            data = orchestrator.get_market_data(ticker)
            e_date = data.get("earnings_date")
            
            if e_date:
                events.append({
                    "ticker": ticker,
                    "name": ticker, # 종목명은 필요시 DataManager에서 보강
                    "date": e_date,
                    "country": "KR" if ".KS" in ticker or ".KQ" in ticker else "US",
                    "link": f"https://finance.yahoo.com/quote/{ticker}"
                })
            prog.progress((i + 1) / len(monitored_tickers))
        
        st.session_state.earnings_cache = events
        status.empty()
        prog.empty()
        st.rerun()

    # --- 3. Render ---
    events_list = st.session_state.earnings_cache
    if not events_list:
        st.info("💡 Click 'Sync Earnings Data' to load upcoming earnings events.")
        return

    df_events = pd.DataFrame(events_list)
    if filter_mine and portfolio and portfolio.holdings:
        my_tickers = set([h.get('종목코드') for h in portfolio.holdings])
        df_events = df_events[df_events['ticker'].isin(my_tickers)]

    if df_events.empty:
        st.caption("No upcoming earnings found for selected filter.")
        return

    # Sort and Render
    df_events['sort_date'] = pd.to_datetime(df_events['date'])
    st.dataframe(df_events[['date', 'name', 'ticker', 'country']].sort_values('date'), use_container_width=True, hide_index=True)