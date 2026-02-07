"""
GEM: OMNI - Stock Analysis Terminal v5.2 (Unified Integrity)
Synchronized with Central Data Hub (SSOT).
Complete restoration of Technical Analysis (v4.7) + Fundamental Mastery (v5.1).
Strictly verified via Triple-Lock Pipeline.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from skills.data_orchestrator import DataOrchestrator
from skills.market_screener import MarketScreener
from skills.quant_engine import FactorEngine
from skills.news_manager import NewsManager
from skills.research_engine import ResearchEngine
from skills.ticker_search import TickerSearchEngine
from skills.chart_tools import ChartEngine
from pages.style_utils import load_custom_css


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
        if is_ready and len(h_chart) > 1:
            report = FactorEngine.generate_strategic_analysis(
                ticker_only, last_p, h_chart, market_context
            )
            pivots = FactorEngine.calculate_pivot_points(h_chart.iloc[-1])
            st.markdown("#### 📜 기술적 시장 전략 분석 (Strategic Report)")
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

    with tab3:
        st.markdown("#### 🏛️ 기업 내재가치 및 펀더멘털 분석 (Fundamentals)")
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
                st.table(pd.DataFrame(report_data))
            else:
                st.info("상세 리포트 생성을 위한 데이터가 부족합니다.")
        with f_col2:
            st.markdown("##### 💎 핵심 지표 대시보드")
            fin = extra.get("financials", {})
            growth = extra.get("growth", {})
            val = extra.get("valuation", {})
            c1, c2 = st.columns(2)
            c1.metric(
                "ROE", f"{(fin.get('roe', 0) * 100):.1f}%" if fin.get("roe") else "N/A"
            )
            c2.metric(
                "PEG Ratio",
                f"{growth.get('peg_ratio', 0):.2f}"
                if growth.get("peg_ratio")
                else "N/A",
            )
            st.divider()
            v1, v2 = st.columns(2)
            v1.metric(
                "P/E (Trailing)",
                f"{val.get('trailing_pe', 0):.1f}x"
                if val.get("trailing_pe")
                else "N/A",
            )
            v2.metric(
                "P/S Ratio",
                f"{val.get('ps_ratio', 0):.1f}x" if val.get("ps_ratio") else "N/A",
            )
            st.divider()
            analyst = extra.get("analyst_opinions", {})
            if analyst:
                mean_t = analyst.get("target_mean", 0)
                upside = ((mean_t - last_p) / last_p * 100) if last_p > 0 else 0
                st.metric(
                    "평균 목표가", f"{cur_sym}{mean_t:{p_fmt}}", f"{upside:+.2f}% 여력"
                )
                st.write(
                    f"추천 등급: **{analyst.get('recommendation', 'N/A').upper()}**"
                )

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
