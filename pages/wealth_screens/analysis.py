import streamlit as st

from core.data_manager import DataManager
from pages.style_utils import (
    format_krw,
    metric_card,
    render_tv_chart,
    render_tv_news,
    render_tv_technicals,
)


def render_analysis_screen() -> None:
    st.title("심화 종목 분석")

    ticker = st.text_input(
        "티커 입력 (예: AAPL, PLTR, 005930.KS)",
        value="PLTR",
    ).upper()

    if "calculated_portfolio" in st.session_state:
        df = st.session_state["calculated_portfolio"]
        selected = df[df["ticker"].str.upper() == ticker]
        holding = selected.iloc[0] if not selected.empty else None

        if holding is not None:
            c_holdings, _ = st.columns([2, 1])
            qty = holding.get("quantity", 0)
            ret = holding.get("return_pct", 0.0)
            with c_holdings:
                st.success(f"보유 중: {qty}주 ({ret:+.1f}%)")

    if not ticker:
        st.info("분석할 종목 티커를 입력해 주세요.")
        return

    with st.spinner(f"{ticker} 종목 데이터를 불러오는 중..."):
        res = DataManager.get_stock_data(ticker)
        if not res.get("success"):
            st.error(f"종목 데이터 조회 실패: {res.get('error')}")
            return
        summary = res.get("summary", {})

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card(
            "현재가",
            f"{summary.get('unit', '$')}{summary.get('current_price', 0):,.2f}",
            f"{summary.get('price_change_pct', 0):+.2f}%",
        )
    with m2:
        metric_card(
            "52주 최고",
            f"{summary.get('unit', '$')}{summary.get('fifty_two_week_high', 0):,.2f}",
            "상단 범위",
        )
    with m3:
        metric_card("거래량", f"{summary.get('volume', 0):,.0f}", "주")
    with m4:
        metric_card("시가총액", format_krw(summary.get("market_cap", 0)), "Market Cap")

    tab_chart, tab_fund, tab_val, tab_peer, tab_sim = st.tabs(
        ["프로 차트", "재무 건강성", "밸류에이션", "동종업 비교", "시뮬레이션"]
    )

    with tab_chart:
        render_tv_chart(ticker)
        c1, c2 = st.columns(2)
        with c1:
            render_tv_technicals(ticker)
        with c2:
            render_tv_news(ticker)

    with tab_fund:
        st.subheader("재무 건강성")
        st.json(summary.get("financials", {}))

    with tab_val:
        st.subheader("밸류에이션 평가")
        st.info("Valuation Engine 연동 예정")

    with tab_peer:
        st.subheader("동종업 비교")
        st.info("동종업 비교 기능 연동 예정")

    with tab_sim:
        st.subheader("몬테카를로 시뮬레이션")
        st.info("시뮬레이션 기능 연동 예정")
