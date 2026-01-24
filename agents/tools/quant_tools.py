"""
Quantitative Risk Analysis Tools for CrewAI
Wraps existing quant_engine functionality into CrewAI Tools
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict, List
from pydantic import BaseModel, Field
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from skills.quant_engine import fetch_historical_prices, calculate_correlation, calculate_portfolio_beta


class QuantRiskInput(BaseModel):
    """Input schema for Quant Risk Analysis Tool"""
    tickers: List[str] = Field(..., description="List of stock tickers to analyze")
    weights: Dict[str, float] = Field(default_factory=dict, description="Portfolio weights (ticker: weight)")


class QuantRiskAnalysisTool(BaseTool):
    name: str = "Analyze Portfolio Risk"
    description: str = (
        "Performs quantitative risk analysis on a portfolio including correlation matrix and beta calculation. "
        "Takes list of tickers and portfolio weights as input. "
        "Returns correlation matrix and portfolio beta (market sensitivity). "
        "Use this tool to assess portfolio risk and diversification."
    )
    args_schema: Type[BaseModel] = QuantRiskInput

    def _run(
        self,
        tickers: List[str],
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Analyze portfolio risk

        Args:
            tickers: List of stock tickers
            weights: Portfolio weights dictionary

        Returns:
            Dictionary containing correlation matrix and portfolio beta
        """
        try:
            if weights is None:
                weights = {}

            if not tickers:
                return {
                    "success": False,
                    "message": "No tickers provided"
                }

            # Fetch historical prices
            price_df = fetch_historical_prices(tickers)

            if price_df.empty:
                return {
                    "success": False,
                    "message": "Failed to fetch historical prices"
                }

            # Calculate correlation matrix
            corr_matrix = calculate_correlation(price_df)

            # Calculate portfolio beta
            portfolio_beta = 0.0
            if weights:
                portfolio_beta = calculate_portfolio_beta(price_df, weights)

            return {
                "success": True,
                "correlation_matrix": corr_matrix.to_dict() if not corr_matrix.empty else {},
                "portfolio_beta": float(portfolio_beta),
                "tickers_analyzed": list(price_df.columns),
                "message": "Successfully analyzed portfolio risk"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to analyze portfolio risk: {str(e)}"
            }
