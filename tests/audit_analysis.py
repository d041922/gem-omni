"""
Analysis Data Quality Audit
Deep dive into analyze_stock() output to find why charts/metrics are failing.
"""
import sys
import os
from skills.stock_analyzer import analyze_stock
from skills.earnings_analyzer import EarningsAnalyzer
from skills.peer_comparison import compare_within_sector

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def audit_analysis(ticker="NVDA"):
    print(f"🕵️ Auditing Analysis Data for {ticker}...")
    
    # 1. Main Analyze Stock
    res = analyze_stock(ticker)
    if not res['success']:
        print(f"❌ analyze_stock failed: {res['error']}")
        return

    s = res['summary']
    f = s['fundamentals']
    
    print(f"\n📊 Fundamentals Check:")
    print(f"   - PE: {f.get('pe')} (Is it 0?)")
    print(f"   - PEG: {f.get('peg')}")
    print(f"   - ROE: {f.get('roe')}")
    
    # 2. Earnings Trend
    ea = EarningsAnalyzer()
    e_res = ea.analyze_earnings_trend(ticker)
    print(f"\n📈 Earnings Trend Check:")
    if 'raw_history' in e_res:
        hist = e_res['raw_history']
        print(f"   - History Records: {len(hist)}")
        if len(hist) > 0:
            print(f"   - Sample: {hist[0]}")
            if hist[0]['revenue'] == 0:
                print("   ❌ Revenue is 0!")
    else:
        print("   ❌ 'raw_history' key MISSING!")

    # 3. Peer Comparison
    p_res = compare_within_sector(ticker)
    print(f"\n🏆 Peer Comparison Check:")
    if 'error' in p_res:
        print(f"   ❌ Error: {p_res['error']}")
    else:
        print(f"   - Peers Found: {len(p_res.get('peers_metrics', []))}")
        print(f"   - Data: {p_res.get('peers_metrics')}")

if __name__ == "__main__":
    audit_analysis("NVDA")
