"""
Portfolio Utility Functions
Unified portfolio data access and checks

Solves:
  - stock_analysis.py와 stock_analysis_crew.py의 포트폴리오 체크 로직 불일치 문제
  - 중복 코드 제거

Usage:
    from skills.portfolio_utils import check_portfolio_holding, get_portfolio_context_for_ai

    # Check if ticker is in portfolio
    holding = check_portfolio_holding('NVDA')
    if holding:
        print(f"보유 중: {holding['quantity']}주, 수익률 {holding['return_pct']}%")

    # Get AI context
    context = get_portfolio_context_for_ai('NVDA')
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any


def load_portfolio_from_session() -> Optional[pd.DataFrame]:
    """
    Load portfolio from session state

    Returns:
        Portfolio DataFrame or None if not available
    """
    if 'calculated_portfolio' in st.session_state:
        return st.session_state.calculated_portfolio
    elif 'raw_portfolio_df' in st.session_state:
        return st.session_state.raw_portfolio_df
    else:
        return None


def check_portfolio_holding(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Check if ticker is in user's portfolio (UNIFIED VERSION)

    Solves: stock_analysis.py:20-57 vs stock_analysis_crew.py:119-150 불일치

    Args:
        ticker: Stock ticker (e.g., 'NVDA', '005930.KS')

    Returns:
        Dict with holding info or None if not found

        Example return:
        {
            'ticker': 'NVDA',
            'name': '엔비디아',
            'quantity': 100.0,
            'avg_price_usd': 120.5,
            'avg_price_krw': 174725.0,
            'current_value': 20000000.0,
            'profit_loss': 3000000.0,
            'return_pct': 15.0,
            'sector': 'AI/반도체',
            'account': 'ISA 계좌'
        }
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

    # Extract data (handle multiple possible column names)
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

    Used by: stock_analysis_crew.py

    Args:
        ticker: Stock ticker to check

    Returns:
        Markdown formatted portfolio context for AI prompt
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

    Returns:
        {
            'total_value': float,
            'total_cost': float,
            'total_profit': float,
            'return_pct': float,
            'num_holdings': int,
            'sectors': Dict[str, float]  # sector -> percentage
        }
    """
    portfolio_df = load_portfolio_from_session()

    if portfolio_df is None or portfolio_df.empty:
        return None

    total_value = portfolio_df.get('평가금액(KRW)', pd.Series([0])).sum()
    total_cost = portfolio_df.get('매수금액(KRW)', pd.Series([0])).sum()
    total_profit = portfolio_df.get('손익(KRW)', pd.Series([0])).sum()
    return_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

    # Sector distribution
    sectors = {}
    if '카테고리' in portfolio_df.columns and '평가금액(KRW)' in portfolio_df.columns:
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


# Example usage
if __name__ == '__main__':
    # This would be run in Streamlit context
    print("Portfolio Utils - Test (requires Streamlit session_state)")

    # Example 1: Check holding
    # holding = check_portfolio_holding('NVDA')
    # if holding:
    #     print(f"Found: {holding['name']}, {holding['quantity']} shares")

    # Example 2: Get AI context
    # context = get_portfolio_context_for_ai('NVDA')
    # print(context)
