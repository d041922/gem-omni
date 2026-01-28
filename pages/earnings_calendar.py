import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, date
import calendar
import time

st.set_page_config(page_title="실적 캘린더", page_icon="📅", layout="wide")

# --- Fallback Data (Estimated for Jan/Feb 2026) ---
# Used when live API fails (Common with free yfinance/Naver)

KR_EARNINGS_EST = {
    "005930.KS": date(2026, 1, 31), "000660.KS": date(2026, 1, 25),
    "373220.KS": date(2026, 1, 27), "207940.KS": date(2026, 1, 24),
    "005380.KS": date(2026, 1, 25), "000270.KS": date(2026, 1, 25),
    "005490.KS": date(2026, 1, 31), "035420.KS": date(2026, 2, 2),
    "035720.KS": date(2026, 2, 13), "105560.KS": date(2026, 2, 7),
    "055550.KS": date(2026, 2, 8)
}

US_EARNINGS_EST = {
    "NFLX": date(2026, 1, 20), "TSLA": date(2026, 1, 28),
    "MSFT": date(2026, 1, 30), "GOOGL": date(2026, 1, 30),
    "AAPL": date(2026, 2, 1),  "AMZN": date(2026, 2, 1),
    "META": date(2026, 2, 1),  "NVDA": date(2026, 2, 21),
    "AMD": date(2026, 1, 30),  "INTC": date(2026, 1, 25),
    "QCOM": date(2026, 2, 5)
}

# --- Helper Functions ---

def get_naver_stock_data(code):
    """
    Fetch stock data using Naver Mobile API
    URL: https://m.stock.naver.com/api/stock/{code}/basic
    """
    try:
        clean_code = code.replace('.KS', '').replace('.KQ', '')
        url = f"https://m.stock.naver.com/api/stock/{clean_code}/basic"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            data = res.json()
            name = data.get('stockName', '-')
            
            # Use PC Link as requested (Mobile link was considered "broken/weird")
            link = f"https://finance.naver.com/item/main.naver?code={clean_code}"
            
            # Fallback Date
            e_date = KR_EARNINGS_EST.get(code)
            
            return {
                "ticker": code,
                "name": name,
                "link": link,
                "date": e_date, 
                "country": "KR"
            }
    except: pass
    return None

def get_calendar_data(ticker, name, country="US"):
    """
    Fetch earnings date safely handling various sources & fallbacks
    """
    # 1. KR Logic
    if country == "KR":
        return get_naver_stock_data(ticker)

    # 2. US Logic
    try:
        stock = yf.Ticker(ticker)
        cal = stock.calendar
        earnings_date = None
        
        # Try fetch from yfinance
        if cal is not None:
            if isinstance(cal, dict) and 'Earnings Date' in cal:
                vals = cal['Earnings Date']
                if len(vals) > 0: earnings_date = vals[0]
            elif isinstance(cal, pd.DataFrame) and not cal.empty:
                if 'Earnings Date' in cal.index:
                    earnings_date = cal.loc['Earnings Date'].iloc[0]
                elif 0 in cal.index:
                    earnings_date = cal.iloc[0, 0]
                else:
                     earnings_date = cal.iat[0, 0]

        # Use Fallback if API failed
        if not earnings_date and ticker in US_EARNINGS_EST:
            earnings_date = US_EARNINGS_EST[ticker]

        # Validate
        if isinstance(earnings_date, (datetime, pd.Timestamp, date)):
            if isinstance(earnings_date, (datetime, pd.Timestamp)):
                 e_date = earnings_date.date()
            else:
                 e_date = earnings_date # Already date object
            
            link = f"https://finance.yahoo.com/quote/{ticker}"
                
            return {
                "ticker": ticker,
                "name": name,
                "date": e_date,
                "link": link,
                "country": country
            }
            
    except:
        # Fallback on error
        if ticker in US_EARNINGS_EST:
             return {
                "ticker": ticker,
                "name": name,
                "date": US_EARNINGS_EST[ticker],
                "link": f"https://finance.yahoo.com/quote/{ticker}",
                "country": country
            }
        
    return None

def render_monthly_calendar(year, month, events_df):
    """
    Render a visual calendar grid
    """
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    st.markdown(f"### 🗓️ {month_name} {year}")
    
    cols = st.columns(7)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, day in enumerate(days):
        cols[i].markdown(f"**{day}**", help="요일")

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    is_today = (day == datetime.now().day and month == datetime.now().month and year == datetime.now().year)
                    if is_today:
                        st.markdown(f"#### <span style='color:red'>{day}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"#### {day}")
                    
                    if not events_df.empty:
                        day_events = events_df[
                            (events_df['date'].apply(lambda x: x.year) == year) & 
                            (events_df['date'].apply(lambda x: x.month) == month) & 
                            (events_df['date'].apply(lambda x: x.day) == day)
                        ]
                        
                        for _, row in day_events.iterrows():
                            color = "#e3f2fd" if row['country'] == "US" else "#e8f5e9" # Light Blue / Light Green
                            border = "blue" if row['country'] == "US" else "green"
                            
                            st.markdown(
                                f"""
                                <a href="{row['link']}" target="_blank" style="text-decoration:none; color:black;">
                                    <div style="
                                        background-color: {color};
                                        border: 1px solid {border};
                                        border-radius: 4px;
                                        padding: 2px 4px;
                                        margin-bottom: 2px;
                                        font-size: 0.75em;
                                        white-space: nowrap;
                                        overflow: hidden;
                                        text-overflow: ellipsis;
                                    ">
                                        {row['name']}
                                    </div>
                                </a>
                                """, 
                                unsafe_allow_html=True
                            )
        st.markdown("---")

# --- Main App ---

st.title("📅 실적 발표 캘린더")

col1, col2 = st.columns([2, 1])
with col1:
    view_mode = st.radio("보기 모드", ["달력 보기", "리스트 보기"], horizontal=True, label_visibility="collapsed")
with col2:
    filter_my_portfolio = st.toggle("내 보유 종목만 보기", value=False)

# Data Definition
us_tickers = {
    "AAPL": "Apple", "MSFT": "MS", "GOOGL": "Google", "AMZN": "Amazon",
    "NVDA": "NVIDIA", "TSLA": "Tesla", "META": "Meta", "NFLX": "Netflix",
    "AMD": "AMD", "INTC": "Intel", "QCOM": "Qualcomm"
}

kr_tickers = {
    "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "373220.KS": "LG엔솔",
    "207940.KS": "삼바", "005380.KS": "현대차", "000270.KS": "기아",
    "005490.KS": "POSCO", "035420.KS": "NAVER", "035720.KS": "Kakao",
    "105560.KS": "KB금융", "055550.KS": "신한지주"
}

# Add Portfolio Tickers if available
portfolio_tickers = []
if 'calculated_portfolio' in st.session_state and st.session_state.calculated_portfolio is not None:
    try:
        pdf = st.session_state.calculated_portfolio
        # Try to find ticker column
        for col in ['종목코드', 'Ticker', 'ticker', 'code']:
            if col in pdf.columns:
                portfolio_tickers = pdf[col].tolist()
                break
    except: pass

# Fetch Logic
if 'earnings_data' not in st.session_state:
    st.session_state.earnings_data = []

if st.button("🔄 데이터 갱신 (전체 종목)", type="primary"):
    all_events = []
    
    prog = st.progress(0)
    status = st.empty()
    total = len(us_tickers) + len(kr_tickers)
    count = 0
    
    # 1. US Fetch
    for t, n in us_tickers.items():
        count += 1
        status.text(f"US 데이터 조회 중... {n}")
        res = get_calendar_data(t, n, "US")
        if res: all_events.append(res)
        prog.progress(count / total)
    
    # 2. KR Fetch
    for t, n in kr_tickers.items():
        count += 1
        status.text(f"KR 데이터 조회 중... {n}")
        res = get_calendar_data(t, n, "KR")
        if res: all_events.append(res)
        prog.progress(count / total)
        
    status.empty()
    prog.empty()
    
    if all_events:
        st.session_state.earnings_data = all_events
        st.success(f"데이터 갱신 완료: 총 {len(all_events)}개 일정")
    else:
        st.warning("예정된 실적 발표 정보를 찾지 못했습니다.")

# --- Filter & Render ---

if st.session_state.earnings_data:
    df = pd.DataFrame(st.session_state.earnings_data)
    
    # Apply Portfolio Filter
    if filter_my_portfolio and portfolio_tickers:
        # Normalize tickers for comparison (remove .KS etc)
        # Create a set of normalized portfolio tickers
        p_set = set([str(x).replace('.KS','').replace('.KQ','').upper() for x in portfolio_tickers])
        
        # Add a flag for filtering
        # Check if row ticker (normalized) is in p_set
        df['is_mine'] = df['ticker'].apply(
            lambda x: str(x).replace('.KS','').replace('.KQ','').upper() in p_set
        )
        
        # Filter
        df = df[df['is_mine']]
        
        if df.empty:
            st.info("보유 종목 중 예정된 실적 발표가 없습니다.")
    
    if not df.empty:
        if view_mode.startswith("달력"):
            today = datetime.now()
            df['sort_date'] = pd.to_datetime(df['date'])
            unique_dates = df['sort_date'].dt.to_period('M').unique()
            years_months = sorted([(d.year, d.month) for d in unique_dates])
            
            if not years_months:
                years_months = [(today.year, today.month)]
                
            for y, m in years_months[:3]: # Show max 3 months
                render_monthly_calendar(y, m, df)
                
        else:
            st.subheader("📋 실적 발표 리스트")
            
            display_df = df.copy()
            display_df['D-Day'] = display_df['date'].apply(
                lambda x: (x - datetime.now().date()).days
            ).apply(lambda d: "오늘" if d == 0 else (f"D-{d}" if d > 0 else "완료"))
            
            st.dataframe(
                display_df[['date', 'D-Day', 'country', 'name', 'ticker', 'link']],
                column_config={
                    "date": st.column_config.DateColumn("날짜"),
                    "link": st.column_config.LinkColumn("상세 정보"),
                    "country": "국가"
                },
                hide_index=True
            )
else:
    st.info("데이터를 갱신하면 캘린더가 표시됩니다.")