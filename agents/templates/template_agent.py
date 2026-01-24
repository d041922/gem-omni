"""
Template Agent for New Domain
Replace {DOMAIN} with your domain name (e.g., Health, Relationships, Education)
"""
from crewai import Agent
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import your tools
# from agents.tools.{domain}_tools import YourTool


def create_{domain}_agent() -> Agent:
    """
    Creates a {Domain} Agent

    This agent is responsible for:
    - Responsibility 1
    - Responsibility 2
    - Responsibility 3
    """
    return Agent(
        role="{Domain} Specialist",  # e.g., "Health Tracking Specialist"
        goal="Clearly define what this agent aims to achieve",
        backstory="""You are an experienced professional in {domain} field.
You have X years of experience working at {companies}.

Your expertise includes:
- Specific skill 1
- Specific skill 2
- Specific skill 3

You are {work style description} and always {core value}.""",
        tools=[
            # YourTool()
        ],
        verbose=True,
        allow_delegation=False
    )


# Create singleton instance
{domain}_agent = create_{domain}_agent()
