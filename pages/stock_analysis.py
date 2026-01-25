"""
Single Stock Analysis Page (한글 버전)
Token-optimized deep analysis for individual stocks
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, Dict, Any
from skills.stock_analyzer import analyze_stock, generate_ai_analysis
from agents.crews.stock_analysis_crew import run_stock_analysis


@st.cache_data(ttl=1800)  # 30분 캐싱 - 같은 종목 재분석 시 토큰 절약
def cached_analyze_stock(ticker: str, period: str):
    """Cached stock analysis to prevent duplicate API calls"""
    return analyze_stock(ticker, period)


# Removed: check_portfolio_holding() moved to skills/portfolio_utils.py
# Import from unified utility instead
from skills.portfolio_utils import check_portfolio_holding


def render_stock_analysis_page():
    """Render single stock analysis page"""
    st.markdown("<p class='panel-header'>🔍 개별 종목 심층 분석</p>", unsafe_allow_html=True)

    # Input section
    col_input, col_period = st.columns([3, 1])
    with col_input:
        ticker_input = st.text_input(
            "종목 티커 입력",
            value=st.session_state.get('last_ticker', ''),
            placeholder="미국: AAPL, NVDA | 한국: 005930.KS (삼성전자)",
            help="미국 주식: AAPL, NVDA 등 | 한국 주식: 종목코드.KS (예: 005930.KS)"
        ).upper().strip()

    with col_period:
        period = st.selectbox(
            "분석 기간",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,  # Default: 1y
            key='stock_period'
        )

    analyze_button = st.button("🚀 종목 분석", width="stretch", type="primary")

    # Check if we have existing analysis in session state
    show_results = False
    ticker = ticker_input

    if analyze_button and ticker:
        # New analysis requested
        st.session_state.last_ticker = ticker
        st.session_state.last_period = period
        show_results = True
    elif 'current_stock_analysis' in st.session_state and ticker == st.session_state.get('last_ticker', ''):
        # Show existing analysis
        show_results = True
        ticker = st.session_state.last_ticker
        period = st.session_state.get('last_period', '1y')

    if not show_results:
        st.info("👆 종목 티커를 입력하고 '종목 분석' 버튼을 클릭하세요")

        # Example tickers - US stocks
        st.markdown("### 📊 미국 인기 종목")
        example_cols = st.columns(5)
        examples = ["AAPL", "NVDA", "MSFT", "TSLA", "GOOGL"]
        for idx, ex_ticker in enumerate(examples):
            if example_cols[idx].button(ex_ticker, width="stretch", key=f"ex_us_{ex_ticker}"):
                st.session_state.last_ticker = ex_ticker
                st.session_state.last_period = "1y"
                st.rerun()

        # Example tickers - Korean stocks
        st.markdown("### 🇰🇷 한국 인기 종목")
        kr_cols = st.columns(5)
        kr_examples = [
            ("삼성전자", "005930.KS"),
            ("SK하이닉스", "000660.KS"),
            ("NAVER", "035420.KS"),
            ("카카오", "035720.KS"),
            ("LG에너지", "373220.KS")
        ]
        for idx, (name, ticker) in enumerate(kr_examples):
            if kr_cols[idx].button(name, width="stretch", key=f"ex_kr_{ticker}"):
                st.session_state.last_ticker = ticker
                st.session_state.last_period = "1y"
                st.rerun()

        st.markdown("---")
        st.caption("💡 팁: 한국 주식은 종목코드 뒤에 .KS를 붙이세요 (예: 005930.KS)")

        return

    # Perform or retrieve analysis
    if analyze_button:
        with st.spinner(f"📊 {ticker} 분석 중..."):
            try:
                # Use cached analysis
                analysis_result = cached_analyze_stock(ticker, period)

                if not analysis_result.get("success"):
                    st.error(f"❌ {analysis_result.get('error', '분석 실패')}")
                    return

                # Store in session state
                st.session_state.current_stock_analysis = analysis_result
                # Clear previous AI analysis
                if 'ai_stock_analysis' in st.session_state:
                    del st.session_state.ai_stock_analysis

            except Exception as e:
                st.error(f"❌ 오류: {str(e)}")
                st.exception(e)
                return

    # Retrieve from session state
    if 'current_stock_analysis' not in st.session_state:
        return

    analysis_result = st.session_state.current_stock_analysis
    summary = analysis_result["summary"]
    df = analysis_result["dataframe"]

    # Check if stock is in portfolio
    portfolio_info = check_portfolio_holding(ticker)

    # Display results
    st.divider()

    # Header: Stock name and current price
    col_name, col_price, col_change = st.columns([2, 1, 1])
    with col_name:
        # Show portfolio badge if holding
        if portfolio_info:
            st.markdown(f"## {summary['name']} 🎯")
            st.caption(f"티커: {summary['ticker']} | ⭐ 포트폴리오 보유 중")

            # Show holding details
            avg_price = portfolio_info['avg_price_usd']
            if avg_price > 0:
                current_price = summary['current_price']
                gain_loss_pct = ((current_price - avg_price) / avg_price * 100)
                gain_color = "🟢" if gain_loss_pct > 0 else "🔴"

                st.caption(f"보유 수량: {portfolio_info['quantity']:.2f}주")
                st.caption(f"평균 단가: ${avg_price:.2f} | 수익률: {gain_loss_pct:+.1f}% {gain_color}")
        else:
            st.markdown(f"## {summary['name']}")
            st.caption(f"티커: {summary['ticker']}")

    with col_price:
        st.metric(
            "현재가",
            f"${summary['current_price']:.2f}",
            f"{summary['price_change_pct']:+.2f}%"
        )

    with col_change:
        position_color = "🟢" if summary['position_52w_pct'] > 50 else "🔴"
        st.metric(
            "52주 위치",
            f"{summary['position_52w_pct']:.1f}% {position_color}",
            f"최고가: ${summary['52week_high']:.2f}"
        )

    st.divider()

    # Main content: Chart + Technical Indicators
    col_chart, col_indicators = st.columns([2, 1])

    with col_chart:
        st.markdown("### 📈 주가 차트")
        render_price_chart(df, ticker)

    with col_indicators:
        st.markdown("### 📊 기술적 지표")
        render_technical_indicators(summary)

    st.divider()

    # Fundamentals
    st.markdown("### 💼 기업 펀더멘털")
    render_fundamentals(summary)

    st.divider()

    # === NEW: 깊이 분석 섹션 ===
    # Earnings Trend Analysis
    st.markdown("### 📊 실적 추세 분석")
    render_earnings_analysis(ticker)

    st.divider()

    # Peer Comparison
    st.markdown("### 🏆 경쟁사 비교")
    render_peer_comparison(ticker)

    st.divider()

    # Valuation Analysis
    st.markdown("### 💰 밸류에이션 분석")
    render_valuation_analysis(ticker)

    st.divider()

    # AI Analysis
    st.markdown("### 🧠 AI 투자 분석")

    # Analysis mode selection
    col1, col2 = st.columns([1, 1])
    with col1:
        analysis_mode = st.radio(
            "분석 방식 선택",
            ["단일 AI 분석 (빠름, 5초)", "멀티에이전트 분석 (심층, 30초)"],
            help="단일 AI: 빠른 분석 (1개 AI)\n멀티에이전트: 3명의 전문가 토론 + 합의"
        )

    # Check if AI analysis already exists
    if 'ai_stock_analysis' in st.session_state and 'ai_analysis_mode' in st.session_state:
        st.markdown(st.session_state.ai_stock_analysis)

        col_refresh, col_switch = st.columns([1, 1])
        with col_refresh:
            if st.button("🔄 AI 분석 새로고침", width="stretch"):
                del st.session_state.ai_stock_analysis
                del st.session_state.ai_analysis_mode
                st.rerun()
        with col_switch:
            current_mode = st.session_state.ai_analysis_mode
            other_mode = "멀티에이전트" if "단일" in current_mode else "단일 AI"
            if st.button(f"🔄 {other_mode}로 재분석", width="stretch"):
                del st.session_state.ai_stock_analysis
                del st.session_state.ai_analysis_mode
                st.rerun()
    else:
        if st.button("🤖 AI 투자 의견 생성", width="stretch", type="primary"):
            # Single AI Analysis
            if "단일" in analysis_mode:
                with st.spinner("⏳ AI 분석 중... (약 5초 소요)"):
                    ai_analysis = generate_ai_analysis(analysis_result)
                    st.session_state.ai_stock_analysis = ai_analysis
                    st.session_state.ai_analysis_mode = analysis_mode
                    st.rerun()

            # Multi-Agent Analysis
            else:
                with st.spinner("⏳ 멀티에이전트 분석 중...\n\n4명의 전문가가 토론하고 있습니다... (약 30초 소요)"):
                    try:
                        # Load portfolio data for Risk Control Agent
                        portfolio_data = None
                        try:
                            from skills.gsheet_loader import load_data_from_gsheet
                            portfolio_df, _, _ = load_data_from_gsheet("GEM_Finance_Portfolio")

                            if not portfolio_df.empty:
                                holdings = []
                                total_value = portfolio_df['평가금액(KRW)'].sum() if '평가금액(KRW)' in portfolio_df.columns else 0

                                for _, row in portfolio_df.iterrows():
                                    holdings.append({
                                        'ticker': row.get('종목코드', row.get('티커코드', '')),
                                        'name': row.get('종목명', ''),
                                        'sector': row.get('카테고리', 'Unknown'),
                                        'value_pct': (row.get('평가금액(KRW)', 0) / total_value * 100) if total_value > 0 else 0
                                    })

                                portfolio_data = {
                                    'holdings': holdings,
                                    'total_value': total_value
                                }
                        except:
                            pass  # If portfolio load fails, continue without it

                        ai_analysis = run_stock_analysis(
                            ticker=analysis_result['ticker'],
                            analysis_data=analysis_result['summary'],
                            data_file_path=analysis_result['data_file'],
                            portfolio_data=portfolio_data
                        )
                        st.session_state.ai_stock_analysis = ai_analysis
                        st.session_state.ai_analysis_mode = analysis_mode
                        st.rerun()
                    except Exception as e:
                        st.error(f"멀티에이전트 분석 실패: {str(e)}")
                        st.info("단일 AI 분석을 시도하세요.")


def render_price_chart(df: pd.DataFrame, ticker: str):
    """Render interactive price chart with technical indicators"""
    # Create subplots: Price + Volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{ticker} 주가', '거래량')
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='주가'
        ),
        row=1, col=1
    )

    # Moving Averages
    if 'ma20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['ma20'], name='MA20',
                      line=dict(color='orange', width=1)),
            row=1, col=1
        )

    if 'ma60' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['ma60'], name='MA60',
                      line=dict(color='green', width=1)),
            row=1, col=1
        )

    # Bollinger Bands
    if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['bb_upper'], name='볼린저 상단',
                      line=dict(color='gray', width=1, dash='dash'),
                      showlegend=False),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['bb_lower'], name='볼린저 하단',
                      line=dict(color='gray', width=1, dash='dash'),
                      fill='tonexty', fillcolor='rgba(128,128,128,0.1)',
                      showlegend=False),
            row=1, col=1
        )

    # Volume
    colors = ['red' if row['Close'] < row['Open'] else 'green'
              for _, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='거래량',
               marker=dict(color=colors)),
        row=2, col=1
    )

    # Layout
    fig.update_layout(
        height=600,
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        showlegend=True,
        hovermode='x unified'
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#30363D')

    st.plotly_chart(fig, width="stretch")


def render_technical_indicators(summary: dict):
    """Render technical indicators panel"""
    tech = summary.get('technical_indicators', {})

    # RSI
    rsi = tech.get('rsi', 0)
    rsi_signal = "🔴 과매수" if rsi > 70 else "🟢 과매도" if rsi < 30 else "⚪ 중립"
    st.metric("RSI (14일)", f"{rsi:.1f}", rsi_signal)

    st.divider()

    # MACD
    macd = tech.get('macd', 0)
    macd_signal = tech.get('macd_signal', 0)
    macd_status = "🟢 강세" if macd > macd_signal else "🔴 약세"
    st.metric("MACD", f"{macd:.2f}", macd_status)

    st.divider()

    # Moving Averages
    current_price = summary.get('current_price', 0)
    ma20 = tech.get('ma20', 0)
    ma60 = tech.get('ma60', 0)

    ma_status = "🟢 골든크로스" if ma20 > ma60 else "🔴 데드크로스"
    st.caption("**이동평균선**")
    st.caption(f"MA20: ${ma20:.2f}")
    st.caption(f"MA60: ${ma60:.2f}")
    st.caption(ma_status)

    st.divider()

    # Bollinger Bands
    bb_upper = tech.get('bb_upper', 0)
    bb_lower = tech.get('bb_lower', 0)
    bb_position = "🔴 상단" if current_price > bb_upper else "🟢 하단" if current_price < bb_lower else "⚪ 중간"

    st.caption("**볼린저 밴드**")
    st.caption(f"상단: ${bb_upper:.2f}")
    st.caption(f"하단: ${bb_lower:.2f}")
    st.caption(f"위치: {bb_position}")


def render_fundamentals(summary: dict):
    """Render fundamental metrics"""
    fund = summary.get('fundamentals', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sector = fund.get('sector', 'N/A')
        st.metric("섹터", sector)

    with col2:
        market_cap = fund.get('market_cap', 0)
        if market_cap > 0:
            market_cap_b = market_cap / 1e9
            st.metric("시가총액", f"${market_cap_b:.1f}B")
        else:
            st.metric("시가총액", "N/A")

    with col3:
        pe = fund.get('pe_ratio', 0)
        if pe > 0:
            st.metric("PER", f"{pe:.1f}")
        else:
            st.metric("PER", "N/A")

    with col4:
        beta = fund.get('beta', 0)
        if beta > 0:
            beta_status = "고위험" if beta > 1.5 else "저위험" if beta < 0.8 else "보통"
            st.metric("베타", f"{beta:.2f}", beta_status)
        else:
            st.metric("베타", "N/A")


def render_earnings_analysis(ticker: str):
    """Render earnings trend analysis"""
    try:
        from skills.earnings_analyzer import analyze_earnings_trend

        with st.spinner("실적 추세 분석 중..."):
            result = analyze_earnings_trend(ticker)

        if 'error' in result:
            st.warning(f"실적 데이터를 불러올 수 없습니다: {result['error']}")
            return

        # Revenue Trend
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("**📈 매출 추세**")
            rev = result.get('revenue_trend', {})

            if 'qoq_growth' in rev and rev['qoq_growth']:
                # QoQ Growth chart
                qoq = rev['qoq_growth']
                quarters = [f"Q{i+1}" for i in range(len(qoq))]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=quarters,
                    y=qoq,
                    marker_color=['#4ECDC4' if v > 0 else '#FF6B6B' for v in qoq],
                    text=[f"{v:+.1f}%" for v in qoq],
                    textposition='outside'
                ))
                fig.update_layout(
                    height=200,
                    margin=dict(t=20, b=20, l=20, r=20),
                    template='plotly_dark',
                    showlegend=False,
                    yaxis_title="QoQ 성장률 (%)"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Direction indicator
                direction = rev.get('direction', 'unknown')
                if direction == 'accelerating':
                    st.success(f"✅ {rev.get('summary', '성장 가속')}")
                elif direction == 'decelerating':
                    st.warning(f"⚠️ {rev.get('summary', '성장 둔화')}")
                else:
                    st.info(f"➡️ {rev.get('summary', '안정적 성장')}")

        with col2:
            st.markdown("**💰 마진율 추세**")
            margin = result.get('margin_analysis', {})

            if 'gross_margin' in margin and margin['gross_margin']:
                gross = margin['gross_margin']
                net = margin.get('net_margin', [])

                quarters = [f"Q{i+1}" for i in range(len(gross))]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=quarters, y=gross,
                    name='Gross Margin',
                    line=dict(color='#4ECDC4', width=3),
                    mode='lines+markers'
                ))

                if net:
                    fig.add_trace(go.Scatter(
                        x=quarters, y=net,
                        name='Net Margin',
                        line=dict(color='#FF6B6B', width=3),
                        mode='lines+markers'
                    ))

                fig.update_layout(
                    height=200,
                    margin=dict(t=20, b=20, l=20, r=20),
                    template='plotly_dark',
                    yaxis_title="마진율 (%)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                st.plotly_chart(fig, use_container_width=True)

                trend = margin.get('trend', 'stable')
                if trend == 'improving':
                    st.success(f"✅ {margin.get('summary', '마진율 개선')}")
                elif trend == 'declining':
                    st.warning(f"⚠️ {margin.get('summary', '마진율 하락')}")
                else:
                    st.info(f"➡️ {margin.get('summary', '마진율 안정')}")

        # Quality Score
        st.divider()
        col_score, col_surprise = st.columns([1, 1])

        with col_score:
            quality_score = result.get('quality_score', 0)
            recommendation = result.get('recommendation', 'unknown')

            st.metric("실적 품질 스코어", f"{quality_score}/10")

            if recommendation == 'strong_growth':
                st.success("🚀 강력한 성장")
            elif recommendation == 'moderate_growth':
                st.info("📈 안정적 성장")
            elif recommendation == 'slowing':
                st.warning("📉 성장 둔화")
            else:
                st.error("🔴 실적 악화")

        with col_surprise:
            surprise = result.get('surprise_analysis', {})
            beat_rate = surprise.get('beat_rate')

            if beat_rate is not None:
                st.metric(
                    "가이던스 상회 비율",
                    f"{beat_rate*100:.0f}%",
                    f"Avg +{surprise.get('avg_surprise', 0):.1f}%"
                )

                consistency = surprise.get('consistency', 'unknown')
                if consistency == 'high':
                    st.success("🎯 높은 예측 가능성")
                elif consistency == 'moderate':
                    st.info("➡️ 보통 예측 가능성")
                else:
                    st.warning("⚠️ 낮은 예측 가능성")

    except Exception as e:
        st.error(f"실적 분석 오류: {str(e)}")


def render_peer_comparison(ticker: str):
    """Render peer comparison with yfinance fallback"""
    try:
        from skills.peer_comparison import compare_within_sector

        with st.spinner("경쟁사 비교 중..."):
            result = compare_within_sector(ticker)

        if 'error' in result:
            # Fallback: Show basic info from yfinance
            st.warning("⚠️ 상세 경쟁사 데이터 없음 (주요 종목만 지원)")

            try:
                import yfinance as yf
                stock = yf.Ticker(ticker)
                info = stock.info

                st.markdown("**📊 기본 정보 (yfinance)**")
                col1, col2, col3, col4 = st.columns(4)

                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                pe = info.get('trailingPE', 0)
                peg = info.get('pegRatio', 0)

                col1.metric("섹터", sector)
                col2.metric("산업", industry[:15] + "..." if len(industry) > 15 else industry)
                col3.metric("PER", f"{pe:.1f}" if pe and pe > 0 else "N/A")
                col4.metric("PEG", f"{peg:.2f}" if peg and peg > 0 else "N/A")

                st.caption("💡 상세 경쟁사 비교는 NVDA, AAPL, TSLA 등 주요 종목에서 지원됩니다.")
                st.caption(f"🔍 오류 상세: {result.get('error', 'Unknown error')}")

            except Exception as fallback_error:
                st.error(f"기본 정보도 불러올 수 없습니다: {fallback_error}")

            return

        # Comparison Table
        peer_table = result.get('peer_table')

        if peer_table is not None and not peer_table.empty:
            # Display columns
            display_cols = ['ticker', 'revenue_growth_yoy', 'gross_margin', 'net_margin', 'pe_ratio', 'peg_ratio']
            available_cols = [col for col in display_cols if col in peer_table.columns]

            if available_cols:
                display_df = peer_table[available_cols].copy()

                # Rename columns
                display_df.columns = ['티커', '매출 성장률', 'Gross Margin', 'Net Margin', 'PER', 'PEG']

                # Highlight main ticker
                def highlight_main(row):
                    if row['티커'] == ticker:
                        return ['background-color: #1e3a5f'] * len(row)
                    return [''] * len(row)

                styled_df = display_df.style.apply(highlight_main, axis=1)
                st.dataframe(styled_df, use_container_width=True)

        # Summary
        summary = result.get('comparison_summary', {})
        col1, col2, col3 = st.columns(3)

        with col1:
            growth_rank = summary.get('growth_rank')
            total = summary.get('total_peers', 0)
            if growth_rank:
                st.metric("성장률 순위", f"{growth_rank}/{total}")

        with col2:
            margin_rank = summary.get('margin_rank')
            if margin_rank:
                st.metric("마진율 순위", f"{margin_rank}/{total}")

        with col3:
            market_share = summary.get('market_share_pct')
            if market_share:
                st.metric("시장 점유율", f"{market_share:.1f}%")

        # Competitive Advantage
        advantage = summary.get('competitive_advantage', 'unknown')
        summary_text = summary.get('summary', '')

        if advantage == 'dominant':
            st.success(f"🏆 {summary_text}")
        elif advantage == 'strong':
            st.info(f"💪 {summary_text}")
        elif advantage == 'moderate':
            st.warning(f"➡️ {summary_text}")
        else:
            st.error(f"⚠️ {summary_text}")

    except Exception as e:
        st.error(f"경쟁사 비교 오류: {str(e)}")


def render_valuation_analysis(ticker: str):
    """Render valuation analysis"""
    try:
        from skills.valuation_engine import calculate_valuation_metrics

        with st.spinner("밸류에이션 분석 중..."):
            result = calculate_valuation_metrics(ticker)

        if 'error' in result:
            st.warning(f"밸류에이션 데이터를 불러올 수 없습니다")
            return

        # Multiples
        col1, col2, col3, col4 = st.columns(4)
        multiples = result.get('multiples', {})

        with col1:
            pe = multiples.get('pe_ratio')
            st.metric("PER", f"{pe:.1f}" if pe else "N/A")

        with col2:
            peg = multiples.get('peg_ratio')
            if peg:
                peg_status = "저평가" if peg < 1.0 else "적정" if peg < 1.5 else "고평가"
                st.metric("PEG", f"{peg:.2f}", peg_status)
            else:
                st.metric("PEG", "N/A")

        with col3:
            ps = multiples.get('price_to_sales')
            st.metric("P/S", f"{ps:.1f}" if ps else "N/A")

        with col4:
            pb = multiples.get('price_to_book')
            st.metric("P/B", f"{pb:.1f}" if pb else "N/A")

        st.divider()

        # Profitability & Valuation Score
        col_profit, col_score = st.columns([1, 1])

        with col_profit:
            st.markdown("**💼 수익성**")
            profit = result.get('profitability', {})

            roe = profit.get('roe')
            roa = profit.get('roa')
            net_margin = profit.get('net_margin')

            if roe:
                st.caption(f"ROE: {roe:.1f}%")
            if roa:
                st.caption(f"ROA: {roa:.1f}%")
            if net_margin:
                st.caption(f"Net Margin: {net_margin:.1f}%")

        with col_score:
            valuation_score = result.get('valuation_score', 0)
            assessment = result.get('assessment', 'unknown')

            st.metric("밸류에이션 스코어", f"{valuation_score}/10")

            if assessment == 'undervalued':
                st.success("💎 저평가")
            elif assessment == 'fair_value':
                st.info("✅ 적정 가격")
            else:
                st.warning("⚠️ 고평가")

        # Summary
        st.divider()
        summary_text = result.get('summary', '')
        st.markdown(f"**💡 종합 평가**: {summary_text}")

        # Sector Comparison
        sector_comp = result.get('sector_comparison', {})
        if sector_comp.get('premium_pct'):
            premium = sector_comp['premium_pct']
            justified = sector_comp.get('premium_justified', False)

            if justified:
                st.info(f"📊 섹터 대비 Premium {premium:+.1f}% (정당화 가능)")
            else:
                st.warning(f"📊 섹터 대비 Premium {premium:+.1f}% (과도)")

    except Exception as e:
        st.error(f"밸류에이션 분석 오류: {str(e)}")
