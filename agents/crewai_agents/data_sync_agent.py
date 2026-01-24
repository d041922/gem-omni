"""
Data Synchronization Agent for CrewAI
Responsible for loading and synchronizing portfolio data from multiple sources
"""
from crewai import Agent, LLM
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
    # Create Gemini LLM for data sync (flash model for simple tasks)
    llm = LLM(
        model="gemini/gemini-3-flash-preview",
        temperature=0.1
    )

    return Agent(
        role="Data Synchronization Specialist",
        goal="Accurately load and synchronize portfolio data from Google Sheets and KIS API",
        backstory="""You are a veteran data engineer with 15 years of experience in financial data integration.
You have worked with major investment banks ensuring data accuracy across multiple systems.
Your expertise includes Google Sheets API, brokerage API integration, data validation,
and real-time synchronization. You are meticulous and never compromise on data quality.""",
        tools=[
            GSheetLoaderTool(),
            KISAccountTool()
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )


# Create singleton instance
data_sync_agent = create_data_sync_agent()
