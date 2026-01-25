"""
Portfolio Utility Functions
Unified portfolio data access and checks

Solves:
  - stock_analysis.py와 stock_analysis_crew.py의 포트폴리오 체크 로직 불일치 문제
  - 중복 코드 제거
  - 홈 화면 및 각 페이지 데이터 로딩 통합
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from typing import Optional, Dict, Any, Tuple
from skills.gsheet_loader import load_data_from_gsheet
from skills.finance_core_lib import calculate_portfolio_metrics


def load_portfolio_data(force_refresh: bool = False) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Unified portfolio data loader with caching.
    Ensures data is available for all pages (Home, Dashboard, Analysis).

    Args:
        force_refresh: If True, bypass cache and reload from GSheet/YFinance

    Returns:
        (calculated_df, current_prices_dict)
    """
    # 1. Check if already in session state and not forcing refresh
    if not force_refresh and 'calculated_portfolio' in st.session_state:
        return st.session_state.calculated_portfolio, st.session_state.get('current_prices', {})

    # 2. Load from Google Sheets
    try:
        # Use a container for status messages if we're in a script with UI
        with st.spinner("⏳ 구글 시트에서 포트폴리오 로드 중..."):
            portfolio_df, watchlist_df, cash_df = load_data_from_gsheet("GEM_Finance_Portfolio")
            st.session_state.raw_portfolio_df = portfolio_df
            st.session_state.watchlist_df = watchlist_df
            st.session_state.cash_df = cash_df

        # 3. Fetch current prices
        with st.spinner("🚀 실시간 주가 데이터 수집 중..."):
            current_prices = {}
            ticker_col = '종목코드' if '종목코드' in portfolio_df.columns else '티커코드'

            if ticker_col in portfolio_df.columns:
                tickers = portfolio_df[ticker_col].dropna().unique()
                for ticker in tickers:
                    try:
                        # Optimization: Use existing price if not forcing refresh
                        if not force_refresh and 'current_prices' in st.session_state and ticker in st.session_state.current_prices:
                            current_prices[ticker] = st.session_state.current_prices[ticker]
                            continue
                            
                        stock = yf.Ticker(str(ticker))
                        # Use fast_info for performance
                        price = stock.fast_info.get('last_price', None)
                        if price is None:
                            hist = stock.history(period='1d')
                            if not hist.empty:
                                price = hist['Close'].iloc[-1]
                        
                        if price:
                            current_prices[ticker] = float(price)
                    except:
                        pass

        # 4. Calculate metrics
        exchange_rate = 1450  # TODO: Fetch real exchange rate
        calculated_df = calculate_portfolio_metrics(portfolio_df, current_prices, exchange_rate)
        
        # 5. Store in session state
        st.session_state.calculated_portfolio = calculated_df
        st.session_state.current_prices = current_prices
        st.session_state.cash_df = cash_df # Ensure cash_df is explicitly saved here
        
        return calculated_df, current_prices

    except Exception as e:
        st.error(f"포트폴리오 로딩 실패: {e}")
        return pd.DataFrame(), {}


def load_portfolio_from_session() -> Optional[pd.DataFrame]:
    """
    Load portfolio from session state or load it if missing
    """
    if 'calculated_portfolio' in st.session_state:
        return st.session_state.calculated_portfolio
    else:
        df, _ = load_portfolio_data()
        return df if not df.empty else None


def check_portfolio_holding(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Check if ticker is in user's portfolio (UNIFIED VERSION)
    """
    portfolio_df = load_portfolio_from_session()

    if portfolio_df is None or portfolio_df.empty:
        return None

    # Find ticker column
    ticker_col = None
    for col in ['종목코드', '티커코드', 'ticker']:
        if col in portfolio_df.columns:
            ticker_col = col
            break

    if ticker_col is None:
        return None

    # Normalize ticker for comparison
    portfolio_df_copy = portfolio_df.copy()
    portfolio_df_copy['_normalized_ticker'] = portfolio_df_copy[ticker_col].astype(str).str.upper().str.strip()
    ticker_normalized = str(ticker).upper().strip()

    # Find match
    match = portfolio_df_copy[portfolio_df_copy['_normalized_ticker'] == ticker_normalized]

    if match.empty:
        return None

    row = match.iloc[0]

    # Extract data
    name = row.get('종목명', row.get('name', ticker))
    quantity = float(row.get('수량', 0))
    avg_price_usd = float(row.get('평균 단가(USD)', row.get('avg_price_usd', 0)))
    avg_price_krw = float(row.get('평균 단가(KRW)', row.get('avg_price_krw', 0)))
    current_value = float(row.get('평가금액(KRW)', row.get('current_value', 0)))
    profit_loss = float(row.get('손익(KRW)', row.get('profit_loss', 0)))
    return_pct = float(row.get('수익률(%)', row.get('return_pct', 0)))
    sector = row.get('카테고리', row.get('sector', 'Unknown'))
    account = row.get('계좌', row.get('account', 'Unknown'))

    return {
        'ticker': ticker,
        'name': name,
        'quantity': quantity,
        'avg_price_usd': avg_price_usd,
        'avg_price_krw': avg_price_krw,
        'current_value': current_value,
        'profit_loss': profit_loss,
        'return_pct': return_pct,
        'sector': sector,
        'account': account
    }


def get_portfolio_context_for_ai(ticker: str) -> str:
    """
    Generate portfolio context text for AI agents (UNIFIED VERSION)
    """
    portfolio_df = load_portfolio_from_session()

    if portfolio_df is None or portfolio_df.empty:
        return "\n## 📊 현재 포트폴리오 정보\n- 포트폴리오 데이터 없음\n"

    # Calculate total value
    total_value = 0
    if '평가금액(KRW)' in portfolio_df.columns:
        total_value = portfolio_df['평가금액(KRW)'].sum()
    elif 'current_value' in portfolio_df.columns:
        total_value = portfolio_df['current_value'].sum()

    # Build holdings list
    holdings = []
    sector_dist = {}

    for _, row in portfolio_df.iterrows():
        ticker_val = row.get('종목코드', row.get('티커코드', ''))
        name_val = row.get('종목명', row.get('name', ''))
        sector = row.get('카테고리', row.get('sector', 'Unknown'))
        value = row.get('평가금액(KRW)', row.get('current_value', 0))
        value_pct = (value / total_value * 100) if total_value > 0 else 0

        # Accumulate sector distribution
        sector_dist[sector] = sector_dist.get(sector, 0) + value_pct

        holdings.append({
            'ticker': str(ticker_val),
            'name': str(name_val),
            'sector': sector,
            'value': value,
            'value_pct': value_pct
        })

    # Check if target ticker exists in portfolio
    existing_position = check_portfolio_holding(ticker)

    # Format context
    context = f"""
## 📊 현재 포트폴리오 정보
- 총 보유 종목: {len(holdings)}개
- 총 평가금액: ₩{total_value/1e8:.2f}억원
"""

    if existing_position:
        context += f"- **{ticker} 기존 보유**: 있음\n"
        context += f"  - 수익률: {existing_position['return_pct']:.1f}%\n"
        context += f"  - 평가금액: ₩{existing_position['current_value']/1e6:.0f}백만원\n"
        context += f"  - 보유 비중: {(existing_position['current_value']/total_value*100):.1f}%\n"
        context += f"  - 계좌: {existing_position['account']}\n"
    else:
        context += f"- **{ticker} 기존 보유**: 없음 (신규 매수 검토 대상)\n"

    # Sector distribution
    context += "\n### 섹터 분산 현황\n"
    for sector, pct in sorted(sector_dist.items(), key=lambda x: -x[1]):
        context += f"- {sector}: {pct:.1f}%\n"

    # Top 5 holdings
    context += "\n### Top 5 보유 종목\n"
    sorted_holdings = sorted(holdings, key=lambda x: -x['value_pct'])[:5]
    for h in sorted_holdings:
        context += f"- {h['name']} ({h['ticker']}): {h['value_pct']:.1f}%\n"

    return context


def get_portfolio_summary() -> Optional[Dict[str, Any]]:
    """
    Get portfolio summary statistics
    """
    portfolio_df = load_portfolio_from_session()

    if portfolio_df is None or portfolio_df.empty:
        return None

    total_value = portfolio_df['평가금액(KRW)'].sum() if '평가금액(KRW)' in portfolio_df.columns else 0
    total_cost = portfolio_df['매수금액(KRW)'].sum() if '매수금액(KRW)' in portfolio_df.columns else 0
    total_profit = portfolio_df['손익(KRW)'].sum() if '손익(KRW)' in portfolio_df.columns else 0
    return_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

    # Sector distribution
    sectors = {}
    if '카테고리' in portfolio_df.columns:
        sector_values = portfolio_df.groupby('카테고리')['평가금액(KRW)'].sum()
        sectors = {sector: (value / total_value * 100) for sector, value in sector_values.items()}

    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'return_pct': return_pct,
        'num_holdings': len(portfolio_df),
        'sectors': sectors
    }