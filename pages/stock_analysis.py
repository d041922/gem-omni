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
        st.markdown(f"#### 📰 {ticker_only} 관련 주요 소식")
        news_manager = NewsManager(orchestrator)
        news_key = f"news_{ticker_only}"
        if st.button("🔄 뉴스 갱신", key="force_news"):
            del st.session_state[news_key]
            st.rerun()
        if news_key not in st.session_state:
            with st.spinner("정보 수집 중..."):
                st.session_state[news_key] = news_manager.fetch_ticker_news(ticker_only)
        ticker_news = st.session_state[news_key]
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
        if st.button(
            "🚀 전문가 토론 리포트 생성",
            key="btn_generate_report",
            use_container_width=True,
            type="primary",
        ):
            with st.spinner("분석 중..."):
                pdf_bytes = research.get_report_with_cache(ticker_only)
                if pdf_bytes:
                    st.download_button(
                        "📥 PDF 분석서 다운로드",
                        pdf_bytes,
                        f"OMNI_Analysis_{ticker_only}.pdf",
                        "application/pdf",
                        use_container_width=True,
                    )
                    st.success("리포트 생성이 완료되었습니다.")
                else:
                    st.error("리포트 생성에 실패했습니다.")


if __name__ == "__main__":
    render_stock_analysis()
