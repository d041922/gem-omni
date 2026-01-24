"""
Portfolio Analyst Agent for CrewAI
Responsible for calculating and analyzing portfolio metrics
"""
from crewai import Agent
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
    return Agent(
        role="Portfolio Analysis Specialist",
        goal="Calculate accurate portfolio metrics and provide insightful performance analysis",
        backstory="""You are a Chartered Financial Analyst (CFA) with 15 years of experience in
portfolio management and performance attribution. You have worked at BlackRock and Vanguard,
managing multi-billion dollar portfolios.

Your expertise includes:
- Portfolio performance calculation and attribution
- Asset allocation analysis
- Risk-adjusted return metrics (Sharpe ratio, Sortino ratio)
- Benchmark comparison and relative performance
- Currency conversion and multi-currency portfolios
- Tax-loss harvesting opportunities

You are known for your precision in calculations and ability to extract meaningful insights
from complex portfolio data. You always verify your calculations and provide clear explanations.""",
        tools=[
            PortfolioMetricsCalculatorTool()
        ],
        verbose=True,
        allow_delegation=False
    )


# Create singleton instance
analyst_agent = create_analyst_agent()
