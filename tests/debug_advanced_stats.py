import sys
import os
import pandas as pd

sys.path.append(os.getcwd())
from skills.data_orchestrator import DataOrchestrator

def test_extra_stats():
    print("--- OMNI ADVANCED DATA DIAGNOSTIC ---")
    orch = DataOrchestrator()
    
    print("Fetching advanced stats for NVDA...")
    data = orch.get_full_ticker_data("NVDA")
    
    extra = data.get("extra_stats", {})
    fin = extra.get("financials", {})
    mkt = extra.get("market_stats", {})
    analyst = extra.get("analyst_opinions", {})
    
    print(f"ROE: {fin.get('roe')}")
    print(f"52w High: {mkt.get('high_52w')}")
    print(f"Target Mean: {analyst.get('target_mean')}")
    
    return fin.get('roe') is not None

if __name__ == "__main__":
    test_extra_stats()