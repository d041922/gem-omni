from skills.kis_tools import KISConnector
import sys

def test():
    try:
        print("--- KIS API INTEGRATION TEST ---")
        kis = KISConnector()
        
        mode = "PAPER TRADING (Mock)" if kis.is_paper else "REAL TRADING (Actual)"
        print(f"[1] Connection Mode: {mode}")
        
        print("[2] Requesting Access Token & Balance...")
        balance = kis.fetch_balance()
        
        print("\n[3] RESULT: SUCCESS ✅")
        print(f"   - Total Asset Value: {balance['total_eval_amt']:,.0f} KRW")
        print(f"   - Total Profit/Loss: {balance['total_profit_amt']:,.0f} KRW")
        
        holdings = balance['holdings']
        print(f"\n[4] Holdings ({len(holdings)} items):")
        
        if not holdings:
            print("   (No stocks found in this account)")
        
        for h in holdings:
            print(f"   - {h['ticker']} : {h['amount']} shares")
            
    except Exception as e:
        print(f"\n[X] RESULT: FAILED ❌")
        print(f"   - Error: {str(e)}")

if __name__ == "__main__":
    test()
