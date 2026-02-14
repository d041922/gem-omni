import sys
import os
import json
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_manager import get_data_manager

def test_data_manager():
    dm = get_data_manager()
    
    print("--- 1. Testing Market Indices ---")
    indices = dm.get_market_indices()
    print(json.dumps(indices, indent=2))
    
    print("\n--- 2. Testing Stock Snapshot (AAPL) ---")
    snapshot = dm.get_stock_snapshot("AAPL")
    print(json.dumps(snapshot, indent=2))

    print("\n--- 3. Testing Cache Hit ---")
    start = time.time()
    dm.get_stock_snapshot("AAPL")
    print(f"Second call took: {time.time() - start:.4f}s")

if __name__ == "__main__":
    test_data_manager()
