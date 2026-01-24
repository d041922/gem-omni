"""
Finance Crew for GEM: OMNI
Orchestrates four specialized agents to perform comprehensive portfolio analysis
"""
from crewai import Crew, Task, Process
import sys
import os
from typing import Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.crewai_agents.data_sync_agent import data_sync_agent
from agents.crewai_agents.analyst_agent import analyst_agent
from agents.crewai_agents.risk_agent import risk_agent
from agents.crewai_agents.strategy_agent import strategy_agent


class FinanceCrew:
    """
    FinanceCrew: Comprehensive Portfolio Analysis Crew

    This crew orchestrates four specialized agents to perform:
    1. Data Synchronization (from Google Sheets and KIS API)
    2. Portfolio Analysis (metrics calculation and performance)
    3. Risk Assessment (quantitative risk analysis)
    4. Strategy Generation (AI-powered investment recommendations)
    """

    def __init__(self, memory_system=None, spreadsheet_name: str = "GEM_Finance_Portfolio"):
        """
        Initialize FinanceCrew

        Args:
            memory_system: Optional memory system for context persistence
            spreadsheet_name: Name of Google Sheets spreadsheet to load
        """
        self.memory = memory_system
        self.spreadsheet_name = spreadsheet_name

        # Define Tasks
        self.sync_task = Task(
            description=f"""Load and synchronize portfolio data from multiple sources:
1. Load portfolio data from Google Sheets spreadsheet named '{spreadsheet_name}'
2. Fetch real-time account data from KIS API
3. Combine and validate data from both sources
4. Ensure data consistency and handle any discrepancies

Return a structured summary of the loaded data including:
- Number of positions loaded
- Total portfolio value
- Data source details
- Any warnings or issues encountered""",
            agent=data_sync_agent,
            expected_output="Structured portfolio data summary with holdings, watchlist, and cash positions"
        )

        self.analysis_task = Task(
            description="""Analyze the synchronized portfolio data:
1. Calculate key portfolio metrics for each position:
   - Purchase cost (매수금액)
   - Current evaluation (평가금액)
   - Profit/Loss (손익)
   - Return percentage (수익률)
2. Calculate total portfolio metrics
3. Identify top performers and underperformers
4. Analyze asset allocation
5. Calculate USD/KRW currency exposure

Provide a comprehensive analysis report with:
- Summary statistics
- Position-level details
- Performance insights""",
            agent=analyst_agent,
            expected_output="Comprehensive portfolio metrics report with calculated returns and analysis",
            context=[self.sync_task]  # Uses data from sync_task
        )

        self.risk_task = Task(
            description="""Perform quantitative risk assessment on the portfolio:
1. Calculate portfolio beta (market sensitivity)
2. Analyze correlation matrix between holdings
3. Assess diversification quality
4. Identify concentration risks
5. Evaluate systematic vs unsystematic risk

Provide a risk assessment report including:
- Portfolio beta value
- Key correlation insights
- Diversification score
- Risk warnings and concerns
- Risk mitigation recommendations""",
            agent=risk_agent,
            expected_output="Quantitative risk assessment report with beta, correlations, and risk metrics",
            context=[self.analysis_task]  # Uses analysis results
        )

        self.strategy_task = Task(
            description="""Generate comprehensive investment strategy recommendations:
1. Synthesize insights from portfolio analysis and risk assessment
2. Generate AI-powered strategy report using Gemini
3. Provide actionable recommendations
4. Identify specific opportunities and threats
5. Create prioritized action plan

The strategy report should include:
- Portfolio Health Assessment
- Risk Assessment Summary
- Strategic Recommendations (specific actions)
- Potential Concerns (what to watch)
- Action Items (prioritized list)

Use clear, non-technical language that investors can understand and act upon.""",
            agent=strategy_agent,
            expected_output="Comprehensive AI-powered investment strategy report with actionable recommendations in JSON format",
            context=[self.analysis_task, self.risk_task]  # Uses both analysis and risk results
        )

        # Create Crew
        self.crew = Crew(
            agents=[data_sync_agent, analyst_agent, risk_agent, strategy_agent],
            tasks=[self.sync_task, self.analysis_task, self.risk_task, self.strategy_task],
            verbose=True,
            process=Process.sequential,  # Execute tasks in order
            memory=False  # Disable built-in memory (we use custom memory system)
        )

    def generate_full_report(self) -> Dict[str, Any]:
        """
        Execute the full portfolio analysis workflow

        Returns:
            Dictionary containing results from all four tasks
        """
        try:
            # Execute crew workflow
            result = self.crew.kickoff()

            # Parse result
            # CrewAI returns the output of the last task by default
            return {
                "success": True,
                "strategy_report": str(result),
                "message": "Successfully completed full portfolio analysis"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to complete portfolio analysis: {str(e)}"
            }

    def sync_data_only(self) -> Dict[str, Any]:
        """
        Execute only data synchronization task

        Returns:
            Dictionary containing sync results
        """
        try:
            # Execute only sync task
            result = self.sync_task.execute_sync()
            return {
                "success": True,
                "sync_result": result,
                "message": "Successfully synchronized data"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to sync data: {str(e)}"
            }
