#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import yfinance as yf
from skills.gsheet_loader import load_data_from_gsheet
from skills.finance_core_lib import calculate_portfolio_metrics

sys.stdout.reconfigure(encoding='utf-8')

# Load data
df, _, _ = load_data_from_gsheet('GEM_Finance_Portfolio')

print(f"=== Loaded {len(df)} rows ===")
print(f"\nColumns: {df.columns.tolist()}")

# Show first row
print("\n=== First Row ===")
for col in df.columns:
    print(f"{col}: {df[col].iloc[0]}")

# Find ticker column
ticker_candidates = [c for c in df.columns if 'code' in str(c).lower() or '코드' in str(c)]
if ticker_candidates:
    ticker_col = ticker_candidates[0]
    print(f"\n=== Ticker Column: {ticker_col} ===")
    tickers = df[ticker_col].dropna().unique()
    print(f"Tickers: {tickers[:5]}")

    # Fetch prices
    prices = {}
    for ticker in tickers:
        if ticker and str(ticker).strip():
            try:
                stock = yf.Ticker(str(ticker))
                hist = stock.history(period='1d')
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    prices[ticker] = float(price)
                    print(f"  {ticker}: ${price:.2f}")
            except Exception as e:
                print(f"  {ticker}: FAILED - {e}")

    print(f"\n=== Fetched {len(prices)} prices ===")
    print(prices)

    # Calculate
    result = calculate_portfolio_metrics(df, prices, 1450)

    print("\n=== Results ===")
    name_col = [c for c in result.columns if '명' in str(c) or 'name' in str(c).lower()][0]

    for idx in range(min(5, len(result))):
        row = result.iloc[idx]
        name = row.get(name_col, 'N/A')
        cost = row.get('매수금액(KRW)', 0)
        value = row.get('평가금액(KRW)', 0)
        profit = row.get('손익(KRW)', 0)
        returns = row.get('수익률(%)', 0)
        print(f"{name}: 매수={cost:,.0f}, 평가={value:,.0f}, 손익={profit:,.0f}, 수익률={returns:.2f}%")
else:
    print("ERROR: Ticker column not found")