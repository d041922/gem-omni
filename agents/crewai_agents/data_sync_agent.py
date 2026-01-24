"""
Data Synchronization Agent for CrewAI
Responsible for loading and synchronizing portfolio data from multiple sources
"""
from crewai import Agent
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.tools.gsheet_tools import GSheetLoaderTool
from agents.tools.kis_tools_wrapper import KISAccountTool


def create_data_sync_agent() -> Agent:
    """
    Creates a Data Synchronization Agent

    This agent is responsible for:
    - Loading portfolio data from Google Sheets
    - Fetching real-time account data from KIS API
    - Ensuring data consistency and accuracy
    - Combining data from multiple sources
    """
    return Agent(
        role="Data Synchronization Specialist",
        goal="Accurately load and synchronize portfolio data from Google Sheets and KIS API",
        backstory="""You are a veteran data engineer with 20 years of experience in financial data integration.
You have worked with major investment banks and hedge funds, ensuring data accuracy and consistency
across multiple systems. You understand the critical importance of data quality in investment decisions.

Your expertise includes:
- Google Sheets API integration
- Brokerage API integration (KIS, Interactive Brokers, etc.)
- Data validation and error handling
- Real-time data synchronization
- Financial data normalization

You are meticulous, detail-oriented, and never compromise on data accuracy.""",
        tools=[
            GSheetLoaderTool(),
            KISAccountTool()
        ],
        verbose=True,
        allow_delegation=False
    )


# Create singleton instance
data_sync_agent = create_data_sync_agent()
