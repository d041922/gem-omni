"""
KIS (Korea Investment & Securities) API Tools for CrewAI
Wraps existing kis_tools functionality into CrewAI Tools
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict
from pydantic import BaseModel
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from skills.kis_tools import KISConnector


class KISAccountInput(BaseModel):
    """Input schema for KIS Account Tool"""
    pass  # No input needed, uses environment variables


class KISAccountTool(BaseTool):
    name: str = "Fetch KIS Account Balance"
    description: str = (
        "Fetches real-time account balance and holdings from Korea Investment & Securities (KIS) API. "
        "Returns holdings list with ticker, name, amount, avg_price, current_price, profit_pct, "
        "and summary with total_eval_amt and total_profit_amt. "
        "Use this tool to synchronize data from KIS brokerage account."
    )
    args_schema: Type[BaseModel] = KISAccountInput

    def _run(self) -> Dict[str, Any]:
        """
        Fetch account balance from KIS API

        Returns:
            Dictionary containing holdings and account summary
        """
        try:
            connector = KISConnector()
            balance_data = connector.fetch_balance()

            return {
                "success": True,
                "holdings": balance_data.get("holdings", []),
                "total_eval_amt": balance_data.get("total_eval_amt", 0),
                "total_profit_amt": balance_data.get("total_profit_amt", 0),
                "message": "Successfully fetched KIS account balance"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to fetch KIS account balance: {str(e)}"
            }
