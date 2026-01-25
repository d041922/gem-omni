"""
Settings Page - User Personalization
"""
import streamlit as st
from core.memory import MemorySystem


def render_settings_page():
    """Render user settings and personalization page"""
    st.title("⚙️ 개인화 설정")

    # Initialize memory system
    if 'memory' not in st.session_state:
        st.session_state.memory = MemorySystem()

    memory = st.session_state.memory
    profile = memory.user_profile

    st.markdown("### 투자 프로필")
    st.caption("AI 분석 시 개인 투자 성향과 목표를 반영합니다.")

    # Investment Goal
    investment_goal = st.text_input(
        "투자 목표",
        value=profile.get("investment_goal", "장기 자산 증식"),
        help="예: 은퇴 자금 마련, 주택 구입, 자녀 교육비 등"
    )

    # Risk Tolerance
    col1, col2 = st.columns(2)
    with col1:
        risk_tolerance = st.selectbox(
            "위험 성향",
            options=["보수적", "중간", "공격적"],
            index=["보수적", "중간", "공격적"].index(profile.get("risk_tolerance", "중간")),
            help="보수적: 안정성 우선 | 중간: 균형 | 공격적: 고수익 추구"
        )

    with col2:
        investment_horizon = st.selectbox(
            "투자 기간",
            options=["단기 (<3년)", "중기 (3-10년)", "장기 (>10년)"],
            index=["단기 (<3년)", "중기 (3-10년)", "장기 (>10년)"].index(profile.get("investment_horizon", "장기 (>10년)")),
            help="투자 자금을 회수할 예상 시기"
        )

    # Preferred Strategy
    preferred_strategy = st.selectbox(
        "선호 전략",
        options=["가치 투자", "성장 투자", "배당 투자", "퀀트 투자", "혼합"],
        index=["가치 투자", "성장 투자", "배당 투자", "퀀트 투자", "혼합"].index(profile.get("preferred_strategy", "가치 투자")),
        help="가치: 저평가 종목 | 성장: 고성장 기업 | 배당: 배당 수익 | 퀀트: 수치 기반"
    )

    st.divider()
    st.markdown("### 리스크 관리 기준")

    col3, col4, col5 = st.columns(3)
    with col3:
        max_single = st.slider(
            "단일 종목 최대 비중",
            min_value=5,
            max_value=30,
            value=profile.get("max_single_position", 15),
            step=1,
            help="한 종목이 포트폴리오에서 차지할 수 있는 최대 비중 (%)"
        )

    with col4:
        max_sector = st.slider(
            "섹터 최대 집중도",
            min_value=20,
            max_value=50,
            value=profile.get("max_sector_concentration", 30),
            step=5,
            help="한 섹터가 포트폴리오에서 차지할 수 있는 최대 비중 (%)"
        )

    with col5:
        rebal_threshold = st.slider(
            "리밸런싱 기준",
            min_value=3,
            max_value=15,
            value=profile.get("rebalancing_threshold", 5),
            step=1,
            help="목표 비중에서 벗어나면 리밸런싱 제안 (%)"
        )

    st.divider()

    # Save button
    if st.button("💾 설정 저장", type="primary", use_container_width=True):
        # Update profile
        memory.user_profile.update({
            "investment_goal": investment_goal,
            "risk_tolerance": risk_tolerance,
            "investment_horizon": investment_horizon,
            "preferred_strategy": preferred_strategy,
            "max_single_position": max_single,
            "max_sector_concentration": max_sector,
            "rebalancing_threshold": rebal_threshold
        })

        # Save to file
        memory.save_all_memory()
        st.success("✅ 설정이 저장되었습니다!")
        st.balloons()

    # Preview
    st.divider()
    st.markdown("### 📋 현재 설정 요약")
    st.json(memory.user_profile)
