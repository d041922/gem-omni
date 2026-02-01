"""
Code Reviewer [Dev Tool] v1.1
Automated code quality assurance agent.
Uses Gemini 2.0 Flash for high-speed review.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Tuple

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

class CodeReviewer:
    def __init__(self):
        self.api_key = load_google_api_key()
        self.client = genai.Client(api_key=self.api_key) if HAS_GENAI and self.api_key else None

    def review_code(self, file_path: str) -> Tuple[bool, str]:
        """
        Reviews the target file using the latest Gemini model.
        """
        if not self.client:
            return True, "Reviewer Offline (Skipped)"

        path = Path(file_path)
        if not path.exists():
            return False, "File not found."

        code_content = path.read_text(encoding="utf-8")
        
        prompt = f"""
        You are a Senior Code Reviewer.
        Review the following Python code for:
        1. Logical Bugs
        2. Security Vulnerabilities
        3. Code Style (PEP8)
        4. Hardcoding or Fake Data

        Code Content:
        ```python
        {code_content}
        ```

        Output JSON ONLY:
        {{
            "passed": true/false,
            "score": 0-100,
            "feedback": "Concise feedback"
        }}
        """

        try:
            # Using the latest 2.0 stable model
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            result = json.loads(response.text)
            
            passed = result.get("passed", False)
            if result.get("score", 0) < 80:
                passed = False
                
            return passed, f"[Score: {result.get('score')}] {result.get('feedback')}"

        except Exception as e:
            return False, f"Review Error: {e}"

if __name__ == "__main__":
    rev = CodeReviewer()
    ok, msg = rev.review_code(__file__)
    print(f"Review Result: {ok}\n{msg}")