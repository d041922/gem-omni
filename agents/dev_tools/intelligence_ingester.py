"""
Intelligence Ingester v9.0: Passive Mode
Reliant on the Main Agent (Gemini CLI) for intent refinement.
It simply takes the command and extracts keywords for research.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Path Setup
current_file = Path(__file__).resolve()
root_dir = current_file.parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.dev_tools.key_loader import load_google_api_key

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class IntelligenceIngester:
    def __init__(self):
        self.root_dir = root_dir
        self.api_key = load_google_api_key()
        self.client = genai.Client(api_key=self.api_key) if HAS_GENAI and self.api_key else None

    def analyze_intent(self, mission: str) -> Dict[str, Any]:
        """
        [Passive Analysis]
        Assumes 'mission' is already refined by the Main Agent (Gemini CLI).
        Just generates keywords for the Researcher.
        """
        refined_mission = mission
        
        # Simple Keyword Extraction using LLM (for better search results)
        # If LLM fails, just use the mission string.
        keywords = [mission]
        
        if self.client:
            prompt = f"""
            Extract 3 technical search keywords from this command.
            Command: "{mission}"
            Return JSON: {{ "keywords": ["kw1", "kw2", "kw3"] }}
            """
            try:
                res = self.client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                data = json.loads(res.text)
                keywords = data.get("keywords", [mission])
            except:
                pass

        return {
            "keywords": keywords,
            "refined_mission": refined_mission,
            "clarification_needed": False, # Always trust the Main Agent
            "question": None
        }

    def digest_report(self, report_path: str, current_mission: str) -> Dict:
        path = Path(report_path)
        if not path.exists():
            return {}
        content = path.read_text(encoding="utf-8")
        
        if self.client:
            prompt = f"""
            Summarize report for: "{current_mission}"
            Report: {content[:10000]}...
            Return JSON: {{ "research_summary_ko": "...", "best_practices": [{{ "feature": "...", "description": "..." }}], "metrics": ["..."] }}
            """
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                return json.loads(response.text)
            except:
                pass

        return {
            "research_summary_ko": "Raw Content",
            "best_practices": [{"feature": "Manual Review", "description": "Check report."}],
            "metrics": ["N/A"]
        }