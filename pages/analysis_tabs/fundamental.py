"""
Fundamental Analysis Module
Encapsulates all fundamental analysis rendering logic.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from skills.quant_engine import FactorEngine
from skills.market_screener import MarketScreener


def _resolve_peg_display(growth: dict, valuation: dict) -> tuple[str, str]:
    peg = growth.get("peg_ratio")
    if peg is not None and peg != 0:
        return f"{peg:.2f}", "reported"

    pe = valuation.get("trailing_pe")
    rev_growth = growth.get("rev_growth")
    if pe and rev_growth and rev_growth > 0:
        derived = pe / (rev_growth * 100)
        return f"{derived:.2f}", "derived: trailing_pe / revenue_growth"

    return "N/A", "unavailable: growth/valuation data missing"


def render_fundamental_tab(
    ticker_only: str, screener: MarketScreener, extra: dict, last_p: float, holding_info: dict = None
):
    """
    Renders the Fundamental Analysis tab (Tab 3).
    Includes: Comprehensive Verdict (Top), Quarterly Results, Master Matrix, and Key Metrics.
    """
    st.markdown("#### 🏛️ 기업 내재가치 및 펀더멘털 분석 (Fundamentals)")

    # [Data Preparation]
    verdict = FactorEngine.generate_comprehensive_verdict(extra, last_p, ticker_only, holding_info)
    peer_summary = FactorEngine.generate_peer_comparison(extra)

    # --- [NEW] Comprehensive Verdict Section (Moved to TOP) ---
    st.markdown("### 💡 종합 판정 (Verdict)")
    v_col1, v_col2 = st.columns([2, 1])
    with v_col1:
        st.markdown(
            f"""
        <div style="background: rgba(49, 130, 246, 0.05); padding: 20px; border-radius: 12px; border-left: 5px solid #3182F6;">
            <ul style="margin: 0; padding-left: 20px; color: #E6EDF3; line-height: 1.8;">
                <li><b>밸류에이션:</b> {verdict["valuation"]}</li>
                <li><b>성장 모멘텀:</b> {verdict["growth"]}</li>
                <li><b>리스크 요인 (Watch Item):</b> {verdict["risk"]}</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with v_col2:
        sector_name = extra.get("profile", {}).get("sector", "시장")
        st.markdown(
            f"<div style='text-align:center; padding:10px; opacity:0.75;'>업계 평균({sector_name}) 대비<br><b style='font-size:1.0rem; color:#8B949E;'>상대 평가 요약</b></div>",
            unsafe_allow_html=True,
        )
        # Peer Comparison (Fixed HTML rendering)
        st.markdown(
            f"<div style='background: rgba(0, 216, 165, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(0, 216, 165, 0.2); font-size: 0.85rem; color: #00D8A5; margin-top:10px;'>{peer_summary}</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    f_col1, f_col2 = st.columns([1.2, 1])
    with f_col1:
        fin_df = screener.get_financial_data(ticker_only)
        if not fin_df.empty:
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=fin_df.index,
                    y=fin_df["Total Revenue"],
                    name="매출",
                    marker_color="#3182F6",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=fin_df.index,
                    y=fin_df["Net Income"],
                    name="순이익",
                    line=dict(color="#FF4B4B", width=3),
                )
            )
            fig.update_layout(
                title="주요 실적 추이 (Quarterly)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E6EDF3"),
                height=400,
                margin=dict(t=40, b=20, l=0, r=0),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### 📂 전략적 펀더멘털 리포트 (Master Matrix)")
        report_data = FactorEngine.generate_fundamental_report(extra)
        if report_data:
            st.dataframe(pd.DataFrame(report_data), use_container_width=True, hide_index=True)
        else:
            st.info("상세 리포트 생성을 위한 데이터가 부족합니다.")

    with f_col2:
        st.markdown("##### 💎 핵심 지표 대시보드 (Key Metrics)")
        fin = extra.get("financials", {})
        growth = extra.get("growth", {})
        val = extra.get("valuation", {})
        health = extra.get("health", {})

        # --- Row 1: 수익성 & 성장성 ---
        c1, c2 = st.columns(2)
        c1.metric(
            "ROE (수익성)",
            f"{(fin.get('roe', 0) * 100):.1f}%" if fin.get("roe") else "N/A",
        )
        peg_value, peg_source = _resolve_peg_display(growth, val)
        c2.metric(
            "PEG Ratio (성장성)",
            peg_value,
        )
        c2.caption(peg_source)
        st.divider()

        # --- Row 2: 가치평가 & 재무건전성 ---
        v1, v2, v3 = st.columns(3)
        pe_ttm = val.get("trailing_pe", 0)
        pe_fwd = val.get("forward_pe", 0)
        v1.metric(
            "P/E (TTM)",
            f"{pe_ttm:.1f}x" if pe_ttm else "N/A",
        )
        v2.metric(
            "P/E (FWD)",
            f"{pe_fwd:.1f}x" if pe_fwd else "N/A",
        )
        v3.metric(
            "부채비율 (Safety)",
            f"{health.get('debt_to_equity', 0):.1f}%"
            if health.get("debt_to_equity")
            else "N/A",
        )
        st.divider()

        # --- Row 3: 현금흐름 & 유동성 ---
        f1, f2 = st.columns(2)
        fcf = fin.get("fcf") if fin.get("fcf") is not None else 0
        ni = fin.get("net_income") if fin.get("net_income") is not None else 0
        fcf_ni_ratio = (fcf / ni * 100) if ni != 0 else 0
        f1.metric("현금전환율 (Quality)", f"{fcf_ni_ratio:.1f}%" if fcf != 0 else "N/A")
        f2.metric(
            "유동비율 (Liquidity)",
            f"{health.get('current_ratio', 0):.2f}x"
            if health.get("current_ratio")
            else "N/A",
        )
        st.divider()
