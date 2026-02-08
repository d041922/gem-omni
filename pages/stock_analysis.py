"""
GEM: OMNI - Stock Analysis Terminal v5.3 (Modular Architecture)
Synchronized with Central Data Hub (SSOT).
Refactored to use modular tabs (pages/analysis_tabs) for Zero Regression.
Strictly verified via Triple-Lock Pipeline.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from skills.data_orchestrator import DataOrchestrator
from skills.market_screener import MarketScreener
from skills.news_manager import NewsManager
from skills.research_engine import ResearchEngine
from skills.ticker_search import TickerSearchEngine
from skills.news_analyzer import get_analyst_ratings, analyze_news_sentiment
from pages.style_utils import load_custom_css

# Import Analysis Modules
from pages.analysis_tabs.technical import render_technical_tab
from pages.analysis_tabs.fundamental import render_fundamental_tab


def render_top_navigator():
    cols = st.columns(4)
    menu = [
        ("🏠 전체 홈", "home"),
        ("🌍 시장 현황", "market"),
        ("🎯 종목 발굴", "screener"),
        ("🔍 종목 분석", "analysis"),
    ]
    curr = st.session_state.get("current_page", "analysis")
    for i, (label, page) in enumerate(menu):
        with cols[i]:
            if st.button(
                label,
                use_container_width=True,
                type="primary" if curr == page else "secondary",
            ):
                if curr != page:
                    st.session_state.current_page = page
                    st.rerun()
    st.divider()


def render_stock_analysis():
    load_custom_css()
    orchestrator = DataOrchestrator()
    search_engine = TickerSearchEngine()
    screener = MarketScreener(orchestrator)
    research = ResearchEngine()

    render_top_navigator()

    # [DEBUG] Portfolio Sync Sidebar
    with st.sidebar:
        st.markdown("### 🛠️ 데이터 관리")
        if st.button("🔄 포트폴리오 강제 동기화", use_container_width=True):
            with st.spinner("GSheet 동기화 중..."):
                if orchestrator.sync_portfolio():
                    st.success("동기화 완료!")
                    st.rerun()
                else:
                    st.error("동기화 실패")

        # 보유 종목 리스트 미리보기 (디버깅용)
        state = orchestrator.read_state()
        holdings = state.get("data", {}).get("portfolio", {}).get("holdings", [])
        with st.expander("📦 보유 종목 캐시 현황"):
            for h in holdings:
                st.write(f"- {h['ticker']}: {h['quantity']}주")

    # 1. Search Header
    st.markdown("### 🔍 종목 정밀 리서치")
    col_search, col_status = st.columns([2, 1])

    with col_search:
        search_query = st.text_input(
            "종목 검색 (명칭/티커)",
            value="NVDA",
            key="stock_search_input",
            label_visibility="collapsed",
        ).strip()
        candidates = search_engine.search_symbols(search_query)
        if candidates:
            options = [f"{c['name']} ({c['symbol']})" for c in candidates]
            selected_option = st.selectbox(
                "결과:",
                options,
                key="stock_search_select",
                label_visibility="collapsed",
            )
            selected_data = candidates[options.index(selected_option)]
            tv_symbol = search_engine.to_tradingview_format(
                selected_data["symbol"], selected_data["exchange"]
            )
            ticker_only = selected_data["symbol"]
        else:
            st.warning("종목을 찾을 수 없습니다.")
            return

    # [Machine Domain] 데이터 수집 및 국가별 통화 설정
    ticker_info = orchestrator.get_full_ticker_data(ticker_only)
    h_chart = pd.DataFrame.from_dict(ticker_info.get("history", {}))
    is_ready = ticker_info.get("is_ready", False)
    owned = ticker_info.get("holding_info")
    last_p = ticker_info.get("last_price", 0)
    extra = ticker_info.get("extra_stats", {})
    market_context = ticker_info.get("market_context", {})

    is_kr = ".KS" in ticker_only.upper() or ".KQ" in ticker_only.upper()
    cur_sym = "₩" if is_kr else "$"
    p_fmt = ",.0f" if is_kr else ",.2f"

    with col_status:
        if owned:
            avg_p = owned.get("average_price", 0)
            pnl_pct = ((last_p - avg_p) / avg_p * 100) if avg_p > 0 else 0
            color = "#FF4B4B" if pnl_pct > 0 else "#3182F6"
            st.markdown(
                f"""
                <div class='glass-card' style='padding:15px; border-left: 5px solid {color};'>
                    <div style='font-size:0.8rem; color:#8B949E;'>✅ SSOT 포트폴리오 연동</div>
                    <div style='font-size:1.2rem; font-weight:bold;'>{owned.get("quantity", 0):,.1f}주 보유</div>
                    <div style='display:flex; justify-content:space-between; margin-top:5px;'>
                        <span style='font-size:0.9rem; color:#8B949E;'>평단: {cur_sym}{avg_p:{p_fmt}}</span>
                        <span style='font-size:1.1rem; font-weight:bold; color:{color};'>{pnl_pct:+.2f}%</span>
                    </div>
                    <div style='font-size:1.4rem; font-weight:bold; margin-top:8px; color:white;'>현재가: {cur_sym}{last_p:{p_fmt}}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='glass-card' style='padding:15px; opacity:0.6;'>⚪ 포트폴리오 미보유 종목</div>",
                unsafe_allow_html=True,
            )

    # 2. Main Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 실시간 차트", "📊 기술 분석", "🏛️ 펀더멘털", "📰 뉴스", "🤖 AI 리서치"]
    )

    with tab1:
        components.html(
            f'<div style="height:600px;width:100%"><script src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>{{ "width": "100%", "height": "600", "symbol": "{tv_symbol}", "interval": "D", "theme": "dark", "style": "1", "locale": "kr" }}</script></div>',
            height=600,
        )

    with tab2:
        render_technical_tab(
            ticker_only, h_chart, market_context, is_ready, cur_sym, p_fmt, last_p
        )

    with tab3:
        render_fundamental_tab(ticker_only, screener, extra, last_p, owned)

    with tab4:
        st.markdown(f"#### 📰 {ticker_only} 전략적 심리 및 컨센서스")

        # 1. Analyst & Sentiment Summary (Investing.com Style)
        analyst_data = get_analyst_ratings(ticker_only)
        news_manager = NewsManager(orchestrator)
        news_key = f"news_{ticker_only}"

        if news_key not in st.session_state:
            with st.spinner("최신 뉴스 분석 중..."):
                st.session_state[news_key] = news_manager.fetch_ticker_news(ticker_only)
        ticker_news = st.session_state[news_key]

        # Aggregate Sentiment Calculation
        agg_sentiment = analyze_news_sentiment(
            [{"title": n["headline"]} for n in ticker_news], ticker_only
        )

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            consensus = analyst_data.get("consensus", "N/A")
            color_map = {
                "Buy": "#FF4B4B",
                "Strong Buy": "#FF4B4B",
                "Sell": "#3182F6",
                "Strong Sell": "#3182F6",
                "Hold": "#8B949E",
            }
            c_color = color_map.get(consensus, "white")

            st.markdown(
                f"""
                <div class='glass-card' style='padding:15px; text-align:center;'>
                    <div style='font-size:0.9rem; color:#8B949E;'>애널리스트 컨센서스</div>
                    <div style='font-size:1.8rem; font-weight:bold; color:{c_color};'>{consensus}</div>
                    <div style='font-size:0.8rem; margin-top:5px;'>총 {analyst_data.get("total_analysts", 0)}명 참여</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col_c2:
            st.markdown(
                f"""
                <div class='glass-card' style='padding:15px; text-align:center;'>
                    <div style='font-size:0.9rem; color:#8B949E;'>최근 뉴스 심리 (Exa AI)</div>
                    <div style='font-size:1.8rem; font-weight:bold;'>{agg_sentiment}</div>
                    <div style='font-size:0.8rem; margin-top:5px;'>최근 {len(ticker_news)}건 분석 결과</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        if analyst_data.get("status") == "success":
            target_mean = analyst_data.get("target_mean", 0)
            target_high = analyst_data.get("target_high", 0)
            target_low = analyst_data.get("target_low", 0)
            upside_val = analyst_data.get("upside_pct", 0)
            up_color = "#FF4B4B" if upside_val > 0 else "#3182F6"

            st.markdown(
                f"""
                <div class='glass-card' style='padding:15px; margin-top:15px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <span style='font-size:1rem; font-weight:bold;'>🎯 목표 주가 (12개월)</span>
                        <span style='font-size:1.2rem; font-weight:bold; color:{up_color};'>Upside {upside_val:+.1f}%</span>
                    </div>
                    <div style='display:flex; justify-content:space-between; margin-top:10px; font-size:0.85rem; color:#8B949E;'>
                        <span>최저 {cur_sym}{target_low:{p_fmt}}</span>
                        <span>평균 {cur_sym}{target_mean:{p_fmt}}</span>
                        <span>최고 {cur_sym}{target_high:{p_fmt}}</span>
                    </div>
                    <div style='height:8px; background:#161B22; border-radius:4px; margin-top:8px; position:relative;'>
                        <div style='position:absolute; left:0%; width:100%; height:100%; background:linear-gradient(90deg, #3182F6, #FF4B4B); opacity:0.3; border-radius:4px;'></div>
                        <div style='position:absolute; left:{(last_p - target_low) / (target_high - target_low) * 100 if (target_high - target_low) > 0 else 50}%; width:4px; height:120%; background:white; top:-10%; box-shadow:0 0 5px white;'></div>
                    </div>
                    <div style='text-align:center; font-size:0.75rem; color:#8B949E; margin-top:5px;'>현재가 위치 ({cur_sym}{last_p:{p_fmt}})</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown("#### 📰 실시간 뉴스 타임라인")
        if st.button("🔄 뉴스 갱신", key="force_news"):
            del st.session_state[news_key]
            st.rerun()

        if ticker_news:
            for n in ticker_news:
                st.markdown(
                    f"<div style='margin-bottom:15px; padding:15px; background:rgba(255,255,255,0.02); border-radius:10px; border-left: 4px solid #3182F6;'><b>{n['headline']}</b><br><span style='color:#8B949E; font-size:0.8rem;'>분석: {n['sentiment']}</span><p style='font-size:0.85rem; margin-top:5px;'>{n['summary']}</p></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("관련 뉴스가 없습니다.")

    with tab5:
        st.markdown("#### 🤖 AI 전문가 협의체 보고서")

        # 1. Report Status & Metadata Display
        research_key = f"research_{ticker_only}"

        if st.button(
            "🚀 전문가 토론 리포트 생성/갱신",
            key="btn_generate_report",
            use_container_width=True,
            type="primary",
        ):
            with st.spinner("전문가 위원회 소집 및 토론 중..."):
                st.session_state[research_key] = research.get_report_with_cache(
                    ticker_only, force_refresh=True
                )

        # Display cached result if available
        if research_key not in st.session_state:
            # Try to load from cache without force refresh
            res = research.get_report_with_cache(ticker_only)
            if res:
                st.session_state[research_key] = res

        if research_key in st.session_state:
            res = st.session_state[research_key]
            pdf_bytes = res.get("pdf")
            meta = res.get("metadata", {})

            # 1. Top Briefing (Verdict & Portfolio Advice)
            v_color = (
                "#FF4B4B"
                if "BUY" in meta.get("verdict", "")
                else "#3182F6"
                if "SELL" in meta.get("verdict", "")
                else "#8B949E"
            )

            col_v1, col_v2 = st.columns([1, 2])
            with col_v1:
                st.markdown(
                    f"""
                    <div class='glass-card' style='padding:20px; border-left: 10px solid {v_color}; text-align:center;'>
                        <div style='font-size:0.9rem; color:#8B949E;'>최종 투자의견</div>
                        <div style='font-size:2.2rem; font-weight:bold; color:{v_color};'>{meta.get("verdict", "N/A")}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            with col_v2:
                st.markdown(
                    f"""
                    <div class='glass-card' style='padding:20px; border-left: 5px solid #FFD700;'>
                        <div style='font-size:0.9rem; color:#8B949E;'>🛡️ 마스터 포트폴리오 조언</div>
                        <div style='font-size:1.05rem; font-weight:bold; margin-top:5px;'>{meta.get("portfolio_advice", "N/A")}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            # 2. Key Action Strategy
            st.markdown(
                f"""
                <div class='glass-card' style='padding:20px; margin-top:15px; background:rgba(49, 130, 246, 0.05);'>
                    <div style='font-size:0.9rem; color:#8B949E; margin-bottom:10px;'>🎯 핵심 대응 전략 (Action Plan)</div>
                    <div style='font-size:1.1rem; line-height:1.6;'>{meta.get("action_plan", "N/A")}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

            # 3. Detailed Debate (The Clash)
            with st.expander("🏛️ 위원회 끝장 토론 상세 및 논쟁점 보기", expanded=False):
                st.markdown(
                    f"""
                    <div style='background:rgba(255,255,255,0.03); padding:15px; border-radius:10px;'>
                        <div style='font-size:0.9rem; color:#8B949E; margin-bottom:5px;'>🔥 핵심 논쟁점 (Battle Ground)</div>
                        <div style='font-size:1.1rem; font-weight:bold; color:#FF4B4B;'>{meta.get("battle_ground", "N/A")}</div>
                    </div>
                    <div style='margin-top:15px;'>
                        <div style='font-size:0.9rem; color:#8B949E; margin-bottom:5px;'>💡 위원회 토론 요약</div>
                        <div style='font-size:1rem; line-height:1.6;'>{meta.get("ai_summary", "N/A")}</div>
                    </div>
                    <div style='margin-top:15px;'>
                        <div style='font-size:0.9rem; color:#8B949E; margin-bottom:5px;'>⚖️ 최종 결정 근거</div>
                        <div style='font-size:0.95rem; color:#C9D1D9;'>{meta.get("reason", "N/A")}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            if pdf_bytes:
                st.download_button(
                    "📥 상세 PDF 리포트 다운로드 (전문가 버전)",
                    pdf_bytes,
                    f"OMNI_Analysis_{ticker_only}.pdf",
                    "application/pdf",
                    use_container_width=True,
                )
        else:
            st.info(
                "전문가 리포트가 생성되지 않았습니다. 위 버튼을 눌러 분석을 시작하십시오."
            )


if __name__ == "__main__":
    render_stock_analysis()
