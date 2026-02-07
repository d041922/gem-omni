"""
Technical Analysis Module (Frozen)
Encapsulates all technical analysis rendering logic to prevent regression.
"""

import streamlit as st
from skills.quant_engine import FactorEngine
from skills.chart_tools import ChartEngine


def render_technical_tab(
    ticker_only: str,
    h_chart: object,
    market_context: dict,
    is_ready: bool,
    cur_sym: str,
    p_fmt: str,
    last_p: float,
):
    """
    Renders the Technical Analysis tab (Tab 2).
    Includes: Strategic Report, Trend Ribbon, Pivot Levels, and Technical Chart.
    """
    if is_ready and len(h_chart) > 1:
        report = FactorEngine.generate_strategic_analysis(
            ticker_only, last_p, h_chart, market_context
        )
        pivots = FactorEngine.calculate_pivot_points(h_chart.iloc[-1])
        ribbon = FactorEngine.get_ma_ribbon_status(h_chart)

        st.markdown("#### 📜 기술적 시장 전략 분석 (Strategic Report)")

        # MA Ribbon Visualization
        st.markdown("##### 🎗️ 이동평균선 추세판 (Trend Ribbon)")
        r_cols = st.columns(6)
        for i, (ma, status) in enumerate(ribbon.items()):
            color = (
                "#FF4B4B"
                if status == "Bullish"
                else "#3182F6"
                if status == "Bearish"
                else "#8B949E"
            )
            symbol = "▲" if status == "Bullish" else "▼" if status == "Bearish" else "-"
            with r_cols[i]:
                st.markdown(
                    f"<div style='text-align:center; padding:8px; background:rgba(255,255,255,0.05); border-radius:8px; border-bottom: 3px solid {color};'><span style='font-size:0.8rem; color:#8B949E;'>{ma}</span><br><b style='color:{color};'>{symbol}</b></div>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            f"""
        <table style="width:100%; border-collapse: collapse; background: rgba(255,255,255,0.02); border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05);">
            <tr style="background: rgba(49, 130, 246, 0.1);">
                <th style="padding: 18px; text-align: left; width: 25%; color: white; font-size: 1rem;">분석 항목</th>
                <th style="padding: 18px; text-align: left; color: white; font-size: 1rem;">전문가적 해석 (Professional Insight)</th>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 18px; font-weight: bold; color: #8B949E;">📍 시장 위치</td>
                <td style="padding: 18px; line-height: 1.6;">{report["position"]}</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 18px; font-weight: bold; color: #8B949E;">📈 추세 및 패턴</td>
                <td style="padding: 18px; line-height: 1.6;">{report["trend"]}</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 18px; font-weight: bold; color: #8B949E;">⚖️ 수급 및 변동성</td>
                <td style="padding: 18px; line-height: 1.6;">{report["supply"]}</td>
            </tr>
            <tr>
                <td style="padding: 18px; font-weight: bold; color: #8B949E;">🎯 대응 전략 제언</td>
                <td style="padding: 18px; line-height: 1.6; color: #E6EDF3;"><strong>{report["action"]}</strong></td>
            </tr>
        </table>
        """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("##### 📍 주요 대응 레이어 및 목표 가격 (Target Levels)")
        cols = st.columns(4)
        levels = [
            ("저항 2선", pivots["Classic"]["R2"], "#FF4B4B"),
            ("저항 1선", pivots["Classic"]["R1"], "#FF8A8A"),
            ("중심 피벗", pivots["Classic"]["P"], "#3182F6"),
            ("지지 1선", pivots["Classic"]["S1"], "#00D8A5"),
        ]
        for i, (label, val, color) in enumerate(levels):
            dist = ((val - last_p) / last_p) * 100
            with cols[i]:
                st.markdown(
                    f"<div style='text-align:center; padding:12px; background:rgba(255,255,255,0.02); border-radius:12px; border-top: 3px solid {color};'><span style='color:#8B949E; font-size:0.8rem;'>{label}</span><br><b style='font-size:1.1rem;'>{cur_sym}{val:{p_fmt}}</b><br><span style='color:{color}; font-size:0.85rem;'>{dist:+.2f}%</span></div>",
                    unsafe_allow_html=True,
                )
        st.plotly_chart(
            ChartEngine().create_technical_chart(
                ticker_only, h_chart, pivots["Classic"]
            ),
            use_container_width=True,
        )
    else:
        st.warning("기술 데이터를 불러오는 중...")
