"""
Quant Engine [Safe Edition]
Performs mathematical quant analysis without hardcoded zero risks.
"""
import pandas as pd
import numpy as np

def calculate_volatility(prices: pd.Series) -> float:
    if prices.empty:
        return 0.0
    return float(prices.pct_change().std() * np.sqrt(252))