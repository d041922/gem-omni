"""
Google Sheets Tools for CrewAI
Wraps existing gsheet_loader functionality into CrewAI Tools
Optimized to reduce token usage by returning summaries instead of full data
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict
from pydantic import BaseModel, Field
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from skills.gsheet_loader import load_data_from_gsheet
from agents.tools.data_cache import save_portfolio_data


class GSheetLoaderInput(BaseModel):
    """Input schema for GSheet Loader Tool"""
    spreadsheet_name: str = Field(..., description="The name of the Google Sheets spreadsheet to load")


class GSheetLoaderTool(BaseTool):
    name: str = "Load Google Sheets Data"
    description: str = (
        "Loads portfolio, watchlist, and cash data from a Google Sheets spreadsheet. "
        "Returns compact summaries with key metrics and file paths where full data is cached. "
        "This tool is optimized to minimize token usage. "
        "Full data can be accessed via the returned file paths when needed."
    )
    args_schema: Type[BaseModel] = GSheetLoaderInput

    def _run(self, spreadsheet_name: str) -> Dict[str, Any]:
        """
        Load data from Google Sheets (Token-Optimized)

        Args:
            spreadsheet_name: Name of the Google Sheets spreadsheet

        Returns:
            Dictionary containing file paths and summaries (not full data)
        """
        try:
            portfolio_df, watchlist_df, cash_df = load_data_from_gsheet(spreadsheet_name)

            # Save full data to cache files and return summaries only
            portfolio_cache = save_portfolio_data(
                portfolio_df,
                "portfolio_raw.json",
                metadata={"source": spreadsheet_name, "type": "portfolio"}
            )

            watchlist_cache = save_portfolio_data(
                watchlist_df,
                "watchlist.json",
                metadata={"source": spreadsheet_name, "type": "watchlist"}
            )

            # Cash data is usually small, can include directly
            cash_dict = cash_df.to_dict(orient='records') if not cash_df.empty else []

            return {
                "success": True,
                "portfolio_file": portfolio_cache.get("file_path"),
                "portfolio_summary": portfolio_cache.get("summary", {}),
                "watchlist_file": watchlist_cache.get("file_path"),
                "watchlist_summary": watchlist_cache.get("summary", {}),
                "cash": cash_dict,
                "message": (
                    f"Successfully loaded {portfolio_cache['summary'].get('total_positions', 0)} portfolio positions "
                    f"and {watchlist_cache['summary'].get('total_positions', 0)} watchlist items. "
                    f"Full data cached at: {portfolio_cache.get('file_path')}"
                )
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to load data from {spreadsheet_name}: {str(e)}"
            }
