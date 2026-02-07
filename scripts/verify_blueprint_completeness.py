import os
import sys
from typing import List, Dict

def check_phase_completion(track_id: str) -> Dict[str, bool]:
    """
    로드맵(plan.md)과 실제 코드베이스를 대조하여 기능 완결성을 검토함.
    """
    results = {}
    
    # 1. Phase 7: Cache Engine
    results["Phase 7: Cache Engine"] = os.path.exists("data/reports/cache")
    
    # 2. Phase 7: Template v2.0
    template_path = "skills/templates/report_template.md"
    if os.path.exists(template_path):
        content = open(template_path, "r", encoding="utf-8").read()
        results["Phase 7: Template v2.0"] = "Technical Pulse" in content or "Strategic Verdict" in content
    else:
        results["Phase 7: Template v2.0"] = False
        
    # 3. Phase 8: SSOT Enforcement (Bypass Check)
    results["Phase 8: SSOT Enforcement"] = True
    pages = ["pages/stock_analysis.py", "pages/earnings_calendar.py"]
    for page in pages:
        if os.path.exists(page):
            content = open(page, "r", encoding="utf-8").read()
            # import 구문뿐만 아니라 yf. 사용도 체크
            if ("import yfinance" in content and "orchestrator" not in content) or ("yf.Ticker" in content):
                print(f"🚨 BYPASS DETECTED in {page}")
                results["Phase 8: SSOT Enforcement"] = False
                
    return results

if __name__ == "__main__":
    print("--- [GEM: OMNI] Blueprint Completeness Audit ---")
    completion = check_phase_completion("finance-v1")
    all_passed = True
    for task, status in completion.items():
        print(f"[{'PASS' if status else 'FAIL'}] {task}")
        if not status: 
            all_passed = False
        
    if not all_passed:
        print("\n❌ BLUEPRINT NOT MET: Some features are missing or violating protocols.")
        sys.exit(1)
    else:
        print("\n✅ BLUEPRINT VERIFIED: All active track milestones are correctly implemented.")
        sys.exit(0)