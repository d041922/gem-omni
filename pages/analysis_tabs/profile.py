"""
Company Profile Module
Renders business overview, SWOT analysis, and Economic Moat.
Now focused on 'Ingredients' for analysis.
"""

import streamlit as st
from typing import Dict, Any
from skills.research_engine import ResearchEngine


def render_profile_tab(ticker: str, ticker_info: Dict[str, Any]):
    """
    Renders the Company Profile tab (Tab 1).
    Focuses on 'Foundational Facts' and 'AI Strategic Ingredients'.
    """
    extra = ticker_info.get("extra_stats", {})
    profile = extra.get("profile", {})
    financials = extra.get("financials", {})
    research = ResearchEngine()

    # 1. Identity Header (Cleaned up, No Logo)
    st.markdown(f"### 🏢 {ticker_info.get('name', ticker)} ({ticker})")
    col_meta1, col_meta2 = st.columns([2, 1])

    with col_meta1:
        st.markdown(
            f"**{profile.get('sector', 'N/A')}** | {profile.get('industry', 'N/A')}"
        )
        emp_count = profile.get("employees")
        emp_display = f"{emp_count:,}" if isinstance(emp_count, (int, float)) else "N/A"
        st.markdown(f"👥 {emp_display} Employees | 📍 {profile.get('location', 'N/A')}")

    with col_meta2:
        st.markdown(
            f"<div style='text-align:right;'>🌐 <a href='{profile.get('website', '#')}'>Official Website</a></div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # 2. AI Quick Insight (Foundational Ingredients)
    with st.spinner("AI가 비즈니스 모델을 해부하는 중..."):
        insight = research.get_quick_insight(ticker, profile.get("full_summary", ""))

    # [A] Korean Summary
    st.markdown("#### 📜 비즈니스 요약 (Core Business)")
    st.info(insight.get("summary_kr", "요약을 가져올 수 없습니다."))

    # [B] Strategic Ingredients (Pillars & Moat)
    col_ins1, col_ins2 = st.columns(2)

    with col_ins1:
        st.markdown("#### 🏰 경제적 해자 (Moat)")
        st.markdown(
            f"""
            <div style='background:rgba(49, 130, 246, 0.05); padding:15px; border-radius:10px; border-left: 5px solid #3182F6;'>
                <b style='color:#3182F6; font-size:1.1rem;'>{insight.get("moat", "분석 중")}</b>
                <p style='font-size:0.85rem; margin-top:10px; color:#8B949E;'>이 해자 유형은 위원회 분석의 핵심 근거로 사용됩니다.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col_ins2:
        st.markdown("#### 🔑 핵심 전략 요소 (Key Pillars)")
        pillars = insight.get("pillars", ["데이터 없음"])
        pill_html = "".join(
            [
                f"<span style='background:#21262d; padding:4px 10px; border-radius:15px; border:1px solid #30363d; font-size:0.85rem; margin-right:5px; margin-bottom:5px; display:inline-block;'>#{p}</span>"
                for p in pillars
            ]
        )
        st.markdown(pill_html, unsafe_allow_html=True)

    st.divider()

    # 3. Market 체급 (Market Stats)
    st.markdown("#### 📊 마켓 체급 (Market Stats)")
    m_cols = st.columns(3)

    m_cap = financials.get("market_cap", 0)
    if m_cap > 1e12:
        m_cap_str = f"{m_cap / 1e12:.2f}T"
    elif m_cap > 1e9:
        m_cap_str = f"{m_cap / 1e9:.2f}B"
    else:
        m_cap_str = f"{m_cap:,}"

    with m_cols[0]:
        st.metric("시가총액", m_cap_str)
    with m_cols[1]:
        st.metric(
            "배당 수익률",
            f"{financials.get('dividend_yield', 0) * 100:.2f}%"
            if financials.get("dividend_yield")
            else "0.00%",
        )
    with m_cols[2]:
        st.metric(
            "수익성 (ROE)",
            f"{financials.get('roe', 0) * 100:.1f}%"
            if financials.get("roe")
            else "N/A",
        )
