"""
SOP Compliance & Regression Checker [GEM: OMNI]
Automatically audits code for missing UI components or key logic.
"""
import os

def check_regression(file_path, required_keywords):
    """Checks if specified file contains all required keywords/functions"""
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing = []
    for kw in required_keywords:
        if kw not in content:
            missing.append(kw)
    
    if not missing:
        return "✅ No regression detected. All key components preserved."
    else:
        return f"⚠️ REGRESSION DETECTED! Missing: {', '.join(missing)}"

if __name__ == "__main__":
    # Example: Check Portfolio Manager UI integrity
    portfolio_reqs = ['metric_card', 'stylized_table', 'run_portfolio_audit', 'AssetClassifier']
    print(f"Auditing Portfolio Manager: {check_regression('pages/portfolio_manager.py', portfolio_reqs)}")
    
    # Example: Check Stock Analysis UI integrity
    stock_reqs = ['tab_general', 'tab_tech', 'tab_news', 'tab_finance', 'tab_crew', 'analyze_stock']
    print(f"Auditing Stock Analysis: {check_regression('pages/stock_analysis.py', stock_reqs)}")
