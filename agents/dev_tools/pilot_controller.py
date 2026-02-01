"""
Pilot Controller v4.0: Reasoning First
[SOP v3.0] Enforces Chain-of-Thought (CoT) before coding.
"""
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

current_file = Path(__file__).resolve()
root_dir = current_file.parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.dev_tools.key_loader import load_google_api_key
from agents.dev_tools.verification_logic import OMNIVerifier

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class DevPilot:
    def __init__(self):
        self.root_dir = root_dir
        self.verifier = OMNIVerifier()
        self.api_key = load_google_api_key()
        if HAS_GENAI and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def _generate_code(self, task: str, context: str, error_log: str = None, feedback: str = None) -> Tuple[str, str]:
        """
        Returns: (Reasoning (str), Code (str))
        """
        if not self.client:
            return "No AI", "# AI Offline"

        system_instruction = (
            "You are an Expert Python Developer. "
            "STRICT RULE 1: You must explain your logic in Korean FIRST, then write the code. "
            "STRICT RULE 2: Never use plain 'pip'. Always use 'sys.executable + \" -m pip\"'. "
            "STRICT RULE 3: If the plan requires sidecar files (like model.conf, policy.csv, .env), "
            "your code MUST contain logic to CREATE these files automatically if they are missing."
        )
        
        prompt = f"Mission: {task}\n\nContext:\n{context}"
        if feedback:
            prompt += f"\n\n[CRITICAL FEEDBACK]\n{feedback}\n\nFix the issues mentioned above."

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            text = response.text
            
            # Split reasoning and code
            reasoning = "설명 없음"
            code = text
            if "```python" in text:
                parts = text.split("```python")
                reasoning = parts[0].strip()
                code = parts[1].split("```")[0].strip()
            
            return reasoning, code
        except Exception as e:
            return str(e), f"# Failed: {e}"

    def execute_plan(self, track_id: str, feedback: str = None) -> str:
        """Returns the reasoning for logging."""
        track_dir = self.root_dir / "conductor" / "tracks" / track_id
        plan_path = track_dir / "plan.md"
        spec_path = track_dir / "spec.md"
        
        plan_content = plan_path.read_text(encoding="utf-8")
        spec_content = spec_path.read_text(encoding="utf-8")
        
        target_file_match = re.search(r"([a-zA-Z0-9_/]+\.py)", spec_content + plan_content)
        target_path = Path(target_file_match.group(1)) if target_file_match else track_dir / "result_script.py"
        if not target_path.is_absolute(): target_path = self.root_dir / target_path

        print(f"🔨 [Pilot] 구현/수정 중: {target_path.name}")
        
        context = f"Spec: {spec_content}\nPlan: {plan_content}"
        reasoning, code = self._generate_code(f"Implement {target_path.name}", context, feedback=feedback)
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(code, encoding="utf-8")
        
        # Internal self-correction loop
        for attempt in range(2):
            run_ok, run_msg = self.verifier.run_script(str(target_path))
            if run_ok: break
            _, code = self._generate_code("Fix Error", context, error_log=run_msg)
            target_path.write_text(code, encoding="utf-8")
            
        return reasoning