import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.data_manager import DataManager
from skills.asset_classifier import AssetClassifier
from pages.style_utils import metric_card, format_krw

def render_dashboard():
    if 'calculated_portfolio' not in st.session_state:
        with st.spinner("데이터 동기화 중..."):
            DataManager.get_portfolio_data()
    
    portfolio_obj = st.session_state.get('portfolio_obj')
    df = st.session_state.get('calculated_portfolio')
    
    if not portfolio_obj or df is None or df.empty:
        st.warning("📊 포트폴리오 데이터가 없습니다.")
        return

    # 2. KPI 요약
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("총 자산", format_krw(portfolio_obj.total_net_worth_krw), "KRW Base")
    with c2:
        metric_card("주식 평가액", format_krw(portfolio_obj.stock_value_krw), f"현금: {format_krw(portfolio_obj.cash_krw)}")
    with c3:
        metric_card("총 손익", format_krw(portfolio_obj.profit_krw), f"{portfolio_obj.return_pct:+.2f}%")
    with c4:
        rate = DataManager.get_usd_krw_rate()
        metric_card("USD/KRW", f"₩{rate:,.1f}", "Real-time")

    st.markdown("---")

    # 3. Strategy Analysis
    st.subheader("🎯 Portfolio Strategy")
    cols = df.columns.tolist()
    
    # Safe Mapping Logic
    def get_col(candidates):
        return next((c for c in cols if any(k in str(c).lower() for k in candidates)), None)

    name_col = get_col(['name', '종목명'])
    tick_col = get_col(['code', 'ticker', 'symbol', '종목코드'])
    cate_col = get_col(['cate', 'sector', '카테고리'])
    val_col = get_col(['평가금액', '금액', 'value_krw'])
    ret_col = get_col(['수익률', 'pct', 'returns'])

    classifier = AssetClassifier()
    def safe_classify(row):
        cat = str(row.get(cate_col, 'Unknown')) if cate_col else 'Unknown'
        name = str(row.get(name_col, 'Unknown')) if name_col else 'Unknown'
        ticker = str(row.get(tick_col, 'Unknown')) if tick_col else 'Unknown'
        return classifier.classify(ticker, cat, name)

    df['Asset_Class'] = df.apply(safe_classify, axis=1)
    
    if val_col:
        class_group = df.groupby('Asset_Class')[val_col].sum()
    else:
        class_group = pd.Series(dtype=float)

    labels = ['Core', 'Scaling', 'Optional']
    values = [float(class_group.get(label, 0.0)) for label in labels]
    core_pct = (values[0] / sum(values) * 100) if sum(values) > 0 else 0.0

    col_chart, col_insight = st.columns([1, 1])
    with col_chart:
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker_colors=['#3182F6', '#FFBB00', '#95A5A6'])])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=True, legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig, use_container_width=True)

    with col_insight:
        target = classifier.get_rebalancing_target(core_pct)
        action = str(target.get('action', 'maintain')).upper()
        st.markdown(f"#### 💡 AI Strategy: {action}")
        if 'increase' in action.lower():
            st.warning(f"Core 비중 부족: {core_pct:.1f}%")
        elif 'decrease' in action.lower():
            st.info(f"Core 비중 충분: {core_pct:.1f}%")
        else:
            st.success("⚖️ 균형 잡힌 포트폴리오")

    st.markdown("---")

    # 4. Table
    st.subheader("📝 Holdings Details")
    disp = pd.DataFrame()
    disp['Class'] = df['Asset_Class']
    disp['Ticker'] = df.get(tick_col, 'N/A') if tick_col else 'N/A'
    disp['Name'] = df.get(name_col, 'Unknown') if name_col else 'Unknown'
    if val_col:
        disp['Value (KRW)'] = df[val_col].apply(format_krw)
    if ret_col:
        disp['Return'] = df[ret_col].apply(lambda x: f"{float(x):+.2f}%")
    
    st.dataframe(disp, use_container_width=True, hide_index=True)