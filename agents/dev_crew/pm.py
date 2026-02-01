"""
Project Manager (PM) [Meta-System] - v2.0
Dynamic Roadmap Generation based on Intent.
"""
from typing import Dict, List
import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.dev_crew.researcher import ResearchAgent
from agents.dev_crew.architect import ArchitectAgent
from agents.dev_crew.auditor import QualityAuditor

class ProjectManager:
    def __init__(self):
        self.name = "👑 Project Manager"
        self.researcher = ResearchAgent()
        self.architect = ArchitectAgent()
        self.auditor = QualityAuditor()

    def create_roadmap(self, spec: Dict) -> List[Dict]:
        print(f"{self.name}: Creating dynamic roadmap for '{spec['intent']}'...")
        roadmap = []
        
        if spec['intent'] == "system_audit":
            # WORKFLOW: Data Audit -> Code Scan -> Research -> Report
            roadmap.append({
                "step": 1,
                "agent": "Auditor",
                "task": "Portfolio Data Semantic Check",
                "action": lambda: self.auditor.audit_wealth_dashboard(),
                "output_key": "data_audit_result"
            })
            roadmap.append({
                "step": 2,
                "agent": "Auditor",
                "task": "Full Codebase Anti-Pattern Scan",
                "action": lambda: self.auditor.scan_codebase(),
                "output_key": "code_scan_result"
            })
            roadmap.append({
                "step": 3,
                "agent": "Researcher",
                "task": "UX Consistency Review",
                "action": lambda: self.researcher.research_feature("UI Consistency", "Global Project"),
                "output_key": "ux_report"
            })
        else:
            # WORKFLOW: Research -> Design -> Dev -> QA (Standard)
            roadmap.append({
                "step": 1,
                "agent": "Researcher",
                "action": lambda: self.researcher.research_feature(spec['target'], "Standard"),
                "output_key": "res_report"
            })
            # ... (Rest of standard steps)
            
        return roadmap

    def execute_roadmap(self, roadmap: List[Dict]):
        print(f"{self.name}: Executing Roadmap...")
        for step in roadmap:
            print(f"   ▶ Step {step['step']}: {step['agent']} - {step.get('task', 'Working')}...")
            result = step['action']()
            # If fail, stop
            if result is False:
                break
            
        print("🎉 Roadmap Execution Finished.")

if __name__ == "__main__":
    pm = ProjectManager()
    pm.create_roadmap({"intent": "system_audit", "target": "entire_project"})
