"""
Home Dashboard - Main landing page
Combines market overview, portfolio summary, and quick actions
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


def render_home_page():
    """Render home dashboard page"""
    st.markdown("# 💎 GEM: OMNI Command Center")
    st.markdown("**당신의 포트폴리오를 위한 AI 자산 관리 시스템**")

    st.divider()

    # === SECTION 1: Quick Stats ===
    st.markdown("<p class='panel-header'>📊 포트폴리오 개요</p>", unsafe_allow_html=True)

    if 'calculated_portfolio' in st.session_state:
        result_df = st.session_state.calculated_portfolio

        col1, col2, col3, col4 = st.columns(4)

        total_cost = result_df['매수금액(KRW)'].sum()
        total_value = result_df['평가금액(KRW)'].sum()
        total_profit = result_df['손익(KRW)'].sum()
        return_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

        col1.metric("총 투자금", f"₩{total_cost/1e8:.1f}억")
        col2.metric("총 평가금", f"₩{total_value/1e8:.1f}억")
        col3.metric("총 손익", f"₩{total_profit/1e6:.0f}백만", f"{return_pct:+.1f}%")
        col4.metric("종목 수", f"{len(result_df)}개")

        # Core/Satellite Quick View
        st.divider()
        if 'asset_type' not in result_df.columns:
            from skills.asset_classifier import AssetClassifier
            classifier = AssetClassifier(strategy='balanced')
            result_df['asset_type'] = result_df.apply(
                lambda row: classifier.classify(
                    row.get('티커코드', row.get('종목코드', '')),
                    row.get('카테고리', ''),
                    row.get('종목명', '')
                ), axis=1
            )

        col_core, col_sat = st.columns(2)

        with col_core:
            core_value = result_df[result_df['asset_type'] == 'Core']['평가금액(KRW)'].sum()
            core_pct = (core_value / total_value * 100) if total_value > 0 else 0
            st.metric("💎 Core 자산", f"₩{core_value/1e8:.1f}억", f"{core_pct:.1f}%")
            st.caption("목표: 50-60%")

        with col_sat:
            sat_value = result_df[result_df['asset_type'] == 'Satellite']['평가금액(KRW)'].sum()
            sat_pct = (sat_value / total_value * 100) if total_value > 0 else 0
            st.metric("🚀 Satellite 자산", f"₩{sat_value/1e8:.1f}억", f"{sat_pct:.1f}%")
            st.caption("목표: 40-50%")

    else:
        st.info("포트폴리오 데이터를 불러오는 중...")
        if st.button("📊 데이터 로드", type="primary"):
            st.rerun()

    st.divider()

    # === SECTION 2: Top Performers & Losers ===
    st.markdown("<p class='panel-header'>🏆 수익률 Top 5</p>", unsafe_allow_html=True)

    if 'calculated_portfolio' in st.session_state:
        result_df = st.session_state.calculated_portfolio

        col_top, col_bottom = st.columns(2)

        with col_top:
            st.markdown("**💚 상위 5종목**")
            top_5 = result_df.nlargest(5, '수익률(%)')

            for idx, row in top_5.iterrows():
                name = row.get('종목명', 'N/A')
                ret = row.get('수익률(%)', 0)
                value = row.get('평가금액(KRW)', 0)

                st.caption(f"**{name}**: {ret:+.1f}% (₩{value/1e6:.0f}M)")

        with col_bottom:
            st.markdown("**❤️ 하위 5종목**")
            bottom_5 = result_df.nsmallest(5, '수익률(%)')

            for idx, row in bottom_5.iterrows():
                name = row.get('종목명', 'N/A')
                ret = row.get('수익률(%)', 0)
                value = row.get('평가금액(KRW)', 0)

                st.caption(f"**{name}**: {ret:+.1f}% (₩{value/1e6:.0f}M)")

    st.divider()

    # === SECTION 3: Quick Actions ===
    st.markdown("<p class='panel-header'>⚡ 빠른 액션</p>", unsafe_allow_html=True)

    col_a1, col_a2, col_a3 = st.columns(3)

    with col_a1:
        if st.button("📊 포트폴리오 분석", use_container_width=True):
            st.session_state.nav_target = "portfolio"
            st.rerun()

    with col_a2:
        if st.button("🔍 종목 분석", use_container_width=True):
            st.session_state.nav_target = "stock_analysis"
            st.rerun()

    with col_a3:
        if st.button("🌍 시장 정보", use_container_width=True):
            st.session_state.nav_target = "market"
            st.rerun()

    st.divider()

    # === SECTION 4: Recent Activity ===
    st.markdown("<p class='panel-header'>📝 최근 활동</p>", unsafe_allow_html=True)

    if 'ai_insights' in st.session_state:
        st.markdown("**🧠 최근 AI 분석**")
        st.markdown(st.session_state.ai_insights[:300] + "...")
        st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("아직 AI 분석 기록이 없습니다. 포트폴리오 분석을 실행해보세요.")

    if 'current_stock_analysis' in st.session_state:
        st.divider()
        analysis = st.session_state.current_stock_analysis
        ticker = analysis.get('ticker', 'N/A')
        name = analysis.get('summary', {}).get('name', 'N/A')
        st.markdown(f"**🔍 최근 분석 종목**: {name} ({ticker})")

    st.divider()
    st.caption("💡 팁: 왼쪽 사이드바에서 원하는 페이지로 이동할 수 있습니다")
