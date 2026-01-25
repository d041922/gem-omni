"""
Data Synchronization Agent for CrewAI
Responsible for loading and synchronizing portfolio data from multiple sources
"""
from crewai import Agent
from core.models import flash_llm as gemini_llm
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.tools.gsheet_tools import GSheetLoaderTool
from agents.tools.kis_tools_wrapper import KISAccountTool
from pathlib import Path


def create_data_sync_agent() -> Agent:
    """
    Creates a Data Synchronization Agent

    This agent is responsible for:
    - Loading portfolio data from Google Sheets
    - Fetching real-time account data from KIS API
    - Ensuring data consistency and accuracy
    - Combining data from multiple sources
    """
    # Load system prompt from .claude/agents/ (for prompt caching)
    agent_prompt_file = Path(__file__).parent.parent.parent / ".claude" / "agents" / "data-sync-agent.md"
    if agent_prompt_file.exists():
        with open(agent_prompt_file, 'r', encoding='utf-8') as f:
            backstory = f.read()
    else:
        # Fallback to default
        backstory = """You are a veteran data engineer with 15 years of experience in financial data integration.
You have worked with major investment banks ensuring data accuracy across multiple systems.
Your expertise includes Google Sheets API, brokerage API integration, data validation,
and real-time synchronization. You are meticulous and never compromise on data quality."""

    return Agent(
        role="Data Synchronization Specialist",
        goal="Accurately load and synchronize portfolio data from Google Sheets and KIS API",
        backstory=backstory,
        tools=[
            GSheetLoaderTool(),
            KISAccountTool()
        ],
        llm=gemini_llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )


# Create singleton instance
data_sync_agent = create_data_sync_agent()
