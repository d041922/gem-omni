"""
Google Sheets Tools for CrewAI
Wraps existing gsheet_loader functionality into CrewAI Tools
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict
from pydantic import BaseModel, Field
import pandas as pd
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from skills.gsheet_loader import load_data_from_gsheet


class GSheetLoaderInput(BaseModel):
    """Input schema for GSheet Loader Tool"""
    spreadsheet_name: str = Field(..., description="The name of the Google Sheets spreadsheet to load")


class GSheetLoaderTool(BaseTool):
    name: str = "Load Google Sheets Data"
    description: str = (
        "Loads portfolio, watchlist, and cash data from a Google Sheets spreadsheet. "
        "Returns three dataframes: portfolio_df, watchlist_df, and cash_df. "
        "Use this tool to synchronize data from Google Sheets."
    )
    args_schema: Type[BaseModel] = GSheetLoaderInput

    def _run(self, spreadsheet_name: str) -> Dict[str, Any]:
        """
        Load data from Google Sheets

        Args:
            spreadsheet_name: Name of the Google Sheets spreadsheet

        Returns:
            Dictionary containing portfolio, watchlist, and cash dataframes
        """
        try:
            portfolio_df, watchlist_df, cash_df = load_data_from_gsheet(spreadsheet_name)

            # Convert dataframes to dict format for JSON serialization
            return {
                "success": True,
                "portfolio": portfolio_df.to_dict(orient='records') if not portfolio_df.empty else [],
                "portfolio_columns": portfolio_df.columns.tolist() if not portfolio_df.empty else [],
                "watchlist": watchlist_df.to_dict(orient='records') if not watchlist_df.empty else [],
                "cash": cash_df.to_dict(orient='records') if not cash_df.empty else [],
                "message": f"Successfully loaded data from {spreadsheet_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to load data from {spreadsheet_name}: {str(e)}"
            }
