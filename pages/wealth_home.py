"""
GEM: OMNI-Core [Wealth v4.2 - Polished Bento]
Refined Charts & Clean Layout
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from skills.data_orchestrator import DataOrchestrator
from skills.market_screener import MarketScreener
from pages.style_utils import load_custom_css, metric_card, localize_signal

def format_korean_currency(v: float) -> str:
    if v == 0:
        return "₩0"
    
    v_calc = abs(v)
    res = ""
    
    if v_calc >= 1e12:
        res += f"{int(v_calc // 1e12)}조 "
        v_calc %= 1e12
    if v_calc >= 1e8:
        res += f"{int(v_calc // 1e8)}억 "
        v_calc %= 1e8
    if v_calc >= 1e4:
        res += f"{int(v_calc // 1e4)}만"
        
    return f"₩{res.strip()}" if res else f"₩{abs(v):,.0f}"

def render_wealth_home():
    load_custom_css()
    orchestrator = DataOrchestrator()
    state = orchestrator.read_state()
    data = state.get("data", {})
    summary = data.get("portfolio", {}).get("summary", {})
    holdings = data.get("portfolio", {}).get("holdings", [])
    intel = data.get("intelligence", {}).get("screener_results", [])

    # --- Header ---
    with st.sidebar:
        st.title("💎 자산 관리")
        if st.button("🏠 홈으로 이동", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 데이터 동기화", use_container_width=True):
            with st.spinner("동기화 중..."):
                orchestrator.sync_portfolio()
            st.rerun()

    st.markdown("<h1 style='margin-bottom: 20px;'>🏛️ 자산 마스터 컨트롤</h1>", unsafe_allow_html=True)

    # --- Row 0: Intelligence Briefing ---
    top_pick_html = ""
    if intel:
        p = intel[0]
        h_signal = localize_signal(p['signals'][0])
        top_pick_html = f"""
        <div style='margin-top:15px; padding:15px; background:rgba(49, 130, 246, 0.1); border-radius:12px; border:1px solid rgba(49, 130, 246, 0.3);'>
            <span style='color:#8B949E; font-size:0.8rem;'>TODAY'S TOP PICK</span><br>
            <b style='font-size:1.2rem; color:white;'>{p['ticker']}</b> 
            <span style='color:#FF4B4B; font-weight:bold; margin-left:10px;'>{p['score']}점</span>
            <span style='margin-left:10px;'>{h_signal}</span>
        </div>
        """

    st.markdown(f"""
    <div style='background: rgba(49, 130, 246, 0.05); border-left: 5px solid #3182F6; padding: 20px; border-radius: 8px; margin-bottom: 25px;'>
        <h4 style='margin:0; color:#3182F6;'>Master Briefing</h4>
        <p style='margin:10px 0 0 0; color:#D1D5DB; font-size:1.1rem;'>
            안녕하세요 마스터. 현재 총 자산은 <b style='color:white;'>{format_korean_currency(summary.get('total_krw', 0))}</b> 입니다. 
            {f"지표 분석 결과, 오늘은 <b>{intel[0]['ticker']}</b>에 주목할 필요가 있습니다." if intel else "시장 데이터를 분석 중입니다. 신선한 기회를 찾는 중이니 잠시만 기다려주세요."}
        </p>
        {top_pick_html}
    </div>
    """, unsafe_allow_html=True)

    # --- Row 1: Key Metrics ---
    c1, c2, c3 = st.columns(3)
    pnl = summary.get('daily_pnl_pct', 0)
    
    with c1:
        metric_card("총 순자산", format_korean_currency(summary.get('total_krw', 0)))
    with c2:
        metric_card("투자 자산", format_korean_currency(summary.get('stock_krw', 0)), f"일간 {pnl:+.2f}%", "red" if pnl > 0 else "blue")
    with c3:
        metric_card("현금 보유액", format_korean_currency(summary.get('cash_krw', 0)), "투자 대기 자금")

    # --- Row 2: Deep Analysis & Momentum ---
    if holdings:
        st.divider()
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.markdown('<div class="glass-card" style="min-height: 520px;">', unsafe_allow_html=True)
            st.subheader("📊 포트폴리오 다차원 분석")
            tab1, tab2, tab3 = st.tabs(["📂 계좌별", "🏷️ 전략별", "💎 종목별"])
            df = pd.DataFrame(holdings)
            
            with tab1:
                fig = px.pie(df, names='account', values='current_value_krw', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#E6EDF3"), margin=dict(t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                fig = px.pie(df, names='tier', values='current_value_krw', hole=0.6, color_discrete_sequence=px.colors.sequential.Greens_r)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#E6EDF3"), margin=dict(t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
            with tab3:
                df['label'] = df.apply(lambda x: f"{x['name']}<br>({x['ticker']})", axis=1)
                fig = px.treemap(df, path=['label'], values='current_value_krw', color='current_value_krw', color_continuous_scale='RdBu')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, l=0, r=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_side:
            st.markdown('<div class="glass-card" style="min-height: 520px;">', unsafe_allow_html=True)
            st.subheader("🔥 AI 추천 종목")
            if intel:
                for p in intel[:5]:
                    h_signal = localize_signal(p['signals'][0])
                    st.markdown(f"""
                    <div style="margin-bottom: 12px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:bold; color:white;">{p['ticker']}</span>
                            <span style="color:#FF4B4B; font-weight:bold; font-size:0.9rem;">{p['score']}점</span>
                        </div>
                        <div style="margin-top:4px;">
                            <span class="momentum-badge">{h_signal}</span>
                            <span style="color:#8B949E; font-size:0.75rem;">RSI {p['details'].get('rsi', 'N/A')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("아직 포착된 시그널이 없습니다.")
            
            if st.button("🚀 시장 스캔 시작", use_container_width=True):
                with st.spinner("시장 데이터 분석 중..."):
                    results = MarketScreener(orchestrator).screen_stocks(["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "PLTR", "AMZN"])
                    MarketScreener(orchestrator).save_results(results)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # --- Row 3: Inventory ---
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📜 상세 자산 명세")
        df_table = pd.DataFrame(holdings)
        df_table['Value'] = df_table['current_value_krw'].apply(lambda x: f"₩{x:,.0f}")
        df_table['Price'] = df_table.apply(lambda x: f"{x['currency_symbol']}{x['current_price']:,.2f}", axis=1)
        st.dataframe(df_table[['account', 'tier', 'name', 'ticker', 'quantity', 'Price', 'Value']], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 50px; background: rgba(255,255,255,0.02); border-radius: 16px; border: 1px dashed rgba(255,255,255,0.1); margin-top: 20px;">
            <h3 style="color: #8B949E;">데이터 동기화 필요</h3>
            <p style="color: #666;">좌측 사이드바의 [데이터 동기화] 버튼을 눌러 자산 정보를 불러오세요.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_wealth_home()
