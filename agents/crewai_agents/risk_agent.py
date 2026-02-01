"""
Risk Assessment Agent for CrewAI
Responsible for quantitative risk analysis and portfolio diversification assessment
"""
from crewai import Agent
from core.models import pro_llm as gemini_llm
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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
        backstory = """You are a PhD in Financial Engineering with 12 years of experience in risk management.
You specialize in quantitative risk assessment, tail risk hedging, and portfolio optimization.
Your approach is data-driven and focused on protecting capital during market stress.
You have extensive experience with VaR, stress testing, and correlation analysis."""

    return Agent(
        role="Quantitative Risk Analyst",
        goal="Assess portfolio risk comprehensively using quantitative methods and identify potential risks",
        backstory=backstory,
        tools=[
            # Risk Tools
        ],
        llm=gemini_llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )


# Create singleton instance
risk_agent = create_risk_agent()
