import pandas as pd
import numpy as np

def calculate_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    """일목균형표 (전환선, 기준선, 선행스팬 A/B) 계산"""
    if df.empty: return df
    
    # 전환선: (과거 9일 고가 + 저가) / 2
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2

    # 기준선: (과거 26일 고가 + 저가) / 2
    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2

    # 선행스팬 A: (전환선 + 기준선) / 2, 26일 앞
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

    # 선행스팬 B: (과거 52일 고가 + 저가) / 2, 26일 앞
    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

    # 후행스팬: 현재 종가를 26일 뒤로 (AI 분석용으로 현재 시점 값만 쓰면 됨)
    df['chikou_span'] = df['Close'].shift(-26)
    
    return df

def calculate_bollinger_bands(df: pd.DataFrame, window=20) -> pd.DataFrame:
    """볼린저 밴드 계산"""
    if df.empty: return df
    
    sma = df['Close'].rolling(window=window).mean()
    std = df['Close'].rolling(window=window).std()
    
    df['bb_upper'] = sma + (std * 2)
    df['bb_lower'] = sma - (std * 2)
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / sma
    
    return df

def calculate_fibonacci_levels(df: pd.DataFrame, period=120) -> dict:
    """최근 N일 고점/저점 기준 피보나치 레벨 계산"""
    if len(df) < period: return {}
    
    recent_df = df.iloc[-period:]
    high_val = recent_df['High'].max()
    low_val = recent_df['Low'].min()
    diff = high_val - low_val
    
    levels = {
        "0.0 (High)": high_val,
        "0.236": high_val - diff * 0.236,
        "0.382": high_val - diff * 0.382,
        "0.5 (Mid)": high_val - diff * 0.5,
        "0.618": high_val - diff * 0.618,
        "1.0 (Low)": low_val
    }
    return levels
