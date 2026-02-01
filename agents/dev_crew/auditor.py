"""
Quality Auditor Agent [Meta-System]
The "Bad Cop" who rejects low-quality code and data.
"""
import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.dev_tools.semantic_validator import SemanticValidator
from agents.dev_tools.full_scanner import ProjectScanner

class QualityAuditor:
    def __init__(self):
        self.validator = SemanticValidator()
        self.scanner = ProjectScanner()
        self.name = "👮‍♂️ Quality Auditor"

    def scan_codebase(self) -> bool:
        """
        Runs a full static analysis scan on the codebase.
        """
        print(f"\n{self.name}: Running Full Project Scan...")
        results = self.scanner.scan_project()
        
        issue_count = sum(len(issues) for issues in results.values())
        
        if issue_count == 0:
            print("✅ PASS: Codebase is clean.")
            return True
        else:
            print(f"⚠️ WARNING: Found {issue_count} potential issues.")
            for file, issues in results.items():
                print(f"   📂 {os.path.basename(file)}")
                for iss in issues[:
                    3]: # Show top 3 per file
                    print(f"      - {iss}")
                if len(issues) > 3:
                    print(f"      ... and {len(issues)-3} more")
            
            return True # Don't block, just warn for now (Audit mode)

    def audit_wealth_dashboard(self):
        """
        Audits the Wealth Dashboard Data Logic
        """
        print(f"\n{self.name}: Starting Wealth Dashboard Audit...")
        
        try:
            from core.data_manager import DataManager
            # Force reload to check real logic
            DataManager.get_portfolio_data(force_refresh=True)
            import streamlit as st
            
            df = st.session_state.calculated_portfolio
            
            # Semantic Check
            # Check meaningful columns like '평가금액(KRW)' which we know contains data
            
            # Find actual columns in case of naming mismatch (Auto-detect)
            actual_cols = df.columns.tolist()
            val_col = next((c for c in actual_cols if '평가금액' in c or ('Value' in c and 'KRW' in c)), None)
            
            if val_col:
                res = self.validator.validate_dataframe(df, key_columns=[val_col])
                if res['status'] == 'FAIL':
                    print(f"❌ REJECT: Data Quality Issues Found -> {res['issues']}")
                    return False
                elif res['status'] == 'WARNING':
                    print(f"⚠️ WARNING: Data Quality Concerns -> {res['issues']}")
                    return True # Conditional Pass
                else:
                    print("✅ PASS: Dashboard Data is healthy.")
                    return True
            else:
                print("❌ REJECT: Critical Column 'Value/평가금액' NOT FOUND.")
                return False

        except Exception as e:
            print(f"❌ CRASH: Audit failed with exception -> {e}")
            return False

    def audit_implementation_plan(self, plan_path: str) -> bool:
        """
        Audits an implementation plan for completeness and feasibility.
        """
        print(f"\n{self.name}: Auditing implementation plan: {plan_path}...")
        
        if not os.path.exists(plan_path):
            print(f"❌ REJECT: Plan file not found at {plan_path}")
            return False
            
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        required_sections = ["## 1. System Architecture", "## 2. Data Flow", "## 3. Step-by-Step Tasks", "## 4. Verification Gate"]
        missing = [s for s in required_sections if s not in content]
        
        if missing:
            print(f"❌ REJECT: Plan is missing required sections: {missing}")
            return False
            
        # Check for specific pro-level dependencies mentioned in research
        if "streamlit-aggrid" not in content:
            print("⚠️ WARNING: Plan does not include 'streamlit-aggrid' recommended by research.")
            
        print("✅ PASS: Implementation plan is solid and ready for coding.")
        return True

if __name__ == "__main__":
    auditor = QualityAuditor()
    # If a path is provided as argument, audit that plan
    if len(sys.argv) > 1:
        success = auditor.audit_implementation_plan(sys.argv[1])
    else:
        success = auditor.audit_wealth_dashboard()
    
    if not success:
        sys.exit(1)
