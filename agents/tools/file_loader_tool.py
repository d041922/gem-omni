"""
File Loader Tool for CrewAI Agents
Allows agents to load cached data files without passing full data through context
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict
from pydantic import BaseModel, Field
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.tools.data_cache import load_portfolio_data, load_analysis_result


class FileLoaderInput(BaseModel):
    """Input schema for File Loader Tool"""
    file_path: str = Field(..., description="Path to the cached data file (JSON)")


class CachedDataLoaderTool(BaseTool):
    name: str = "Load Cached Data File"
    description: str = (
        "Loads cached portfolio or analysis data from a file path. "
        "Use this tool to access full data that was cached by previous tasks. "
        "Accepts file path and returns the complete dataset. "
        "Useful when you need detailed information beyond summaries."
    )
    args_schema: Type[BaseModel] = FileLoaderInput

    def _run(self, file_path: str) -> Dict[str, Any]:
        """
        Load cached data file

        Args:
            file_path: Path to cached JSON file

        Returns:
            Dictionary containing the loaded data
        """
        try:
            # Try loading as portfolio data
            try:
                df = load_portfolio_data(file_path)
                return {
                    "success": True,
                    "data": df.to_dict(orient='records'),
                    "columns": df.columns.tolist(),
                    "row_count": len(df),
                    "message": f"Successfully loaded {len(df)} records from {file_path}"
                }
            except Exception:
                # Try loading as analysis result
                result = load_analysis_result(file_path)
                return {
                    "success": True,
                    "data": result,
                    "message": f"Successfully loaded analysis result from {file_path}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to load data from {file_path}: {str(e)}"
            }
