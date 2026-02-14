"""Earnings calendar page."""

import pandas as pd
import streamlit as st

from core.data_manager import DataManager
from pages.style_utils import load_custom_css
from skills.data_orchestrator import DataOrchestrator


def _extract_ticker(holding: dict) -> str | None:
    for key in ("ticker", "symbol", "code"):
        value = holding.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def render_earnings_page() -> None:
    load_custom_css()
    orchestrator = DataOrchestrator()

    st.markdown("## Earnings Calendar")
    st.caption("Upcoming and recent corporate earnings announcements")
    st.divider()

    c1, c2 = st.columns([3, 1])
    with c1:
        st.radio(
            "Display Mode",
            ["Calendar View", "List View"],
            horizontal=True,
            label_visibility="collapsed",
        )
    with c2:
        filter_mine = st.toggle("My Portfolio Only", value=False)

    portfolio = DataManager.get_portfolio_data()
    monitored_tickers = {
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "TSLA",
        "META",
        "NFLX",
        "005930.KS",
        "000660.KS",
    }

    holdings = getattr(portfolio, "holdings", []) if portfolio else []
    for holding in holdings:
        if isinstance(holding, dict):
            ticker = _extract_ticker(holding)
            if ticker:
                monitored_tickers.add(ticker)

    if "earnings_cache" not in st.session_state:
        st.session_state.earnings_cache = []

    if st.button("Sync Earnings Data", use_container_width=True, key="btn_sync_earnings"):
        events: list[dict] = []
        tickers = sorted(monitored_tickers)
        prog = st.progress(0)
        status = st.empty()

        for i, ticker in enumerate(tickers):
            status.text(f"Syncing {ticker} via Orchestrator...")
            data = orchestrator.get_market_data(ticker)
            e_date = data.get("earnings_date")

            if e_date:
                events.append(
                    {
                        "ticker": ticker,
                        "name": ticker,
                        "date": e_date,
                        "country": "KR" if ".KS" in ticker or ".KQ" in ticker else "US",
                        "link": f"https://finance.yahoo.com/quote/{ticker}",
                    }
                )

            prog.progress((i + 1) / len(tickers))

        st.session_state.earnings_cache = events
        status.empty()
        prog.empty()
        st.rerun()

    events_list = st.session_state.earnings_cache
    if not events_list:
        st.info("Click 'Sync Earnings Data' to load upcoming earnings events.")
        return

    df_events = pd.DataFrame(events_list)
    if filter_mine and holdings:
        my_tickers = {
            _extract_ticker(h)
            for h in holdings
            if isinstance(h, dict) and _extract_ticker(h)
        }
        df_events = df_events[df_events["ticker"].isin(my_tickers)]

    if df_events.empty:
        st.caption("No upcoming earnings found for selected filter.")
        return

    df_events["sort_date"] = pd.to_datetime(df_events["date"])
    st.dataframe(
        df_events[["date", "name", "ticker", "country"]].sort_values("sort_date"),
        use_container_width=True,
        hide_index=True,
    )
