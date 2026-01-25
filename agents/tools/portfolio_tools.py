"""
Portfolio Calculation Tools for CrewAI
Wraps existing finance_core_lib functionality into CrewAI Tools
Optimized to reduce token usage by caching results
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict, List
from pydantic import BaseModel, Field
import pandas as pd
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from skills.finance_core_lib import calculate_portfolio_metrics
from agents.tools.data_cache import save_portfolio_data, save_analysis_result


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
        "Returns compact summary with key totals and file path to detailed metrics. "
        "This tool is optimized to minimize token usage. "
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
        Calculate portfolio metrics (Token-Optimized)

        Args:
            portfolio_data: Portfolio data as list of dictionaries
            current_prices: Dictionary of current prices (ticker: price)
            usd_krw_rate: USD to KRW exchange rate

        Returns:
            Dictionary containing summary metrics and file path to detailed results
        """
        try:
            if current_prices is None:
                current_prices = {}

            # Convert list of dicts to DataFrame
            df = pd.DataFrame(portfolio_data)

            if df.empty:
                return {
                    "success": True,
                    "summary": {
                        "total_cost": 0.0,
                        "total_eval": 0.0,
                        "total_profit": 0.0,
                        "total_return_pct": 0.0
                    },
                    "message": "Portfolio is empty"
                }

            # Calculate metrics
            result_df = calculate_portfolio_metrics(df, current_prices, usd_krw_rate)

            # Calculate totals
            total_cost = result_df['매수금액(KRW)'].sum()
            total_eval = result_df['평가금액(KRW)'].sum()
            total_profit = result_df['손익(KRW)'].sum()
            total_return_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0.0

            # Save full metrics to cache
            metrics_cache = save_portfolio_data(
                result_df,
                "portfolio_calculated.json",
                metadata={"usd_krw_rate": usd_krw_rate, "type": "calculated_metrics"}
            )

            # Prepare compact summary
            summary = {
                "total_positions": len(result_df),
                "total_cost_krw": float(total_cost),
                "total_eval_krw": float(total_eval),
                "total_profit_krw": float(total_profit),
                "total_return_pct": float(total_return_pct),
                "usd_krw_rate": usd_krw_rate
            }

            # Add top/bottom performers if available
            if 'top_3_performers' in metrics_cache.get('summary', {}):
                summary['top_3_performers'] = metrics_cache['summary']['top_3_performers']
            if 'bottom_3_performers' in metrics_cache.get('summary', {}):
                summary['bottom_3_performers'] = metrics_cache['summary']['bottom_3_performers']

            return {
                "success": True,
                "metrics_file": metrics_cache.get("file_path"),
                "summary": summary,
                "message": (
                    f"Calculated metrics for {len(result_df)} positions. "
                    f"Total return: {total_return_pct:.2f}%. "
                    f"Full metrics cached at: {metrics_cache.get('file_path')}"
                )
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to calculate portfolio metrics: {str(e)}"
            }
