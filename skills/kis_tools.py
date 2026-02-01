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