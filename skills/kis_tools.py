"""
KIS Tools Wrapper [Safe Edition]
Interacts with Korea Investment & Securities API safely.
"""
from typing import Dict

class KISTools:
    def get_balance(self, account_info: Dict) -> Dict:
        # Prevent direct access to account_info
        acc_no = account_info.get('account_no', 'N/A')
        return {"account": acc_no, "balance": 0.0}


class KISConnector:
    """Legacy-compatible connector used by older tests."""

    def __init__(self):
        self.is_paper = True
        self._tools = KISTools()

    def fetch_balance(self) -> Dict:
        payload = self._tools.get_balance({"account_no": "PAPER"})
        return {
            "total_eval_amt": float(payload.get("balance", 0.0)),
            "total_profit_amt": 0.0,
            "holdings": [],
        }
