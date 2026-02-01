"""
OMNI Commander - GEM: OMNI
Collaborative diagnosis with History & Multi-Expert Intelligence.
"""
import pandas as pd
import os
import yfinance as yf
from skills.gsheet_loader import load_data_from_gsheet, save_audit_log, load_recent_logs
from skills.market_screener import MarketScreener
from skills.technical_indicators import TechnicalAnalyzer
from skills.quant_engine import fetch_historical_prices, calculate_correlation
from skills.sentiment_analyzer import get_news_sentiment
from agents.crews.finance_crew import run_portfolio_audit


def main():
    print("🚀 OMNI Finance System: Strategic Wealth Management Initiated...")

    # 1. Sync Portfolio & History
    print("📥 Syncing portfolio and logs...")
    portfolio_df, watchlist_df, cash_df = load_data_from_gsheet('GEM_Finance_Portfolio')
    if portfolio_df.empty:
        print("❌ Failed to load portfolio.")
        return
    
    recent_history = load_recent_logs('GEM_Finance_Portfolio')
    print(f"📖 Loaded {len(recent_history)} previous logs.")

    # 2. Market Screening
    print("🔍 Screening market for alternatives...")
    screener = MarketScreener()
    candidates = screener.screen_top_candidates()
    candidates_dict = {c['symbol']: c for c in candidates}

    # 3. Data Enrichment (Calculate Missing Values)
    print("💰 Calculating portfolio valuation...")
    exchange_rate = 1450 # Default
    for idx, row in portfolio_df.iterrows():
        ticker = str(row.get('ticker', ''))
        qty = float(row.get('quantity', 0))
        if ticker and qty > 0 and row.get('value_krw', 0) == 0:
            try:
                # Use price from candidates or fetch fresh
                price = candidates_dict.get(ticker, {}).get('price', 0)
                if price == 0:
                    price = yf.Ticker(ticker).history(period='1d')['Close'].iloc[-1]
                
                val = qty * price
                if ".KS" not in ticker and ".KQ" not in ticker:
                    val *= exchange_rate
                portfolio_df.at[idx, 'value_krw'] = val
            except Exception:
                pass

    # 4. Expert Intelligence Gathering (ALL HOLDINGS)
    print("📡 Gathering Intelligence for ALL holdings...")
    intelligence = {}
    
    # Analyze All Holdings + Top 5 Candidates
    target_tickers = [t for t in portfolio_df['ticker'].tolist() if t]
    candidate_tickers = [c['symbol'] for c in candidates[:5]]
    all_targets = list(set([str(t) for t in target_tickers] + candidate_tickers))
    
    # Prices & Correlation
    price_df = fetch_historical_prices(all_targets)
    corr_matrix = calculate_correlation(price_df)
    timing_analyzer = TechnicalAnalyzer()
    
    for ticker in all_targets:
        if not ticker or str(ticker) == "0" or str(ticker) == "nan":
            continue
        print(f"  - Analyzing {ticker}...")
        
        # Expert 1: Sentiment
        sent_data = get_news_sentiment(ticker)
        
        # Expert 2: Timing
        time_data = timing_analyzer.analyze_timing(ticker)
        
        # Expert 3: Risk
        risk_profile = {
            "correlation_with_market": corr_matrix.get("SPY", {}).get(ticker, 0),
            "volatility": price_df[ticker].pct_change().std() if ticker in price_df.columns else 0
        }
        
        intelligence[ticker] = {
            "sentiment": sent_data['sentiment'],
            "timing": time_data,
            "risk": risk_profile
        }

    # 4. Final Calculation & AI Run
    print("🧠 Thinking (Full Collaborative Decision)...")
    cash_balance = 0
    if not cash_df.empty:
        # Sum all numeric-looking columns that might contain cash amounts
        cash_balance = pd.to_numeric(cash_df.iloc[:, -1].astype(str).str.replace(',', ''), errors='coerce').sum()

    market_context = {
        "intelligence": intelligence,
        "market_candidates": candidates[:10],
        "history": recent_history,
        "vix": 15.5 
    }
    
    report = run_portfolio_audit(portfolio_df, cash_balance, market_context)
    if not report or str(report).strip() == "None":
        report = "⚠️ AI 진단 중 오류가 발생하여 보고서를 생성하지 못했습니다. 데이터를 확인하십시오."

    # 5. Output and Log
    report_path = "docs/reports/DAILY_STAFF_REPORT.md"
    try:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(str(report))
        print(f"✅ Report generated: {report_path}")
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
    
    # 6. Save Log back to GSheet
    log_entry = {
        "summary": "Full Strategic Collaboration Audit",
        "actions": "Rebalancing Orders Generated",
        "decisions": report[:1000] # Save top part
    }
    save_audit_log('GEM_Finance_Portfolio', log_entry)
    
    print("\n" + "="*50)
    print(report)
    print("="*50)

if __name__ == "__main__":
    main()
