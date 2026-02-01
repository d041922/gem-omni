"""
Validation Tool [Safe Edition]
Validates agent outputs and data structures.
"""
from typing import Dict

def validate_response(res: Dict) -> bool:
    if not res:
        return False
    # Safe check
    return res.get("status") == "success"