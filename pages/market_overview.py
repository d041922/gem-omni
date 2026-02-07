"""
GEM: OMNI - Market Overview (v4.1)
실시간 뉴스 인텔리전스 통합 버전
"""
import streamlit as st
from skills.data_orchestrator import DataOrchestrator
from pages.style_utils import load_custom_css, metric_card

def localize_sentiment(sentiment: str) -> str:
    mapping = {"Greed": "🟢 긍정", "Fear": "🔴 우려", "Neutral": "⚪ 중립"}
    return mapping.get(sentiment, sentiment)

def render_market_overview():
    load_custom_css()
    orchestrator = DataOrchestrator()
    state = orchestrator.read_state()
    data = state.get("data", {})
    market = data.get("market", {})
    indices = market.get("indices", {})
    fx = market.get("exchange_rate", {}).get("USD_KRW", 1450.0)
    
    # 지능형 데이터 로드
    intel = data.get("intelligence", {})
    briefing = intel.get("daily_briefing", [])

    st.title("🌍 글로벌 시장 현황")
    
    # 1. Macro KPI
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        sp = indices.get("S&P 500", {})
        metric_card("S&P 500", f"{sp.get('value', 0):,.1f}", f"{sp.get('change_pct', 0):+.2f}%", "red" if sp.get('change_pct', 0) > 0 else "blue")
    with m2:
        nq = indices.get("NASDAQ", {})
        metric_card("NASDAQ", f"{nq.get('value', 0):,.1f}", f"{nq.get('change_pct', 0):+.2f}%", "red" if nq.get('change_pct', 0) > 0 else "blue")
    with m3:
        ks = indices.get("KOSPI", {})
        metric_card("KOSPI", f"{ks.get('value', 0):,.1f}", f"{ks.get('change_pct', 0):+.2f}%", "red" if ks.get('change_pct', 0) > 0 else "blue")
    with m4:
        metric_card("USD/KRW 환율", f"₩{fx:,.2f}", "실시간 적용 중")

    st.divider()

    # 2. Market News Intelligence (Exa Integration)
    st.subheader("📰 오늘의 시장 핵심 이슈")
    if briefing:
        # 뉴스 가로 배치 (Bento Grid 스타일)
        cols = st.columns(len(briefing))
        for i, news in enumerate(briefing):
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card" style="min-height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="font-weight:bold; color:white; font-size:1.1rem; margin-bottom:8px;">{news['headline']}</div>
                        <div style="margin-bottom:10px;">
                            <span class="momentum-badge" style="background:rgba(255,255,255,0.1); color:#8B949E;">{localize_sentiment(news['sentiment'])}</span>
                            <span style="font-size:0.8rem; color:#3182F6;">{news['impact']}</span>
                        </div>
                        <p style="color:#D1D5DB; font-size:0.9rem; line-height:1.4;">{news['summary']}</p>
                    </div>
                    <a href="{news['url']}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; padding:8px; border-radius:8px; border:1px solid #3182F6; background:transparent; color:#3182F6; cursor:pointer;">기사 읽기</button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 현재 최신 시장 이슈를 분석 중입니다. 잠시만 기다려주세요.")

    st.divider()
    
    # 3. Sector Rotation (Future Task)
    st.subheader("📊 섹터 흐름 분석")
    st.caption("현재 글로벌 자금의 흐름을 분석 중입니다... (구현 준비 중)")

if __name__ == "__main__":
    render_market_overview()