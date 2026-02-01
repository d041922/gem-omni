"""
Requirements Analyst (Interpreter) [Meta-System] - v2.0
Robustly extracts Intent and Target from user input without hardcoding.
"""
from typing import Dict

class RequirementsAnalyst:
    def __init__(self):
        self.name = "🗣️ Requirements Analyst"

    def analyze(self, user_input: str) -> Dict:
        print(f"{self.name}: Analyzing request -> '{user_input}'...")
        
        # Lowercase for analysis
        low_input = user_input.lower()
        
        # Default Spec
        spec = {
            "intent": "feature_enhancement",
            "target": "specific_module",
            "domain": "wealth",
            "original_request": user_input
        }

        # 1. Intent Classification
        if any(k in low_input for k in ["진단", "검수", "audit", "check", "diagnosis"]):
            spec["intent"] = "system_audit"
        elif any(k in low_input for k in ["고쳐", "수정", "fix", "repair"]):
            spec["intent"] = "bug_fix"
        elif any(k in low_input for k in ["추가", "만들어", "add", "create"]):
            spec["intent"] = "new_feature"

        # 2. Target Identification
        if any(k in low_input for k in ["전체", "프로젝트", "all", "full", "system"]):
            spec["target"] = "entire_project"
        elif "market" in low_input or "마켓" in low_input:
            spec["target"] = "pages/wealth_screens/market.py"
        elif "dashboard" in low_input or "대시보드" in low_input:
            spec["target"] = "pages/wealth_screens/dashboard.py"
        elif "analysis" in low_input or "분석" in low_input:
            spec["target"] = "pages/wealth_screens/analysis.py"

        print(f"✅ Spec Decoded: {spec['intent']} ON {spec['target']}")
        return spec

if __name__ == "__main__":
    analyst = RequirementsAnalyst()
    analyst.analyze("프로젝트 전체 진단해줘")
    analyst.analyze("Market 탭에 차트 추가해")