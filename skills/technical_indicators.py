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

def calculate_adx(df: pd.DataFrame, period=14) -> pd.DataFrame:
    """
    ADX (Average Directional Index) 계산
    추세의 강도를 측정 (0-100)
    - ADX > 25: 강한 추세
    - ADX < 20: 약한 추세 (횡보)
    """
    if df.empty or len(df) < period + 1:
        return df

    # True Range 계산
    df['tr'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )

    # Directional Movement 계산
    df['up_move'] = df['High'] - df['High'].shift(1)
    df['down_move'] = df['Low'].shift(1) - df['Low']

    df['plus_dm'] = np.where(
        (df['up_move'] > df['down_move']) & (df['up_move'] > 0),
        df['up_move'],
        0
    )
    df['minus_dm'] = np.where(
        (df['down_move'] > df['up_move']) & (df['down_move'] > 0),
        df['down_move'],
        0
    )

    # Smoothed TR and DM
    df['atr'] = df['tr'].rolling(window=period).mean()
    df['plus_di'] = 100 * (df['plus_dm'].rolling(window=period).mean() / df['atr'])
    df['minus_di'] = 100 * (df['minus_dm'].rolling(window=period).mean() / df['atr'])

    # DX and ADX
    df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['adx'] = df['dx'].rolling(window=period).mean()

    # Cleanup temporary columns
    df.drop(['tr', 'up_move', 'down_move', 'plus_dm', 'minus_dm', 'dx'], axis=1, inplace=True)

    return df

def calculate_mfi(df: pd.DataFrame, period=14) -> pd.DataFrame:
    """
    MFI (Money Flow Index) 계산
    가격과 거래량을 결합한 모멘텀 지표 (0-100)
    - MFI > 80: 과매수
    - MFI < 20: 과매도
    """
    if df.empty or len(df) < period + 1:
        return df

    # Typical Price
    df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3

    # Raw Money Flow
    df['raw_money_flow'] = df['typical_price'] * df['Volume']

    # Positive and Negative Money Flow
    df['price_diff'] = df['typical_price'].diff()
    df['positive_flow'] = np.where(df['price_diff'] > 0, df['raw_money_flow'], 0)
    df['negative_flow'] = np.where(df['price_diff'] < 0, df['raw_money_flow'], 0)

    # Money Flow Ratio
    positive_mf = df['positive_flow'].rolling(window=period).sum()
    negative_mf = df['negative_flow'].rolling(window=period).sum()

    mf_ratio = positive_mf / negative_mf
    df['mfi'] = 100 - (100 / (1 + mf_ratio))

    # Handle division by zero
    df['mfi'] = df['mfi'].fillna(50)

    # Cleanup temporary columns
    df.drop(['typical_price', 'raw_money_flow', 'price_diff',
             'positive_flow', 'negative_flow'], axis=1, inplace=True)

    return df

def calculate_parabolic_sar(df: pd.DataFrame, af_start=0.02, af_max=0.20) -> pd.DataFrame:
    """
    Parabolic SAR (Stop and Reverse) 계산
    트레일링 스톱 라인 제공
    - 가격 > SAR: 상승 추세
    - 가격 < SAR: 하락 추세

    Args:
        af_start: 초기 가속 계수 (default: 0.02)
        af_max: 최대 가속 계수 (default: 0.20)
    """
    if df.empty or len(df) < 5:
        df['psar'] = np.nan
        df['psar_trend'] = 0
        return df

    length = len(df)
    psar = np.zeros(length)
    trend = np.zeros(length)
    af = af_start
    ep = 0  # Extreme Point

    # Initialize first values
    psar[0] = df['Low'].iloc[0]
    trend[0] = 1  # 1 for uptrend, -1 for downtrend

    for i in range(1, length):
        # Previous values
        prev_psar = psar[i-1]
        prev_trend = trend[i-1]

        if prev_trend == 1:  # Uptrend
            psar[i] = prev_psar + af * (ep - prev_psar)

            # Make sure SAR is below price
            psar[i] = min(psar[i], df['Low'].iloc[i-1])
            if i > 1:
                psar[i] = min(psar[i], df['Low'].iloc[i-2])

            # Check for trend reversal
            if df['Low'].iloc[i] < psar[i]:
                trend[i] = -1
                psar[i] = ep
                af = af_start
                ep = df['Low'].iloc[i]
            else:
                trend[i] = 1
                if df['High'].iloc[i] > ep:
                    ep = df['High'].iloc[i]
                    af = min(af + af_start, af_max)

        else:  # Downtrend
            psar[i] = prev_psar - af * (prev_psar - ep)

            # Make sure SAR is above price
            psar[i] = max(psar[i], df['High'].iloc[i-1])
            if i > 1:
                psar[i] = max(psar[i], df['High'].iloc[i-2])

            # Check for trend reversal
            if df['High'].iloc[i] > psar[i]:
                trend[i] = 1
                psar[i] = ep
                af = af_start
                ep = df['High'].iloc[i]
            else:
                trend[i] = -1
                if df['Low'].iloc[i] < ep:
                    ep = df['Low'].iloc[i]
                    af = min(af + af_start, af_max)

    df['psar'] = psar
    df['psar_trend'] = trend

    return df
