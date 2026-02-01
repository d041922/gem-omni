"""
Template Agent [Safe Edition]
Clean starting point for new agents.
"""
from typing import Dict, Any

class TemplateAgent:
    def __init__(self):
        self.name = "Template Agent"

    def run_task(self, task: str) -> Dict[str, Any]:
        return {"status": "success", "result": f"Task '{task}' completed."}