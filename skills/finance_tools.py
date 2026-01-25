import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional

@st.cache_data(ttl=3600) # 1시간 캐시
def search_ticker_by_name(query: str) -> Optional[str]:
    """
    한글명/영문명으로 티커를 검색합니다.
    """
    # 1. 자주 찾는 한국 주식 매핑
    KR_COMMON = {
        "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "현대차": "005380.KS",
        "네이버": "035420.KS", "카카오": "035720.KS", "에코프로": "086520.KQ"
    }
    if query in KR_COMMON:
        return KR_COMMON[query]

    # 2. yfinance를 통한 티커 추론 (간접 방식)
    # 실제로는 전문 검색 API가 좋으나, 무료 환경에서는 티커 직접 입력 권장 문구 반환
    return None

@st.cache_data(ttl=3600) # 주가 데이터 1시간 캐시
def get_cached_history(ticker: str, period: str = "1y"):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA60'] = df['Close'].rolling(window=60).mean()
    df['SMA120'] = df['Close'].rolling(window=120).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + gain / loss.replace(0, 1e-9)))
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

@st.cache_data(ttl=300)  # 5분 캐싱
def fetch_market_data() -> Dict[str, Dict[str, float]]:
    """Fetch real-time market data from yfinance (S&P500, NASDAQ, KOSPI, VIX)"""
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
                # Handle case where 2nd day might not be available yet (e.g. market just opened)
                if not hist.empty:
                    market_data[name] = {'value': hist['Close'].iloc[-1], 'change': 0}
                else:
                    market_data[name] = {'value': 0, 'change': 0}
        except Exception:
            market_data[name] = {'value': 0, 'change': 0}

    return market_data