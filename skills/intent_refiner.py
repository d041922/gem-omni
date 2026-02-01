"""
Intent Refiner Skill [OMNI-Skill] v1.4 (Strict Mode)
Uses Gemini to clarify and refine vague user commands into actionable technical specs.
"""
import os
import json
import sys
from pathlib import Path
from typing import Dict, Any

current_file = Path(__file__).resolve()
root_dir = current_file.parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from agents.dev_tools.key_loader import load_google_api_key
except ImportError:
    load_google_api_key = lambda: os.getenv("GOOGLE_API_KEY")

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class IntentRefiner:
    def __init__(self):
        self.api_key = load_google_api_key()
        self.client = genai.Client(api_key=self.api_key) if HAS_GENAI and self.api_key else None

    def refine(self, raw_command: str, context: str = "") -> Dict[str, Any]:
        if not self.client:
            return {"refined_mission": raw_command, "clarification_needed": False, "reasoning": "AI Offline"}

        prompt = f"""
        You are a STRICT Chief Architect.
        Your job is to prevent vague tasks from reaching the developers.

        User Command: "{raw_command}"
        Current Context: "{context}"

        [CRITICAL RULES]
        1. If the command lacks a specific **Target File** or **Specific Feature**, you MUST set "clarification_needed": true.
        2. "Fix it", "Improve it", "Make it better" -> CLARIFICATION NEEDED.
        3. "Refactor orchestrator.py" -> OK.
        4. "Add error handling to ingestion" -> OK.

        Output JSON ONLY:
        {{
            "refined_mission": "Refined technical spec (or original if vague)",
            "clarification_needed": true/false,
            "question": "Asking for target file/feature (e.g., 'Which file specifically?')",
            "reasoning": "Why you rejected or accepted it."
        }}
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            return {"refined_mission": raw_command, "reasoning": f"Error: {e}"}

if __name__ == "__main__":
    refiner = IntentRefiner()
    # Test Vague Command
    print(json.dumps(refiner.refine("Fix it"), indent=2))
