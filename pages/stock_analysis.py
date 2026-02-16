"""
GEM: OMNI - Stock Analysis Terminal v5.3 (Modular Architecture)
Synchronized with Central Data Hub (SSOT).
Refactored to use modular tabs (pages/analysis_tabs) for Zero Regression.
Strictly verified via Triple-Lock Pipeline.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from html import escape, unescape
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
from pages.analysis_tabs.profile import render_profile_tab


def _sanitize_html_text(value: object, *, multiline: bool = False) -> str:
    raw = "" if value is None else str(value)
    normalized = unescape(raw).replace("\r\n", "\n").replace("\r", "\n").strip()
    escaped = escape(normalized, quote=True)
    if multiline:
        return escaped.replace("\n", "<br>")
    return escaped


def _format_as_of(value: object) -> str:
    if not value:
        return "unknown"
    try:
        text = str(value).strip()
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return _sanitize_html_text(value)


def _is_stale_news(value: object, *, stale_hours: int = 72) -> bool:
    if not value:
        return False
    try:
        text = str(value).strip()
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() > stale_hours * 3600
    except Exception:
        return False


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
            with st.spinner("캐시 초기화 및 GSheet 동기화 중..."):
                # [SSOT] 모든 전역 데이터 캐시 강제 삭제
                st.cache_data.clear()
                if orchestrator.sync_portfolio():
                    st.success("동기화 및 캐시 갱신 완료!")
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
        ["🏢 기업 개요", "📈 기술 분석", "🏛️ 펀더멘털", "📰 뉴스", "🤖 AI 리서치"]
    )

    with tab1:
        render_profile_tab(ticker_only, ticker_info)

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
            stale_news_detected = False
            for n in ticker_news:
                headline = _sanitize_html_text(n.get("headline", "No Title"))
                sentiment = _sanitize_html_text(n.get("sentiment", "Neutral"))
                summary = _sanitize_html_text(n.get("summary", ""), multiline=True)
                source = _sanitize_html_text(n.get("source", "Unknown"))
                as_of = _format_as_of(n.get("published_at"))
                url = str(n.get("url", "")).strip()
                link_html = (
                    f"<a href='{escape(url, quote=True)}' target='_blank' rel='noopener noreferrer'>View source</a>"
                    if url.startswith("http://") or url.startswith("https://")
                    else ""
                )
                stale_news_detected = stale_news_detected or _is_stale_news(n.get("published_at"))
                st.markdown(
                    f"""
                    <div style='margin-bottom:15px; padding:15px; background:rgba(255,255,255,0.02); border-radius:10px; border-left: 4px solid #3182F6;'>
                        <b>{headline}</b><br>
                        <span style='color:#8B949E; font-size:0.8rem;'>분석: {sentiment}</span><br>
                        <span style='color:#8B949E; font-size:0.78rem;'>source: {source} | as_of: {as_of} {link_html}</span>
                        <p style='font-size:0.85rem; margin-top:8px;'>{summary}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if stale_news_detected:
                st.warning("일부 뉴스의 시점(as_of)이 72시간 이상 경과했습니다. 최신성 확인 후 판단하세요.")
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
                    ticker_only,
                    force_refresh=True,
                    market_news=ticker_news,
                    ticker_info=ticker_info,
                )

        # Display cached result if available
        if research_key not in st.session_state:
            # Try to load from cache without force refresh
            res = research.get_report_with_cache(
                ticker_only,
                market_news=ticker_news,
                ticker_info=ticker_info,
            )
            if res:
                st.session_state[research_key] = res

        if research_key in st.session_state:
            res = st.session_state[research_key]
            # [Patch v5.3] No PDF support
            meta = res.get("metadata", {})

            # --- Layer 1: Headline Card (The Big Picture) ---
            verdict_raw = str(meta.get("verdict", "N/A"))
            v_color = (
                "#FF4B4B"
                if "BUY" in verdict_raw
                else "#3182F6"
                if "SELL" in verdict_raw
                else "#8B949E"
            )
            verdict = _sanitize_html_text(verdict_raw)
            confidence = _sanitize_html_text(meta.get("confidence_score", "50%"))

            # Fallback for old cache
            headline_raw = meta.get(
                "headline_summary",
                meta.get("ai_summary", "요약 정보 없음")[:50] + "...",
            )
            headline = _sanitize_html_text(headline_raw)

            st.markdown(
                f"""
                <div class='glass-card' style='padding:25px; border-left: 10px solid {v_color}; margin-bottom: 20px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div style='font-size:1.1rem; color:#8B949E; font-weight:600;'>OMNI COUNCIL VERDICT</div>
                        <div style='background:{v_color}20; color:{v_color}; padding:5px 12px; border-radius:20px; font-size:0.9rem; font-weight:bold;'>확신도 {confidence}</div>
                    </div>
                    <div style='font-size:3rem; font-weight:900; color:{v_color}; margin: 10px 0; line-height:1;'>{verdict}</div>
                    <div style='font-size:1.3rem; color:#E6EDF3; font-weight:500; border-top:1px solid rgba(255,255,255,0.1); padding-top:15px; margin-top:5px;'>
                        "{headline}"
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # --- Layer 2: The Visual Clash (Expert Grid) ---
            st.markdown("#### ⚔️ 전문가 협의체 격돌 (The Visual Clash)")

            summary_data = meta.get("dashboard_clash") or meta.get("clash_table", [])

            if summary_data:
                # Use st.columns for stable layout instead of raw CSS Grid string
                for i in range(0, len(summary_data), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(summary_data):
                            c = summary_data[i + j]
                            pos = c.get("position", "NEUTRAL")
                            icon = c.get("icon") or (
                                "🟢"
                                if "BULL" in pos
                                else "🔴"
                                if "BEAR" in pos
                                else "🟡"
                            )

                            logic = _sanitize_html_text(
                                c.get("summary_logic") or c.get("logic", "-")
                            )
                            counter = _sanitize_html_text(
                                c.get("summary_counter") or c.get("counter", "-")
                            )
                            agent = _sanitize_html_text(c.get("agent", "Unknown"))
                            pos_text = _sanitize_html_text(pos)

                            # Color Alignment (Patch v4.6: Traffic Light Consistency)
                            # BULL -> Green, BEAR -> Red, NEUTRAL -> Gray
                            card_color = (
                                "#00D8A5"
                                if "BULL" in pos
                                else "#FF4B4B"
                                if "BEAR" in pos
                                else "#8B949E"
                            )
                            card_bg = (
                                "rgba(0, 216, 165, 0.05)"
                                if "BULL" in pos
                                else "rgba(255, 75, 75, 0.05)"
                                if "BEAR" in pos
                                else "rgba(255, 255, 255, 0.02)"
                            )

                            with cols[j]:
                                st.markdown(
                                    f"""
                                <div style='background:{card_bg}; border:1px solid {card_color}40; border-radius:12px; padding:15px; height:100%; position:relative;'>
                                    <div style='position:absolute; top:12px; right:12px; font-size:1.4rem;'>{icon}</div>
                                    <div style='font-size:0.85rem; font-weight:bold; color:#8B949E; margin-bottom:2px;'>{agent}</div>
                                    <div style='font-size:0.75rem; color:{card_color}; font-weight:bold; margin-bottom:10px;'>{pos_text}</div>
                                    <div style='font-size:0.9rem; line-height:1.4; color:#E6EDF3; margin-bottom:8px;'><b>Logic:</b> {logic}</div>
                                    <div style='font-size:0.85rem; line-height:1.4; color:#8B949E;'><i>Vs: {counter}</i></div>
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )
            else:
                st.info("토론 데이터가 없습니다.")

            st.markdown("<br>", unsafe_allow_html=True)

            # --- Layer 3: Master's Bottom Line (3-Card Dashboard) ---
            st.markdown("#### 🎯 마스터 전용 요약 (The Bottom Line)")

            briefing = meta.get("master_briefing", {})
            details = meta.get("details", {})

            # RR Metrics Row
            rr_tac = _sanitize_html_text(details.get("rr_tactical", "N/A"))
            rr_str = _sanitize_html_text(details.get("rr_strategic", "N/A"))

            rr_cols = st.columns(2)
            with rr_cols[0]:
                st.markdown(f"**⚡ 단기 손익비 (Tactical):** {rr_tac}")
            with rr_cols[1]:
                st.markdown(f"**🎯 전략적 손익비 (Strategic):** {rr_str}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Backward compatibility
            if not briefing and "portfolio_advice" in meta:
                briefing = {
                    "status": meta.get("portfolio_advice"),
                    "risk": "기존 데이터 참조 필요",
                    "strategy": meta.get("action_plan"),
                }

            b_cols = st.columns(3)
            with b_cols[0]:
                st.markdown(
                    f"""
                    <div class='glass-card' style='padding:15px; height:100%; border-top: 3px solid #3182F6;'>
                        <div style='color:#3182F6; font-weight:bold; font-size:1rem; margin-bottom:8px;'>📊 포지션 현황</div>
                        <div style='font-size:0.9rem; line-height:1.5; color:#E6EDF3;'>{_sanitize_html_text(briefing.get("status", "-"))}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with b_cols[1]:
                st.markdown(
                    f"""
                    <div class='glass-card' style='padding:15px; height:100%; border-top: 3px solid #FF4B4B;'>
                        <div style='color:#FF4B4B; font-weight:bold; font-size:1rem; margin-bottom:8px;'>⚠️ 리스크 요인</div>
                        <div style='font-size:0.9rem; line-height:1.5; color:#E6EDF3;'>{_sanitize_html_text(briefing.get("risk", "-"))}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with b_cols[2]:
                st.markdown(
                    f"""
                    <div class='glass-card' style='padding:15px; height:100%; border-top: 3px solid #00D8A5;'>
                        <div style='color:#00D8A5; font-weight:bold; font-size:1rem; margin-bottom:8px;'>🚀 최종 전략</div>
                        <div style='font-size:0.9rem; line-height:1.5; color:#E6EDF3;'>{_sanitize_html_text(briefing.get("strategy", "-"))}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            # --- Layer 4: Action Plan Execution Bar ---
            action = meta.get("action_plan", {})
            if isinstance(action, dict) and any(
                action.get(key) for key in ("wait_price", "entry_price", "profit_price", "stop_price")
            ):
                with st.expander("🛠️ 실행 레벨 가이드 (옵션)", expanded=False):
                    st.markdown(
                        f"""
                        <div style='display:flex; gap:10px; flex-wrap:wrap;'>
                            <div style='flex:1; background:#21262d; padding:10px; border-radius:8px; text-align:center; border:1px solid #30363d;'>
                                <div style='color:#8B949E; font-size:0.8rem;'>✋ 관망/대기</div>
                                <div style='color:#E6EDF3; font-weight:bold;'>{_sanitize_html_text(action.get("wait_price", "-"))}</div>
                            </div>
                            <div style='flex:1; background:rgba(0, 216, 165, 0.1); padding:10px; border-radius:8px; text-align:center; border:1px solid #00D8A5;'>
                                <div style='color:#00D8A5; font-size:0.8rem;'>🛒 진입/매수</div>
                                <div style='color:#E6EDF3; font-weight:bold;'>{_sanitize_html_text(action.get("entry_price", "-"))}</div>
                            </div>
                            <div style='flex:1; background:rgba(49, 130, 246, 0.1); padding:10px; border-radius:8px; text-align:center; border:1px solid #3182F6;'>
                                <div style='color:#3182F6; font-size:0.8rem;'>💰 익절/목표</div>
                                <div style='color:#E6EDF3; font-weight:bold;'>{_sanitize_html_text(action.get("profit_price", "-"))}</div>
                            </div>
                            <div style='flex:1; background:rgba(255, 75, 75, 0.1); padding:10px; border-radius:8px; text-align:center; border:1px solid #FF4B4B;'>
                                <div style='color:#FF4B4B; font-size:0.8rem;'>🛡️ 손절/방어</div>
                                <div style='color:#E6EDF3; font-weight:bold;'>{_sanitize_html_text(action.get("stop_price", "-"))}</div>
                            </div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

            # Deep Dive Expander: Show FULL debate here
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander(
                "🔍 위원회 토론 전문 보기 (Deep Dive / 검수용)", expanded=False
            ):
                # 1. AI Summary
                st.markdown(
                    f"**💡 의사결정 요약**: {_sanitize_html_text(meta.get('ai_summary', '내용 없음'))}"
                )
                st.markdown("---")

                # 2. Full Debate Text (Clash Table Original)
                full_clash = meta.get("clash_table", [])
                if full_clash:
                    for fc in full_clash:
                        st.markdown(f"#### {_sanitize_html_text(fc.get('agent', 'Expert'))}")
                        st.info(f"**주장(Logic):** {_sanitize_html_text(fc.get('logic', '-'))}")
                        st.warning(f"**반박(Counter):** {_sanitize_html_text(fc.get('counter', '-'))}")
                        st.divider()

                # Show F-Score Quality Badge
                f_rating = (
                    meta.get("details", {}).get("f_score_rating")
                    or ticker_info.get("details", {}).get("f_score_rating")
                    or "N/A"
                )
                st.markdown(
                    f"""
                    <div style='margin-top:15px; padding:10px; background:rgba(0, 216, 165, 0.1); border-radius:8px;'>
                        <b>💎 재무 퀄리티 진단 (F-Score):</b> {_sanitize_html_text(f_rating)}
                    </div>
                """,
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    render_stock_analysis()
