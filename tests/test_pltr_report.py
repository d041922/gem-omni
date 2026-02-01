
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from skills.stock_analyzer import analyze_stock, generate_ai_analysis

def test_investing_style_report():
    ticker = "PLTR"
    print(f"--- Generating Investing.com Style Report for {ticker} ---")
    
    # 1. Analyze
    result = analyze_stock(ticker)
    if not result.get("success"):
        print(f"Analysis failed: {result.get('error')}")
        return

    # 2. Print Summary Data
    s = result["summary"]
    p = s["performance"]
    a = s["analysts"]
    
    print(f"\n[Basic Info]")
    print(f"Price: ${s['current_price']:.2f} ({s['price_change_pct']:.2f}%)")
    print(f"52W Range: ${s['stats']['52week_low']:.2f} - ${s['stats']['52week_high']:.2f}")
    
    print(f"\n[Performance Table]")
    for period in ["1w", "1m", "3m", "6m", "1y", "5y"]:
        print(f"{period}: {p.get(period, 0):.2f}%")
        
    print(f"\n[Analyst Sentiment]")
    print(f"Opinion: {a['recommendation']} (by {a['num_analysts']} analysts)")
    print(f"Target: Mean ${a['target_mean']:.2f} (High ${a['target_high']:.2f} / Low ${a['target_low']:.2f})")

    # 3. Generate AI Report
    print(f"\n--- AI Analysis (Deep Report) ---")
    ai_report = generate_ai_analysis(result)
    print(ai_report)

if __name__ == "__main__":
    load_dotenv()
    test_investing_style_report()
