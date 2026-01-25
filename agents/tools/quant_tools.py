"""
Quantitative Risk Analysis Tools for CrewAI
Wraps existing quant_engine functionality into CrewAI Tools
Optimized to reduce token usage by returning key insights instead of full matrices
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict, List
from pydantic import BaseModel, Field
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from skills.quant_engine import fetch_historical_prices, calculate_correlation, calculate_portfolio_beta
from agents.tools.data_cache import save_analysis_result


class QuantRiskInput(BaseModel):
    """Input schema for Quant Risk Analysis Tool"""
    tickers: List[str] = Field(..., description="List of stock tickers to analyze")
    weights: Dict[str, float] = Field(default_factory=dict, description="Portfolio weights (ticker: weight)")


class QuantRiskAnalysisTool(BaseTool):
    name: str = "Analyze Portfolio Risk"
    description: str = (
        "Performs quantitative risk analysis on a portfolio including correlation matrix and beta calculation. "
        "Takes list of tickers and portfolio weights as input. "
        "Returns key insights (highly correlated pairs, portfolio beta) and file path to full correlation matrix. "
        "This tool is optimized to minimize token usage. "
        "Use this tool to assess portfolio risk and diversification."
    )
    args_schema: Type[BaseModel] = QuantRiskInput

    def _run(
        self,
        tickers: List[str],
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Analyze portfolio risk (Token-Optimized)

        Args:
            tickers: List of stock tickers
            weights: Portfolio weights dictionary

        Returns:
            Dictionary containing key risk insights and file path to detailed analysis
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

            # Extract key insights from correlation matrix
            # Find highly correlated pairs (> 0.7 or < -0.7)
            high_corr_pairs = []
            if not corr_matrix.empty:
                for i in range(len(corr_matrix.columns)):
                    for j in range(i + 1, len(corr_matrix.columns)):
                        ticker1 = corr_matrix.columns[i]
                        ticker2 = corr_matrix.columns[j]
                        corr_value = corr_matrix.iloc[i, j]

                        if abs(corr_value) > 0.7:
                            high_corr_pairs.append({
                                "ticker1": ticker1,
                                "ticker2": ticker2,
                                "correlation": float(corr_value)
                            })

            # Save full correlation matrix to cache
            risk_analysis = {
                "correlation_matrix": corr_matrix.to_dict(),
                "portfolio_beta": float(portfolio_beta),
                "tickers": tickers,
                "high_correlation_pairs": high_corr_pairs
            }

            cache_result = save_analysis_result(risk_analysis, "risk_analysis.json")

            # Return compact summary
            return {
                "success": True,
                "risk_file": cache_result.get("file_path"),
                "summary": {
                    "portfolio_beta": float(portfolio_beta),
                    "tickers_analyzed": len(tickers),
                    "high_correlation_pairs_count": len(high_corr_pairs),
                    "high_correlation_pairs": high_corr_pairs[:5]  # Top 5 only
                },
                "message": (
                    f"Analyzed risk for {len(tickers)} tickers. "
                    f"Portfolio beta: {portfolio_beta:.2f}. "
                    f"Found {len(high_corr_pairs)} highly correlated pairs. "
                    f"Full analysis cached at: {cache_result.get('file_path')}"
                )
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to analyze portfolio risk: {str(e)}"
            }
