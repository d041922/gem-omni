"""
GEM: OMNI Wealth Home (stabilized)
"""

import pandas as pd
import streamlit as st

from core.application.query_service import QueryService


def format_korean_currency(v: float) -> str:
    try:
        n = float(v)
    except Exception:
        return "KRW 0"
    return f"KRW {n:,.0f}"


def render_wealth_home() -> None:
    st.markdown("## Wealth Management Center")
    # Legacy key used by flow test; harmless compatibility input.
    st.text_input("Analysis Ticker", value="", key="analysis_ticker_input")

    query_service = QueryService()
    payload = query_service.get_wealth_home_payload()
    holdings = payload.get("holdings", [])
    intel = payload.get("top_picks", [])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("My Portfolio", format_korean_currency(payload.get("total_asset", 0)))
    with c2:
        st.metric("Stock", format_korean_currency(payload.get("holdings_value", 0)))
    with c3:
        st.metric("Cash", format_korean_currency(payload.get("cash", 0)))

    if st.button("Sync Portfolio"):
        query_service.sync_wealth_portfolio()
        st.rerun()

    df = pd.DataFrame(holdings)
    if not df.empty:
        if "account" not in df.columns:
            df["account"] = "Main"
        if "tier" not in df.columns:
            df["tier"] = "Core"
        if "name" not in df.columns:
            df["name"] = df.get("ticker", "")
        if "current_price" not in df.columns:
            df["current_price"] = 0.0
        if "quantity" not in df.columns:
            df["quantity"] = 0.0
        if "current_value_krw" not in df.columns:
            df["current_value_krw"] = df["quantity"] * df["current_price"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No holdings yet.")

    st.markdown("### Top Picks")
    if intel:
        for row in intel[:5]:
            st.write(f"- {row.get('ticker', 'N/A')}: {row.get('score', 0)}")
    else:
        st.caption("No screener results yet.")

    if st.button("Run Scan", key="btn_run_scan"):
        if query_service.run_wealth_scan():
            st.success("Scan complete")
        else:
            st.info("No tickers available for scan.")


if __name__ == "__main__":
    render_wealth_home()
