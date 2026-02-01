"""
Technical Indicators Engine [Safe Edition]
Calculates RSI, MACD, Moving Averages safely.
"""
import pandas as pd

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1]) if not rsi.empty else 50.0

def calculate_macd(prices: pd.Series) -> dict:
    if len(prices) < 26:
        return {"macd": 0.0, "signal": 0.0}
    exp1 = prices.ewm(span=12, adjust=False).mean()
    exp2 = prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return {"macd": float(macd.iloc[-1]), "signal": float(signal.iloc[-1])}