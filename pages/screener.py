"""
GEM: OMNI - Stock Screener (v5.0)
Intelligence Integrated Edition (Quant + Memory + Rules)
"""
import streamlit as st
import pandas as pd
from skills.data_orchestrator import DataOrchestrator
from skills.market_screener import MarketScreener
from skills.analysis_manager import AnalysisManager
from core.memory import UserMemoryManager
from pages.style_utils import load_custom_css

def localize_signal(signal: str) -> str:
    mapping = {"Oversold": "🔵 과매도", "Overbought": "🔴 과매수", "Volume Surge": "🔥 수급폭발", "Golden Cross Trend": "📈 상승추세"}
    return mapping.get(signal, signal)

def render_screener():
    load_custom_css()
    orchestrator = DataOrchestrator()
    memory_manager = UserMemoryManager()
    analyzer = AnalysisManager(orchestrator, memory_manager)
    
    state = orchestrator.read_state()
    intel = state.get("data", {}).get("intelligence", {})
    raw_picks = intel.get("screener_results", [])

    st.title("🎯 지능형 종목 스크리너")
    st.markdown("퀀트 데이터와 마스터의 투자 원칙을 결합한 **최적의 매수 후보**를 제안합니다.")

    if st.button("🚀 전체 시장 정밀 스캔 및 전략 수립", use_container_width=True, type="primary"):
        with st.spinner("시장 데이터 분석 및 과거 승률 대조 중..."):
            tickers = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AVGO", "PLTR", "LLY", "V", "MA", "COST"]
            screener = MarketScreener(orchestrator)
            results = screener.screen_stocks(tickers)
            screener.save_results(results)
            st.rerun()

    st.divider()

    if raw_picks:
        # 1. 지능형 분석 수행 (AnalysisManager 통과)
        analyzed_results = []
        filtered_results = []
        
        for pick in raw_picks:
            analysis = analyzer.analyze_candidate(pick)
            if analysis["status"] == "filtered":
                filtered_results.append(analysis)
            else:
                # 원본 데이터와 분석 결과 병합
                analysis["name"] = pick.get("name", pick["ticker"])
                analysis["price"] = pick["price"]
                analyzed_results.append(analysis)

        # 2. 메인 추천 테이블 노출
        if analyzed_results:
            df = pd.DataFrame(analyzed_results)
            
            # 컬럼 가공 및 한글화
            display_df = df[['ticker', 'name', 'final_score', 'verdict', 'reason', 'price']]
            display_df.columns = ['티커', '종목명', '전략 점수', '에이전트 의견', '판단 근거', '현재가']

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📊 에이전트 선정 Top Picks")
            st.dataframe(
                display_df.style.background_gradient(subset=['전략 점수'], cmap='RdYlGn'),
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # 3. 필터링된 항목 노출 (투명성)
        if filtered_results:
            with st.expander("🚫 투자 원칙에 의해 제외된 종목"):
                for f in filtered_results:
                    st.write(f"- **{f['ticker']}**: {f['reason']}")
    else:
        st.info("데이터가 없습니다. 상단의 스캔 버튼을 눌러주세요.")

if __name__ == "__main__":
    render_screener()