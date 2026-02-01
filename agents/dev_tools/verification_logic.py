"""
Verification Logic v3.3: Cynical Auditor
[SOP v3.1] Scans output for hidden failure keywords even if exit code is 0.
"""
import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Tuple, Dict, Any

class OMNIVerifier:
    def __init__(self):
        # API Key loading logic remains...
        from agents.dev_tools.key_loader import load_google_api_key
        self.api_key = load_google_api_key()
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except:
            self.client = None

    def run_script(self, script_path: str) -> Tuple[bool, str]:
        """
        Executes script and scans for 'Hidden Failures'.
        """
        if not os.path.exists(script_path):
            return False, "ERROR: Result file not found."
        
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True, text=True, check=False, timeout=60
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            full_log = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"

            # [Strict Keyword Scan]
            fail_keywords = ["error", "abort", "fail", "exception", "not found", "missing"]
            
            # 1. Check Exit Code
            if result.returncode != 0:
                return False, f"RUNTIME ERROR (Exit {result.returncode}):\n{full_log}"
            
            # 2. Check Hidden Keywords in Output (The 'Fake Success' Trap)
            if any(kw in full_log.lower() for kw in fail_keywords):
                return False, f"HIDDEN FAILURE DETECTED (Keywords matched):\n{full_log}"

            # 3. Check for Empty/Generic Output
            if len(stdout) < 10:
                return False, f"SKEPTICAL: Output too short. Is it a placeholder?\n{full_log}"

            return True, f"VERIFIED SUCCESS:\n{stdout}"

        except subprocess.TimeoutExpired:
            return False, "TIMEOUT: Script took too long."
        except Exception as e:
            return False, f"SYSTEM ERROR: {str(e)}"

    def check_syntax(self, file_path: str) -> Tuple[bool, str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            compile(source, file_path, 'exec')
            return True, "Syntax OK"
        except Exception as e:
            return False, str(e)

    def verify_intent(self, code_path: str, spec_path: str) -> Dict[str, Any]:
        # Implementation remains (same as v3.1)
        pass