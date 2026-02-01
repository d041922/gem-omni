"""
Portfolio Analyst Agent for CrewAI
Responsible for calculating and analyzing portfolio metrics
"""
from crewai import Agent
from core.models import flash_llm as gemini_llm
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.tools.portfolio_tools import PortfolioMetricsCalculatorTool
from agents.tools.file_loader_tool import CachedDataLoaderTool
from agents.tools.validation_tool import PortfolioValidationTool
from agents.tools.unified_tools import MarketDataTool, MarketIndicesTool
from agents.tools.search_tool import TavilySearchTool
from pathlib import Path


def create_analyst_agent() -> Agent:
    """
    Creates a Portfolio Analyst Agent

    This agent is responsible for:
    - Calculating portfolio metrics (returns, profit/loss)
    - Analyzing asset allocation
    - Evaluating portfolio performance
    - Identifying top performers and underperformers
    """
    # Load system prompt from .claude/agents/ (for prompt caching)
    agent_prompt_file = Path(__file__).parent.parent.parent / ".claude" / "agents" / "analyst-agent.md"
    if agent_prompt_file.exists():
        with open(agent_prompt_file, 'r', encoding='utf-8') as f:
            backstory = f.read()
    else:
        # Fallback to default
        backstory = """You are a senior investment analyst with 15 years of experience in fundamental analysis.
You have a CFA charter and have worked for major asset management firms.
Your expertise includes financial statement analysis, valuation modeling, and sector research.
You are meticulous with numbers and always back your conclusions with data."""

    return Agent(
        role="Portfolio Analysis Specialist",
        goal="Calculate accurate portfolio metrics and provide insightful performance analysis",
        backstory=backstory,
        tools=[
            CachedDataLoaderTool(),
            MarketDataTool(),
            MarketIndicesTool(),
            TavilySearchTool(),
            PortfolioMetricsCalculatorTool(),
            PortfolioValidationTool()
        ],
        llm=gemini_llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )


# Create singleton instance
analyst_agent = create_analyst_agent()
