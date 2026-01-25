"""
Home Dashboard - Main landing page
Combines market overview, portfolio summary, and quick actions
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from skills.portfolio_utils import load_portfolio_data


def render_home_page():
    """Render home dashboard page"""
    st.markdown("# 💎 GEM: OMNI Command Center")
    st.markdown("**당신의 포트폴리오를 위한 지능형 AI 자산 관리 시스템**")

    st.divider()

    # === SECTION 0: Agent Strategic Briefing (NEW) ===
    from skills.agent_briefing import AgentBriefing
    
    # Aggregating Context
    market_data = st.session_state.get('market_data_cache', {}) # Use cache if available
    if not market_data:
        # Fallback fetch if not in session
        from skills.finance_tools import fetch_market_data
        market_data = fetch_market_data()
        st.session_state.market_data_cache = market_data

    portfolio_df = st.session_state.get('calculated_portfolio', pd.DataFrame())
    cash_df = st.session_state.get('cash_df', pd.DataFrame())
    
    briefing_engine = AgentBriefing(portfolio_df, cash_df, market_data)
    briefing = briefing_engine.generate_briefing()

    st.markdown(f"### 🤖 에이전트 전략 브리핑")
    
    with st.container():
        # Display Summary
        st.info(f"**오늘의 보고**: {briefing['summary']}")
        
        # Display Nudges in columns
        if briefing['nudges']:
            cols = st.columns(len(briefing['nudges']) if len(briefing['nudges']) <= 3 else 3)
            for i, nudge in enumerate(briefing['nudges'][:3]): # Show top 3
                with cols[i]:
                    st.markdown(f"""
                    <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 15px; height: 180px;">
                        <p style="font-weight: bold; color: #58A6FF; margin-bottom: 5px;">{nudge['title']}</p>
                        <p style="font-size: 0.85rem; color: #8B949E;">{nudge['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.caption(f"최종 업데이트: {briefing['timestamp']}")

    st.divider()

    # === SECTION 1: Quick Stats (Asset Summary) ===
    st.markdown("<p class='panel-header'>📊 자산 현황 요약</p>", unsafe_allow_html=True)

    if 'calculated_portfolio' not in st.session_state:
        load_portfolio_data()

    if 'calculated_portfolio' in st.session_state and not st.session_state.calculated_portfolio.empty:
        result_df = st.session_state.calculated_portfolio
        
        # 1.1 Calculate Stock Stats
        total_stock_cost = result_df['매수금액(KRW)'].sum()
        total_stock_value = result_df['평가금액(KRW)'].sum()
        stock_profit = result_df['손익(KRW)'].sum()
        stock_return = (stock_profit / total_stock_cost * 100) if total_stock_cost > 0 else 0

        # 1.2 Fetch Cash Data from session state
        cash_df = st.session_state.get('cash_df', pd.DataFrame())
        total_cash = 0
        if not cash_df.empty:
            # 금액 컬럼 찾기 (한글/영문/공백 대응)
            amount_col = None
            for col in ['금액', 'amount', '금액(KRW)', 'Amount']:
                if col in cash_df.columns:
                    amount_col = col
                    break
            
            if amount_col:
                total_cash = pd.to_numeric(cash_df[amount_col], errors='coerce').sum()

        # 1.3 Total Asset
        total_asset = total_stock_value + total_cash

        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 자산", f"₩{total_asset/1e8:.2f}억")
        col2.metric("보유 주식", f"₩{total_stock_value/1e8:.2f}억", f"{stock_return:+.1f}%")
        col3.metric("보유 현금", f"₩{total_cash/1e6:.0f}백만")
        col4.metric("종목 수", f"{len(result_df)}개")

        # 1.4 Core/Satellite Quick View
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
            core_v = result_df[result_df['asset_type'] == 'Core']['평가금액(KRW)'].sum()
            core_p = (core_v / total_stock_value * 100) if total_stock_value > 0 else 0
            st.metric("💎 Core 주식", f"₩{core_v/1e8:.2f}억", f"{core_p:.1f}%")
            st.caption("목표: 50-60%")
        with col_sat:
            sat_v = result_df[result_df['asset_type'] == 'Satellite']['평가금액(KRW)'].sum()
            sat_p = (sat_v / total_stock_value * 100) if total_stock_value > 0 else 0
            st.metric("🚀 Satellite 주식", f"₩{sat_v/1e8:.2f}억", f"{sat_p:.1f}%")
            st.caption("목표: 40-50%")

    else:
        st.info("데이터를 불러오는 중입니다...")
        if st.button("📊 데이터 새로고침", type="primary"):
            load_portfolio_data(force_refresh=True)
            st.rerun()

    st.divider()

    # === SECTION 2: Highlights ===
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<p class='panel-header'>🏆 수익률 Top 3</p>", unsafe_allow_html=True)
        if 'calculated_portfolio' in st.session_state:
            top_3 = result_df.nlargest(3, '수익률(%)')
            for _, row in top_3.iterrows():
                st.success(f"**{row['종목명']}**: {row['수익률(%)']:+.1f}%")
        else: st.caption("데이터 없음")

    with col_right:
        st.markdown("<p class='panel-header'>📝 최근 활동</p>", unsafe_allow_html=True)
        if 'ai_insights' in st.session_state:
            insight_summary = st.session_state.ai_insights[:150].replace('\n', ' ') + "..."
            st.info(f"**AI 분석**: {insight_summary}")
            st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        else:
            st.caption("최근 실행된 AI 분석 결과가 없습니다. '포트폴리오 관리'에서 분석을 실행하세요.")

    st.divider()

    # === SECTION 3: Quick Actions ===
    st.markdown("<p class='panel-header'>⚡ 빠른 메뉴</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 포트폴리오 분석", use_container_width=True):
            st.session_state.nav_target = "portfolio"; st.rerun()
    with c2:
        if st.button("🔍 종목 심층 분석", use_container_width=True):
            st.session_state.nav_target = "stock_analysis"; st.rerun()
    with c3:
        if st.button("🌍 시장 정보 확인", use_container_width=True):
            st.session_state.nav_target = "market"; st.rerun()

    if 'current_stock_analysis' in st.session_state:
        st.divider()
        ana = st.session_state.current_stock_analysis
        ticker = ana.get('ticker', 'N/A')
        name = ana.get('summary', {}).get('name', 'N/A')
        price = ana.get('summary', {}).get('current_price', 0)
        change = ana.get('summary', {}).get('price_change_pct', 0)
        
        st.markdown(f"**🔍 최근 분석 종목**: {name} ({ticker}) | 현재가: ${price:.2f} ({change:+.2f}%) ")
        if st.button(f"👉 {name} 분석 페이지로 이동", type="secondary"):
            st.session_state.nav_target = "stock_analysis"; st.rerun()