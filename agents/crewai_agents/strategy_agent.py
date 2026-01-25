"""
AI Strategy Agent for CrewAI
Responsible for generating investment strategy recommendations using AI
"""
from crewai import Agent, LLM
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.tools.ai_strategy_tools import GeminiStrategyTool
from agents.tools.file_loader_tool import CachedDataLoaderTool
from pathlib import Path


def create_strategy_agent() -> Agent:
    """
    Creates an AI Strategy Agent

    This agent is responsible for:
    - Generating comprehensive investment strategy reports
    - Providing actionable recommendations
    - Synthesizing insights from portfolio analysis and risk assessment
    - Identifying market opportunities and threats
    - Creating prioritized action plans
    """
    # Load system prompt from .claude/agents/ (for prompt caching)
    agent_prompt_file = Path(__file__).parent.parent.parent / ".claude" / "agents" / "strategy-agent.md"
    if agent_prompt_file.exists():
        with open(agent_prompt_file, 'r', encoding='utf-8') as f:
            backstory = f.read()
    else:
        # Fallback to default
        backstory = """You are a seasoned investment strategist with 20 years of experience in wealth management.
You have served as Chief Investment Officer (CIO) at major firms managing portfolios for high-net-worth clients.
Your expertise includes strategic asset allocation, tactical rebalancing, market cycle analysis,
and behavioral finance. You combine quantitative analysis with qualitative judgment.
You are known for providing clear, actionable advice that clients can implement.
You avoid jargon and explain complex concepts simply with data-backed recommendations."""

    # Create Gemini LLM for strategy
    llm = LLM(
        model="gemini/gemini-3-pro-preview",
        temperature=0.3
    )

    return Agent(
        role="AI-Powered Investment Strategist",
        goal="Generate comprehensive, actionable investment strategies based on portfolio analysis and risk assessment",
        backstory=backstory,
        tools=[
            GeminiStrategyTool(),
            CachedDataLoaderTool()
        ],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5
    )


# Create singleton instance
strategy_agent = create_strategy_agent()
