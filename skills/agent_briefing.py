"""
Agent Briefing [Safe Edition]
Generates context for AI agents without crashing.
"""
from typing import Dict

def get_agent_context(data: Dict) -> str:
    # Use .get() for all accesses
    p_summary = data.get('portfolio_summary', {})
    total = p_summary.get('total_value', 0)
    return f"Portfolio Total: {total:,.0f}"