import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=43200) # 12시간 캐시
def fetch_historical_prices(tickers: list) -> pd.DataFrame:
    """
    여러 종목의 1년치 종가 데이터를 다운로드합니다.
    """
    if not tickers:
        return pd.DataFrame()
    
    # 한국 주식 티커 처리 (.KS가 없으면 yfinance가 못 찾을 수 있음)
    # 하지만 이미 app.py 등에서 처리해서 넘겨준다고 가정.
    
    # S&P 500 (SPY) 데이터도 벤치마크용으로 함께 다운로드
    target_tickers = list(set(tickers + ["SPY"]))
    
    try:
        data = yf.download(target_tickers, period="1y", progress=False)['Close']
        return data
    except Exception as e:
        print(f"[QuantEngine] Data download failed: {e}")
        return pd.DataFrame()

def calculate_correlation(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    주가 데이터프레임(종가)을 받아 상관계수 행렬을 반환합니다.
    """
    if price_df.empty:
        return pd.DataFrame()
    
    # 일간 수익률 계산
    returns = price_df.pct_change().dropna()
    
    # 상관계수 행렬
    corr_matrix = returns.corr()
    return corr_matrix

def calculate_portfolio_beta(price_df: pd.DataFrame, weights: dict) -> float:
    """
    포트폴리오의 베타(시장 민감도)를 계산합니다.
    Benchmark: SPY
    """
    if price_df.empty or "SPY" not in price_df.columns:
        return 0.0
    
    returns = price_df.pct_change().dropna()
    market_returns = returns["SPY"]
    
    pf_beta = 0.0
    
    for ticker, weight in weights.items():
        if ticker == "SPY" or ticker not in returns.columns:
            continue
            
        asset_returns = returns[ticker]
        
        # 공분산 / 시장분산 = 베타
        covariance = np.cov(asset_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            beta = 0
        else:
            beta = covariance / market_variance
            
        pf_beta += beta * weight
        
    return pf_beta
