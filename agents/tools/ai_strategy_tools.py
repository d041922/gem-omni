"""
AI Strategy Tools [GEM: OMNI]
Provides AI-driven strategic insights and rebalancing recommendations.
"""
import streamlit as st
from typing import Type, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from skills.portfolio_utils import get_portfolio_summary
from skills.stock_analyzer import analyze_stock, get_technical_insight

class StrategyToolInput(BaseModel):
    """Input schema for StrategyTool"""
    action: str = Field(..., description="Action to perform: 'get_portfolio_status' or 'analyze_stock'")
    ticker: Optional[str] = Field(None, description="Ticker symbol for stock analysis")

class GeminiStrategyTool(BaseTool):
    name: str = "Investment Strategy Tool"
    description: str = "Provides portfolio-level insights and individual stock tactical advice."
    args_schema: Type[BaseModel] = StrategyToolInput

    def _run(self, action: str, ticker: Optional[str] = None) -> str:
        try:
            if action == 'get_portfolio_status':
                if 'calculated_portfolio' not in st.session_state:
                    return "Data not loaded."
                summary = get_portfolio_summary()
                return f"Portfolio Value: {summary.get('total_value', 0):,.0f}"
            
            elif action == 'analyze_stock' and ticker:
                res = analyze_stock(ticker)
                if not res.get('success'):
                    return f"Analysis failed: {res.get('error')}"
                s = res.get('summary', {})
                return f"Price: {s.get('current_price', 0)}, Tech: {get_technical_insight(s)}"
                
            return "Unknown action"
        except Exception as e:
            return f"Error: {e}"