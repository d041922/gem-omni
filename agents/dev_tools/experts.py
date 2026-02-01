"""
Experts v1.1: Knowledge Transfuser
[Upgrade] Added 'Knowledge Transfusion' to rescue a failing Pilot.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, List

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from agents.dev_tools.key_loader import load_google_api_key

class BaseExpert:
    def __init__(self):
        self.api_key = load_google_api_key()
        self.client = genai.Client(api_key=self.api_key) if HAS_GENAI and self.api_key else None

class DeepResearchExpert(BaseExpert):
    def execute(self, mission: str) -> str:
        print(f"🌐 [Expert] Deep Research 강제 가동...")
        prompt = f"""
        Research this mission: {mission}. 
        You MUST provide a concrete technical specification.
        NEVER say 'I cannot' or 'TBD'. If unsure, find the most likely best practice.
        Output a full, actionable spec.md content.
        """
        try:
            res = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            return res.text
        except Exception as e:
            return f"Critical Research Failure: {e}"

class ExaExpert(BaseExpert):
    def get_rescue_samples(self, issue: str) -> str:
        """지적받은 문제를 해결할 실제 코드 샘플 수혈"""
        print(f"🚑 [Expert] 지식 수혈 중: {issue[:50]}...")
        prompt = f"Find 3 real-world python code examples to solve this issue: {issue}. Provide only the most robust patterns."
        try:
            res = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            return res.text
        except:
            return "No rescue samples found."

class CodeReviewerExpert(BaseExpert):
    def validate(self, code: str, spec: str, history: str = "") -> Dict[str, Any]:
        print(f"🧐 [Expert] 냉혹한 감리 중...")
        prompt = f"""
        Review this code. 
        [SPEC] {spec}
        [CODE] {code}
        [HISTORY] {history}

        [STRICT RULES]
        1. If the code is a placeholder (pass, TODO, safety-only) -> score 0.
        2. If it doesn't solve the core problem in the Spec -> score 0.
        3. Catch 'Fake Diligence' (adding minor tricks to hide empty logic).

        Output JSON: {{ "score": 0-100, "passed": bool, "is_stagnant": bool, "critique": "str", "progress": "str" }}
        """
        try:
            res = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(res.text)
        except:
            return {"score": 0, "passed": False, "critique": "Reviewer Offline", "is_stagnant": False}