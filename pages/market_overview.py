"""
Market Overview Page (L1: 시장 정보)
Global market intelligence and AI-powered buy recommendations

Structure:
  L1: Market Overview (이 페이지) → 마켓 컨텍스트 제공
  L2: Portfolio Dashboard → Master AI Orchestrator
  L3: Stock Deep Dive → 개별 종목 분석
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict, Any


@st.cache_data(ttl=300)  # 5분 캐싱
def fetch_market_data() -> Dict[str, Dict[str, float]]:
    """Fetch real-time market data from yfinance"""
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "KOSPI": "^KS11",
        "VIX": "^VIX"
    }

    market_data = {}
    for name, ticker in indices.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='2d')

            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                change_pct = ((current - previous) / previous) * 100

                market_data[name] = {
                    'value': current,
                    'change': change_pct
                }
            else:
                market_data[name] = {'value': 0, 'change': 0}
        except:
            market_data[name] = {'value': 0, 'change': 0}

    return market_data


@st.cache_data(ttl=300)
def load_market_intelligence() -> Dict[str, Any]:
    """Load market screener and sector rotation data"""
    try:
        from skills.market_screener import MarketScreener
        from skills.sector_analyzer import SectorAnalyzer

        screener = MarketScreener()
        analyzer = SectorAnalyzer()

        momentum_stocks = screener.screen_momentum_stocks(top_n=10)
        sector_rotation = analyzer.analyze_sector_rotation()

        return {
            'momentum_stocks': momentum_stocks,
            'sector_rotation': sector_rotation,
            'success': True
        }
    except Exception as e:
        print(f"Market intelligence error: {e}")
        return {'success': False, 'error': str(e)}


@st.cache_data(ttl=600)  # 10분 캐싱
def generate_ai_buy_recommendations() -> Dict[str, Any]:
    """
    Generate AI-powered buy recommendations
    (단순 모멘텀이 아닌 종합 분석)
    """
    try:
        from skills.market_recommender import generate_buy_recommendations

        # Load market data
        market_intel = load_market_intelligence()
        if not market_intel['success']:
            return {'success': False, 'error': market_intel.get('error')}

        # Load user portfolio (if available)
        portfolio_df = None
        if 'calculated_portfolio' in st.session_state:
            portfolio_df = st.session_state.calculated_portfolio

        # Generate recommendations
        recommendations = generate_buy_recommendations(
            screener_data=market_intel['momentum_stocks'],
            sector_data=market_intel['sector_rotation'],
            user_portfolio=portfolio_df
        )

        return {
            'success': True,
            'recommendations': recommendations
        }

    except Exception as e:
        print(f"Buy recommendations error: {e}")
        return {'success': False, 'error': str(e)}


def render_market_overview_page():
    """Render Market Overview page"""
    st.markdown("<p class='panel-header'>🌍 Global Market Overview</p>", unsafe_allow_html=True)

    # --- Section 1: 글로벌 지수 ---
    market_data = fetch_market_data()

    col1, col2, col3, col4 = st.columns(4)

    # S&P 500
    sp500 = market_data.get("S&P 500", {})
    col1.metric(
        "S&P 500",
        f"{sp500.get('value', 0):,.1f}",
        f"{sp500.get('change', 0):+.2f}%",
        delta_color="normal"
    )

    # NASDAQ
    nasdaq = market_data.get("NASDAQ", {})
    col2.metric(
        "NASDAQ",
        f"{nasdaq.get('value', 0):,.1f}",
        f"{nasdaq.get('change', 0):+.2f}%",
        delta_color="normal"
    )

    # KOSPI
    kospi = market_data.get("KOSPI", {})
    col3.metric(
        "KOSPI",
        f"{kospi.get('value', 0):,.1f}",
        f"{kospi.get('change', 0):+.2f}%",
        delta_color="normal"
    )

    # VIX
    vix = market_data.get("VIX", {})
    vix_value = vix.get('value', 0)
    vix_status = "Low" if vix_value < 15 else "Normal" if vix_value < 25 else "High"
    col4.metric(
        "VIX (공포 지수)",
        f"{vix_value:.2f}",
        vix_status,
        delta_color="off"
    )

    # Market mood
    avg_change = (sp500.get('change', 0) + nasdaq.get('change', 0) + kospi.get('change', 0)) / 3
    if avg_change > 1:
        market_mood = "📈 시장 강세 - 위험자산 선호"
        mood_color = "#4ECDC4"
    elif avg_change > 0:
        market_mood = "➡️ 시장 안정 - 완만한 상승"
        mood_color = "#FFA500"
    elif avg_change > -1:
        market_mood = "↘️ 시장 약세 - 조정 국면"
        mood_color = "#FF6B6B"
    else:
        market_mood = "📉 시장 하락 - 리스크 회피"
        mood_color = "#FF0000"

    st.markdown(f"""
    <div style='background-color: #161B22; padding: 15px; border-radius: 10px; margin-top: 15px; border-left: 4px solid {mood_color};'>
        <span style='font-size: 1.1rem; font-weight: 600; color: {mood_color};'>{market_mood}</span>
        <span style='float: right; font-size: 0.85rem; color: #8B949E;'>업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- Section 2: 섹터 로테이션 & 스크리닝 ---
    market_intel = load_market_intelligence()

    if market_intel['success']:
        st.markdown("<p class='panel-header'>📊 Market Intelligence</p>", unsafe_allow_html=True)

        col_sector, col_screener = st.columns([1, 1])

        # Left: Sector Rotation
        with col_sector:
            st.markdown("**📊 섹터 로테이션 히트맵**")

            sector_data = market_intel['sector_rotation']
            all_sectors = (
                sector_data['leading_sectors'] +
                sector_data['neutral_sectors'] +
                sector_data['lagging_sectors']
            )
            all_sectors.sort(key=lambda x: x['momentum_score'], reverse=True)

            for sector in all_sectors[:6]:
                momentum = sector['momentum_score']
                return_1m = sector['return_1m']

                if momentum >= 7:
                    emoji = "🟢"
                    color = "#4ECDC4"
                elif momentum >= 5:
                    emoji = "🟡"
                    color = "#FFA500"
                else:
                    emoji = "🔴"
                    color = "#FF6B6B"

                bar_width = int(momentum * 10)
                st.markdown(f"""
                <div style='margin-bottom: 8px;'>
                    <span style='font-size: 0.85rem; color: {color};'>{emoji} <b>{sector['name'][:20]}</b></span>
                    <span style='float: right; font-size: 0.8rem; color: #8B949E;'>{return_1m:+.1f}%</span>
                    <div style='background-color: #30363D; height: 4px; border-radius: 2px; margin-top: 4px;'>
                        <div style='background-color: {color}; height: 4px; width: {bar_width}%; border-radius: 2px;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.caption(f"💰 **Money Flow**: {sector_data['money_flow']['summary']}")

        # Right: Momentum Screener
        with col_screener:
            st.markdown("**🎯 모멘텀 스크리닝 (상위 5개)**")

            momentum_stocks = market_intel['momentum_stocks'][:5]

            for i, stock in enumerate(momentum_stocks, 1):
                rsi = stock['rsi']
                volume_surge = stock['volume_surge']

                if rsi > 70:
                    signal = "🔥"
                elif rsi < 30:
                    signal = "💎"
                else:
                    signal = "📈"

                st.markdown(f"""
                <div style='background-color: #161B22; padding: 8px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #58A6FF;'>
                    <span style='font-size: 0.9rem; font-weight: 600;'>{i}. {stock['ticker']}</span>
                    <span style='font-size: 0.75rem; color: #8B949E; margin-left: 8px;'>{stock['name'][:20]}</span>
                    <br>
                    <span style='font-size: 0.75rem; color: #8B949E;'>
                        RSI {rsi:.0f} {signal} | 거래량 ▲{volume_surge:.1f}x
                    </span>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

    # --- Section 3: AI 기반 매수 추천 (NEW!) ---
    st.markdown("<p class='panel-header'>🤖 AI 매수 추천 (종합 분석)</p>", unsafe_allow_html=True)

    st.info("💡 단순 모멘텀이 아닌 **펀더멘털 + 기술적 지표 + 밸류에이션** 종합 분석")

    if st.button("🚀 AI 매수 추천 생성", type="primary", use_container_width=True):
        with st.spinner("⏳ AI 분석 중... (약 10초 소요)"):
            recommendations = generate_ai_buy_recommendations()

            if recommendations['success']:
                st.session_state.market_recommendations = recommendations['recommendations']
                st.success("✅ AI 매수 추천 완료!")
                st.rerun()
            else:
                st.error(f"❌ 분석 실패: {recommendations.get('error', 'Unknown error')}")

    # Display recommendations if available
    if 'market_recommendations' in st.session_state:
        recommendations = st.session_state.market_recommendations

        if not recommendations:
            st.warning("현재 매수 추천 종목이 없습니다.")
        else:
            for i, rec in enumerate(recommendations[:5], 1):
                # Signal color
                signal = rec['signal']
                if signal == 'Strong Buy':
                    signal_color = "#4ECDC4"
                    signal_emoji = "🚀"
                elif signal == 'Buy':
                    signal_color = "#FFA500"
                    signal_emoji = "📈"
                else:
                    signal_color = "#8B949E"
                    signal_emoji = "👀"

                with st.expander(f"{i}. {rec['ticker']} - {rec['name']} | {signal_emoji} {signal}"):
                    col_price, col_target, col_risk = st.columns(3)

                    col_price.metric("진입가", f"${rec['entry_price']:.2f}")
                    col_target.metric("목표가", f"${rec['target_price']:.2f}",
                                     f"+{((rec['target_price']/rec['entry_price']-1)*100):.1f}%")
                    col_risk.metric("리스크", rec['risk_level'])

                    st.markdown("**📋 투자 근거**")
                    st.write(rec['rationale'])

                    st.markdown("**📊 포트폴리오 적합성**")
                    st.write(rec['portfolio_fit'])

                    # Action button
                    if st.button(f"🔍 {rec['ticker']} 상세 분석", key=f"analyze_{rec['ticker']}"):
                        st.session_state.last_ticker = rec['ticker']
                        st.switch_page("pages/stock_analysis.py")

    else:
        st.caption("👆 버튼을 클릭하여 AI 매수 추천을 받아보세요")

    st.divider()

    # --- Section 4: Fear & Greed Index (향후 확장) ---
    st.markdown("<p class='panel-header'>😱 Fear & Greed Index</p>", unsafe_allow_html=True)
    st.info("🚧 향후 구현 예정: CNN Fear & Greed Index, Put/Call Ratio, VIX Term Structure")


# Main entry point
if __name__ == "__main__":
    render_market_overview_page()
