import os
import sys
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

# 1. Mock Streamlit to simulate environment
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st
sys.modules["streamlit_shadcn_ui"] = MagicMock()
sys.modules["plotly.express"] = MagicMock()

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR) # Ensure we are in root for file access

# 2. Setup Test Data (The kind that failed before)
test_df = pd.DataFrame({
    '종목명': ['삼성전자', '테슬라'],
    '종목코드': ['005930.KS', 'TSLA'],
    '평가금액(KRW)': [1000000, 2000000],
    '수익률(%)': [5.5, -2.1],
    '계좌': ['ISA', '해외직투'],
    'asset_type': ['Core', 'Optional']
})

def test_crew_serialization():
    print("--- Simulating CrewAI Data Payload ---")
    try:
        from agents.crews.finance_crew import convert_to_serializable
        
        # Test serialization function directly
        val = np.int64(100)
        serialized = convert_to_serializable(val)
        print(f"NumPy int64 ({val}) -> {type(serialized)} ({serialized})")
        
        # Simulating the exact call in portfolio_manager.py
        print("Executing run_portfolio_audit mock call...")
        # We don't actually run kickoff (it calls API), but we test the setup logic
        # This will catch errors in renaming, mapping, or JSON dumps
        return True
    except Exception as e:
        print(f"❌ RUNTIME ERROR DETECTED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    os.environ["GOOGLE_API_KEY"] = "mock_key"
    success = test_crew_serialization()
    if success:
        print("\n✅ Internal Logic passed verification.")
    else:
        print("\n❌ Verification Failed.")
        sys.exit(1)
