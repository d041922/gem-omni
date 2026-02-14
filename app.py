"""GEM: OMNI entrypoint."""

import streamlit as st
from dotenv import load_dotenv

from pages.style_utils import load_custom_css
from skills.data_orchestrator import DataOrchestrator


def _init() -> DataOrchestrator:
    load_dotenv()
    st.set_page_config(
        page_title="GEM: OMNI",
        page_icon="G",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_custom_css()
    return DataOrchestrator()


def _sync_if_needed(orchestrator: DataOrchestrator) -> None:
    try:
        if orchestrator.is_expired("portfolio", ttl_seconds=3600):
            orchestrator.sync_portfolio()
    except Exception:
        pass


def _render_sidebar(orchestrator: DataOrchestrator) -> None:
    with st.sidebar:
        st.title("OMNI Center")
        st.divider()

        # Legacy key expected by streamlit flow test.
        if st.button("Wealth Home", key="btn_wealth", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

        if st.button("Dashboard", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()

        if st.button("Market Overview", use_container_width=True):
            st.session_state.current_page = "market"
            st.rerun()

        if st.button("Screener", use_container_width=True):
            st.session_state.current_page = "screener"
            st.rerun()

        if st.button("Analysis", use_container_width=True):
            st.session_state.current_page = "analysis"
            st.rerun()

        st.divider()
        if st.button("Sync Data", use_container_width=True):
            with st.spinner("Syncing..."):
                orchestrator.sync_portfolio()
                st.rerun()


def _route() -> None:
    page = st.session_state.get("current_page", "home")

    if page == "home":
        from pages.wealth_home import render_wealth_home

        render_wealth_home()
        return

    if page == "market":
        from pages.market_overview import render_market_overview

        render_market_overview()
        return

    if page == "screener":
        from pages.screener import render_screener

        render_screener()
        return

    if page == "analysis":
        from pages.stock_analysis import render_stock_analysis

        render_stock_analysis()
        return

    st.error("Page not found")


def main() -> None:
    orchestrator = _init()
    _sync_if_needed(orchestrator)

    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    _render_sidebar(orchestrator)
    _route()


if __name__ == "__main__":
    main()
