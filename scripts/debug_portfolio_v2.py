from skills.data_orchestrator import DataOrchestrator
import json

def debug_sync():
    orch = DataOrchestrator()
    print("--- Starting Portfolio Sync Debug ---")
    success = orch.sync_portfolio()
    print(f"Sync Success: {success}")
    
    state = orch.read_state()
    holdings = state.get('data', {}).get('portfolio', {}).get('holdings', [])
    print(f"\n--- Stored Portfolio ({len(holdings)} items) ---")
    for h in holdings:
        print(f"Ticker: {h['ticker']}, Qty: {h['quantity']}, Avg: {h['average_price']}, Curr: {h['current_price']}")

    print("\n--- Test Matching ---")
    for t in ['005930.KS', '000660.KS', 'NVDA', 'AMZN', 'PLTR', 'META']:
        print(f"\nTesting {t}:")
        data = orch.get_full_ticker_data(t)
        if data.get('is_owned'):
            print(f"MATCH FOUND: {data['holding_info']}")
        else:
            print("MATCH FAILED")

if __name__ == '__main__':
    debug_sync()