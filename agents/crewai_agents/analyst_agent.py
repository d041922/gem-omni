"""
Portfolio Analyst Agent for CrewAI
Responsible for calculating and analyzing portfolio metrics
"""
from crewai import Agent, LLM
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.tools.portfolio_tools import PortfolioMetricsCalculatorTool
from agents.tools.file_loader_tool import CachedDataLoaderTool
from agents.tools.validation_tool import PortfolioValidationTool
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
        backstory = """You are a Chartered Financial Analyst (CFA) with 15 years of experience in
portfolio management and performance attribution. You have worked at BlackRock and Vanguard
managing multi-billion dollar portfolios. Your expertise includes portfolio performance calculation,
asset allocation analysis, risk-adjusted returns, and currency conversion.
You are known for precision in calculations and ability to extract meaningful insights."""

    # Create Gemini LLM for analysis
    llm = LLM(
        model="gemini/gemini-3-flash-preview",
        temperature=0.2
    )

    return Agent(
        role="Portfolio Analysis Specialist",
        goal="Calculate accurate portfolio metrics and provide insightful performance analysis",
        backstory=backstory,
        tools=[
            PortfolioMetricsCalculatorTool(),
            CachedDataLoaderTool(),
            PortfolioValidationTool()
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )


# Create singleton instance
analyst_agent = create_analyst_agent()
