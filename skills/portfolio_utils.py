"""
Portfolio Utility Functions
Unified portfolio data access and checks with GlobalDataManager integration.
Updated: Sector Auto-fill
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, Tuple
from skills.gsheet_loader import load_data_from_gsheet
from skills.finance_core_lib import calculate_portfolio_metrics
from core.data_manager import get_data_manager


def load_portfolio_data(force_refresh: bool = False) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Unified portfolio data loader with central caching via GlobalDataManager.
    Includes Sector Auto-fill logic.
    """
    if not force_refresh and 'calculated_portfolio' in st.session_state:
        return st.session_state.calculated_portfolio, st.session_state.get('current_prices', {})

    dm = get_data_manager()

    try:
        with st.spinner("⏳ 구글 시트에서 포트폴리오 로드 중..."):
            portfolio_df, watchlist_df, cash_df = load_data_from_gsheet("GEM_Finance_Portfolio")
            st.session_state.raw_portfolio_df = portfolio_df
            st.session_state.watchlist_df = watchlist_df
            st.session_state.cash_df = cash_df

        # Ensure '카테고리' column exists
        if '카테고리' not in portfolio_df.columns:
            if 'Category' in portfolio_df.columns:
                portfolio_df['카테고리'] = portfolio_df['Category']
            else:
                portfolio_df['카테고리'] = 'Unknown'

        with st.spinner("🚀 실시간 데이터 및 섹터 정보 수집 중..."):
            current_prices = {}
            ticker_col = '종목코드' if '종목코드' in portfolio_df.columns else '티커코드'

            if ticker_col in portfolio_df.columns:
                tickers = portfolio_df[ticker_col].dropna().unique()
                
                # Iterate to fetch price AND sector
                for ticker in tickers:
                    try:
                        snapshot = dm.get_stock_snapshot(str(ticker))
                        
                        # 1. Price
                        if "current_price" in snapshot:
                            current_prices[ticker] = snapshot["current_price"]
                        
                        # 2. Sector Auto-fill
                        # If category is missing or Unknown, try to fill it from snapshot
                        mask = (portfolio_df[ticker_col] == ticker) & \
                               ((portfolio_df['카테고리'].isna()) | (portfolio_df['카테고리'] == 'Unknown') | (portfolio_df['카테고리'] == ''))
                        
                        if mask.any() and "sector" in snapshot and snapshot["sector"] != "Unknown":
                            portfolio_df.loc[mask, '카테고리'] = snapshot["sector"]
                            
                    except Exception:
                        pass

        # 4. Calculate metrics
        exchange_rate = 1450  
        calculated_df = calculate_portfolio_metrics(portfolio_df, current_prices, exchange_rate)
        
        # 5. Store in session state
        st.session_state.calculated_portfolio = calculated_df
        st.session_state.current_prices = current_prices
        st.session_state.cash_df = cash_df 
        
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
    
    # [FIX] Use confirmed header: '종목코드'
    col_name = '종목코드' if '종목코드' in portfolio_df_copy.columns else ticker_col
    portfolio_df_copy['_normalized_ticker'] = portfolio_df_copy[col_name].astype(str).str.split('.').str[0].str.upper().str.strip()
    ticker_normalized = str(ticker).split('.')[0].upper().strip()

    # Find match
    match = portfolio_df_copy[portfolio_df_copy['_normalized_ticker'] == ticker_normalized]

    if match.empty:
        return None

    row = match.iloc[0]

    # Extract data safely with precise header mapping
    name = row.get('종목명', ticker)
    quantity = float(str(row.get('수량', 0)).replace(',', ''))
    avg_price_usd = float(str(row.get('평균 단가(USD)', 0)).replace(',', ''))
    avg_price_krw = float(str(row.get('평균 단가(KRW)', 0)).replace(',', ''))
    
    # Deciding currency
    is_kr = ".KS" in str(row.get('종목코드', '')) or ".KQ" in str(row.get('종목코드', ''))
    avg_price = avg_price_krw if is_kr else avg_price_usd
    current_value = float(row.get('평가금액(KRW)', row.get('current_value', 0)))
    profit_loss = float(row.get('손익(KRW)', row.get('profit_loss', 0)))
    return_pct = float(row.get('수익률(%)', row.get('return_pct', 0)))
    sector = row.get('카테고리', row.get('sector', 'Unknown'))
    account = row.get('계좌', row.get('account', 'Unknown'))

    return {
        'ticker': ticker,
        'name': name,
        'quantity': quantity,
        'avg_price': avg_price, # Unified price
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
    total_value = portfolio_df['평가금액(KRW)'].sum() if '평가금액(KRW)' in portfolio_df.columns else 0

    # Build holdings list
    holdings = []
    sector_dist = {}

    for _, row in portfolio_df.iterrows():
        ticker_val = row.get('종목코드', row.get('티커코드', ''))
        name_val = row.get('종목명', row.get('name', ''))
        sector = row.get('카테고리', row.get('sector', 'Unknown'))
        value = row.get('평가금액(KRW)', 0)
        value_pct = (value / total_value * 100) if total_value > 0 else 0

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
    else:
        context += f"- **{ticker} 기존 보유**: 없음\n"

    context += "\n### 섹터 분산 현황\n"
    for sector, pct in sorted(sector_dist.items(), key=lambda x:
        -x[1]):
        context += f"- {sector}: {pct:.1f}%\n"

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

def get_full_portfolio_analysis_context() -> str:
    """
    AI 분석을 위해 포트폴리오의 모든 상세 정보를 텍스트로 가공합니다.
    """
    df = load_portfolio_from_session()
    if df is None or df.empty:
        return "포트폴리오 데이터가 없습니다."

    total_cost = df['매수금액(KRW)'].sum()
    total_value = df['평가금액(KRW)'].sum()
    total_profit = df['손익(KRW)'].sum()
    return_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

    df.nlargest(3, '수익률(%)')
    name_col = '종목명' if '종목명' in df.columns else 'name'
    
    context = "## 포트폴리오 요약\n"
    context += f"- 총 평가금액: ₩{total_value/1e8:.2f}억\n"
    context += f"- 총 수익률: {return_pct:+.1f}%\n\n"

    context += "### 전체 보유 종목 상세\n"
    for _, row in df.iterrows():
        ticker = row.get('티커코드', row.get('종목코드', 'N/A'))
        val_pct = (row['평가금액(KRW)'] / total_value * 100) if total_value > 0 else 0
        context += f"- {row[name_col]} ({ticker}): 비중 {val_pct:.1f}%, 수익률 {row['수익률(%)']:.1f}%\n"

    return context