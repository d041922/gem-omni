"""
Risk Assessment Agent for CrewAI
Responsible for quantitative risk analysis and portfolio diversification assessment
"""
from crewai import Agent, LLM
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.tools.quant_tools import QuantRiskAnalysisTool
from agents.tools.file_loader_tool import CachedDataLoaderTool
from agents.tools.validation_tool import PortfolioValidationTool
from pathlib import Path


def create_risk_agent() -> Agent:
    """
    Creates a Risk Assessment Agent

    This agent is responsible for:
    - Calculating portfolio beta (market sensitivity)
    - Analyzing correlation between assets
    - Assessing diversification quality
    - Identifying concentration risks
    - Evaluating systematic vs unsystematic risk
    """
    # Load system prompt from .claude/agents/ (for prompt caching)
    agent_prompt_file = Path(__file__).parent.parent.parent / ".claude" / "agents" / "risk-agent.md"
    if agent_prompt_file.exists():
        with open(agent_prompt_file, 'r', encoding='utf-8') as f:
            backstory = f.read()
    else:
        # Fallback to default
        backstory = """You are a PhD in Financial Engineering from MIT with 12 years of experience in
quantitative risk management. You have worked at Goldman Sachs' Strats team and JP Morgan's quant division.
Your expertise includes portfolio beta and factor models, correlation analysis, stress testing,
and Modern Portfolio Theory optimization. You always consider tail risks and worst-case scenarios.
Your motto: "Hope for the best, prepare for the worst." You provide clear risk metrics and actionable strategies."""

    # Create Gemini LLM for risk analysis
    llm = LLM(
        model="gemini/gemini-3-pro-preview",
        temperature=0.1
    )

    return Agent(
        role="Quantitative Risk Analyst",
        goal="Assess portfolio risk comprehensively using quantitative methods and identify potential risks",
        backstory=backstory,
        tools=[
            QuantRiskAnalysisTool(),
            CachedDataLoaderTool(),
            PortfolioValidationTool()
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )


# Create singleton instance
risk_agent = create_risk_agent()
