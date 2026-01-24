"""
Portfolio Calculation Tools for CrewAI
Wraps existing finance_core_lib functionality into CrewAI Tools
"""
from crewai_tools import BaseTool
from typing import Type, Any, Dict, List
from pydantic import BaseModel, Field
import pandas as pd
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from skills.finance_core_lib import calculate_portfolio_metrics


class PortfolioMetricsInput(BaseModel):
    """Input schema for Portfolio Metrics Calculator Tool"""
    portfolio_data: List[Dict[str, Any]] = Field(..., description="Portfolio data as list of dictionaries")
    current_prices: Dict[str, float] = Field(default_factory=dict, description="Current prices dictionary (ticker: price)")
    usd_krw_rate: float = Field(default=1300.0, description="USD to KRW exchange rate")


class PortfolioMetricsCalculatorTool(BaseTool):
    name: str = "Calculate Portfolio Metrics"
    description: str = (
        "Calculates portfolio metrics including evaluation amount, profit/loss, and return rate. "
        "Takes portfolio data, current prices, and USD/KRW exchange rate as input. "
        "Returns calculated metrics for each position including 매수금액, 평가금액, 손익, 수익률. "
        "Use this tool to analyze portfolio performance."
    )
    args_schema: Type[BaseModel] = PortfolioMetricsInput

    def _run(
        self,
        portfolio_data: List[Dict[str, Any]],
        current_prices: Dict[str, float] = None,
        usd_krw_rate: float = 1300.0
    ) -> Dict[str, Any]:
        """
        Calculate portfolio metrics

        Args:
            portfolio_data: Portfolio data as list of dictionaries
            current_prices: Dictionary of current prices (ticker: price)
            usd_krw_rate: USD to KRW exchange rate

        Returns:
            Dictionary containing calculated portfolio metrics
        """
        try:
            if current_prices is None:
                current_prices = {}

            # Convert list of dicts to DataFrame
            df = pd.DataFrame(portfolio_data)

            if df.empty:
                return {
                    "success": True,
                    "portfolio_metrics": [],
                    "total_cost": 0.0,
                    "total_eval": 0.0,
                    "total_profit": 0.0,
                    "total_return_pct": 0.0,
                    "message": "Portfolio is empty"
                }

            # Calculate metrics
            result_df = calculate_portfolio_metrics(df, current_prices, usd_krw_rate)

            # Calculate totals
            total_cost = result_df['매수금액(KRW)'].sum()
            total_eval = result_df['평가금액(KRW)'].sum()
            total_profit = result_df['손익(KRW)'].sum()
            total_return_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0.0

            return {
                "success": True,
                "portfolio_metrics": result_df.to_dict(orient='records'),
                "columns": result_df.columns.tolist(),
                "total_cost": float(total_cost),
                "total_eval": float(total_eval),
                "total_profit": float(total_profit),
                "total_return_pct": float(total_return_pct),
                "message": "Successfully calculated portfolio metrics"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to calculate portfolio metrics: {str(e)}"
            }
