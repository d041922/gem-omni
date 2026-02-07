import sys
import os
import pandas as pd

sys.path.append(os.getcwd())
from skills.data_orchestrator import DataOrchestrator

def test_diagnostic():
    print("--- OMNI DATA FLOW DIAGNOSTIC ---")
    orch = DataOrchestrator()
    
    # 1. 포트폴리오 동기화 실행
    orch.sync_portfolio()
    
    # 2. NVDA 데이터 조회
    data = orch.get_full_ticker_data("NVDA")
    
    last_price = data.get('last_price', 0)
    holding = data.get('holding_info', {})
    avg_p = holding.get('average_price', 0) if holding else "N/A"
    
    print(f"Ticker: NVDA")
    print(f"Market Price: {last_price}")
    print(f"Holding Average: {avg_p}")
    print(f"Holding Raw: {holding}")
    
    return last_price > 0

if __name__ == "__main__":
    test_diagnostic()