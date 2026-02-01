"""
Data Quality Audit Script [GEM: OMNI]
Checks if the portfolio data logic is producing meaningful results.
"""
import sys
import os
from core.data_manager import DataManager

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def audit_portfolio_data():
    print("🕵️ Starting Data Quality Audit...")
    
    # 1. Load Data
    try:
        DataManager.get_portfolio_data(force_refresh=True)
        # Note: In script mode, session_state might not persist, so we access returned obj
        # But get_portfolio_data stores in session_state. 
        # We need to simulate the environment or modify get_portfolio_data to return values directly for testing.
        # Actually, get_portfolio_data returns 'st.session_state.portfolio_obj'
        
        # HACK: Access the logic directly to verify DataFrame construction
        from skills.gsheet_loader import load_data_from_gsheet
        from skills.finance_core_lib import calculate_portfolio_metrics
        
        p_df, w_df, c_df = load_data_from_gsheet("GEM_Finance_Portfolio")
        print(f"✅ GSheet Loaded: {len(p_df)} rows")
        print(f"   Columns: {p_df.columns.tolist()}")
        
        # Check raw columns before calculation
        # Expected: '평가금액(KRW)' might be missing or named differently
        
        # 2. Check Price Fetching
        # Mock prices for audit speed
        current_prices = {t: 100.0 for t in p_df['종목코드'].unique()}
        
        # 3. Calculate
        # We need to see what calculate_portfolio_metrics produces
        calc_df = calculate_portfolio_metrics(p_df, current_prices, 1450.0)
        
        print("\n📊 Calculation Result Audit:")
        print(f"   Rows: {len(calc_df)}")
        print(f"   Columns: {calc_df.columns.tolist()}")
        
        # 4. Value Check (The '0' Problem)
        # Look for columns that might contain value
        val_cols = [c for c in calc_df.columns if '평가금액' in c or 'Value' in c or 'value' in c]
        print(f"   Value Columns Candidates: {val_cols}")
        
        for vc in val_cols:
            total = calc_df[vc].sum()
            zeros = (calc_df[vc] == 0).sum()
            print(f"   -> Column '{vc}': Total={total:,.0f}, Zeros={zeros}/{len(calc_df)}")
            
            if total == 0:
                print("   ❌ CRITICAL: Total Value is 0! Calculation Logic Failed.")
            else:
                print("   ✅ Value seems present.")

        # 5. Category Check
        cat_cols = [c for c in calc_df.columns if '카테고리' in c or 'Category' in c or 'sector' in c]
        print(f"\n🏷️ Category Audit:")
        for cc in cat_cols:
            unknowns = (calc_df[cc] == 'Unknown').sum()
            print(f"   -> Column '{cc}': Unknowns={unknowns}/{len(calc_df)}")
            print(f"      Unique Values: {calc_df[cc].unique()}")

    except Exception as e:
        print(f"❌ Audit Crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    audit_portfolio_data()
