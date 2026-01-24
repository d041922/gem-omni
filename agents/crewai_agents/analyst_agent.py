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


def create_analyst_agent() -> Agent:
    """
    Creates a Portfolio Analyst Agent

    This agent is responsible for:
    - Calculating portfolio metrics (returns, profit/loss)
    - Analyzing asset allocation
    - Evaluating portfolio performance
    - Identifying top performers and underperformers
    """
    # Create Gemini LLM for portfolio analysis (flash model for analytical tasks)
    llm = LLM(
        model="gemini/gemini-3-flash-preview",
        temperature=0.1
    )

    return Agent(
        role="Portfolio Analysis Specialist",
        goal="Calculate accurate portfolio metrics and provide insightful performance analysis",
        backstory="""You are a Chartered Financial Analyst (CFA) with 15 years of experience in
portfolio management and performance attribution. You have worked at BlackRock and Vanguard
managing multi-billion dollar portfolios. Your expertise includes portfolio performance calculation,
asset allocation analysis, risk-adjusted returns, and currency conversion.
You are known for precision in calculations and ability to extract meaningful insights.""",
        tools=[
            PortfolioMetricsCalculatorTool()
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )


# Create singleton instance
analyst_agent = create_analyst_agent()
