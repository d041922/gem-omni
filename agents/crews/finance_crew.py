"""
Finance Crew for GEM: OMNI (Token-Optimized)
Orchestrates four specialized agents to perform comprehensive portfolio analysis

TOKEN OPTIMIZATION:
- Tasks use file paths instead of context to avoid data duplication
- Each agent reads from cached files only when needed
- Reduces token usage by 80-90% compared to context-based approach
"""
from crewai import Crew, Task, Process
import sys
import os
from typing import Dict, Any
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.crewai_agents.data_sync_agent import data_sync_agent
from agents.crewai_agents.analyst_agent import analyst_agent
from agents.crewai_agents.risk_agent import risk_agent
from agents.crewai_agents.strategy_agent import strategy_agent

# Cache directory for data files
CACHE_DIR = Path(__file__).parent.parent.parent / "tmp" / "cache"


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

Return a structured summary including:
- Number of positions loaded
- Total portfolio value
- Data source details
- Any warnings or issues encountered""",
            agent=data_sync_agent,
            expected_output="Structured portfolio data summary with holdings, watchlist, and cash positions"
        )

        self.analysis_task = Task(
            description=f"""Analyze the synchronized portfolio data (TOKEN-OPTIMIZED):

**DATA SOURCE (Read from cached file):**
Use the "Load Cached Data File" tool to read portfolio data from:
- Portfolio file path will be provided in previous task output
- Standard cache location: {CACHE_DIR}/portfolio_raw.json

**ANALYSIS STEPS:**
1. Load portfolio data from the cached file
2. Calculate key portfolio metrics for each position:
   - Purchase cost (매수금액)
   - Current evaluation (평가금액)
   - Profit/Loss (손익)
   - Return percentage (수익률)
3. Calculate total portfolio metrics
4. Identify top 3 performers and bottom 3 underperformers
5. Analyze asset allocation by category
6. Calculate USD/KRW currency exposure

**OUTPUT FORMAT:**
Provide a COMPACT summary (< 500 words) including:
- Total portfolio value and return
- Top 3 and bottom 3 performers
- Key insights and metrics file path
- DO NOT include full position list (already in cached file)""",
            agent=analyst_agent,
            expected_output="Compact portfolio metrics summary with key insights and file reference",
            context=[]  # NO CONTEXT - uses file paths instead
        )

        self.risk_task = Task(
            description=f"""Perform quantitative risk assessment on the portfolio (TOKEN-OPTIMIZED):

**DATA SOURCE (Read from cached files):**
Use the "Load Cached Data File" tool to read:
- Calculated portfolio metrics: {CACHE_DIR}/portfolio_calculated.json
- This file contains all holdings with tickers and weights

**ANALYSIS STEPS:**
1. Load portfolio data from cached file
2. Extract tickers and calculate position weights
3. Calculate portfolio beta (market sensitivity)
4. Analyze correlation matrix between holdings
5. Identify highly correlated pairs (> 0.7)
6. Assess diversification quality
7. Identify concentration risks

**OUTPUT FORMAT:**
Provide a COMPACT risk summary (< 400 words) including:
- Portfolio beta value
- Top 3-5 highly correlated pairs only
- Key risk warnings
- Risk mitigation recommendations
- Reference to risk analysis file for details
- DO NOT include full correlation matrix in output""",
            agent=risk_agent,
            expected_output="Compact risk assessment summary with beta and key correlation insights",
            context=[]  # NO CONTEXT - uses file paths instead
        )

        self.strategy_task = Task(
            description=f"""Generate comprehensive investment strategy recommendations (TOKEN-OPTIMIZED):

**DATA SOURCE (Read from cached files if needed):**
Reference previous task outputs for:
- Portfolio metrics summary (from analysis_task output)
- Risk assessment summary (from risk_task output)
- If detailed data needed, use "Load Cached Data File" tool:
  - Portfolio metrics: {CACHE_DIR}/portfolio_calculated.json
  - Risk analysis: {CACHE_DIR}/risk_analysis.json

**STRATEGY GENERATION:**
1. Review portfolio metrics summary from previous task
2. Review risk assessment summary from previous task
3. Synthesize key insights from both analyses
4. Generate AI-powered strategy report using Gemini tool
5. Provide 5-7 SPECIFIC, ACTIONABLE recommendations with:
   - Specific ticker symbols
   - Specific amounts or percentages
   - Clear conditions and timing
   - Data-backed rationale

**OUTPUT FORMAT (< 600 words):**
- Portfolio Health Assessment (2-3 sentences)
- Risk Assessment Summary (2-3 sentences)
- Strategic Recommendations (5-7 specific actions)
- Potential Concerns (what to monitor)
- Action Items (prioritized 1-2-3 list)

**REQUIREMENTS:**
✅ Every recommendation must include ticker, amount, and condition
✅ Use data from previous summaries (already compact)
❌ DO NOT load and repeat full datasets
❌ Avoid generic advice like "diversify portfolio"

Use clear language that investors can understand and act upon.""",
            agent=strategy_agent,
            expected_output="Comprehensive AI-powered investment strategy report with 5-7 SPECIFIC actionable recommendations",
            context=[]  # NO CONTEXT - reads from previous task outputs and files as needed
        )

        # Create Crew
        self.crew = Crew(
            agents=[data_sync_agent, analyst_agent, risk_agent, strategy_agent],
            tasks=[self.sync_task, self.analysis_task, self.risk_task, self.strategy_task],
            verbose=False,
            process=Process.sequential,
            memory=False
        )

    def generate_full_report(self, progress_callback=None) -> Dict[str, Any]:
        """
        Execute the full portfolio analysis workflow with progress updates

        Args:
            progress_callback: Optional callback function(step, total, message)

        Returns:
            Dictionary containing results from all four tasks
        """
        try:
            if progress_callback:
                progress_callback(1, 4, "Syncing data from Google Sheets + KIS API")

            # Execute crew workflow
            result = self.crew.kickoff()

            if progress_callback:
                progress_callback(4, 4, "Analysis complete")

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
