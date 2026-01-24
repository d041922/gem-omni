"""
Template Tool for New Domain
Replace {DOMAIN} with your domain name (e.g., Health, Relationships)
Replace {ACTION} with what this tool does (e.g., Fetch, Calculate, Track)
"""
from crewai_tools import BaseTool
from typing import Type, Any, Dict
from pydantic import BaseModel, Field
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import any existing skills or libraries you need
# from skills.{domain}_skills import some_function


class {Action}{Domain}ToolInput(BaseModel):
    """Input schema for {Action}{Domain}Tool"""
    param1: str = Field(..., description="Description of this parameter")
    param2: int = Field(default=0, description="Optional parameter with default")


class {Action}{Domain}Tool(BaseTool):
    name: str = "{Action} {Domain} {Object}"  # e.g., "Fetch Health Metrics"
    description: str = (
        "Detailed description of what this tool does. "
        "Explain when to use it and what it returns. "
        "Be specific so agents know when to use this tool. "
        "Example: Fetches daily health metrics from Fitbit API including steps, heart rate, and sleep data."
    )
    args_schema: Type[BaseModel] = {Action}{Domain}ToolInput

    def _run(self, param1: str, param2: int = 0) -> Dict[str, Any]:
        """
        Brief description of what this method does

        Args:
            param1: Description of param1
            param2: Description of param2

        Returns:
            Dictionary containing success status, data, and message
        """
        try:
            # Your implementation here
            # Example:
            # data = some_function(param1, param2)

            return {
                "success": True,
                "data": {},  # Your actual data here
                "message": f"Successfully completed action with {param1}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to complete action: {str(e)}"
            }
