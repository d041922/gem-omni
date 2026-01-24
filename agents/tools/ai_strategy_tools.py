"""
AI Strategy Tools for CrewAI
Uses Gemini API to generate strategy insights
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict
from pydantic import BaseModel, Field
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class AIStrategyInput(BaseModel):
    """Input schema for AI Strategy Tool"""
    portfolio_summary: str = Field(..., description="Portfolio summary text including metrics and holdings")
    risk_analysis: str = Field(..., description="Risk analysis summary including beta and correlations")
    market_context: str = Field(default="", description="Current market conditions and context")


class GeminiStrategyTool(BaseTool):
    name: str = "Generate AI Strategy Report"
    description: str = (
        "Generates AI-powered investment strategy report using Gemini API. "
        "Takes portfolio summary, risk analysis, and market context as input. "
        "Returns strategic recommendations, insights, and action items. "
        "Use this tool to get AI-driven investment advice."
    )
    args_schema: Type[BaseModel] = AIStrategyInput

    def _run(
        self,
        portfolio_summary: str,
        risk_analysis: str,
        market_context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate AI strategy report

        Args:
            portfolio_summary: Portfolio summary text
            risk_analysis: Risk analysis summary
            market_context: Market context (optional)

        Returns:
            Dictionary containing AI-generated strategy report
        """
        try:
            # Initialize Gemini
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "message": "GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables"
                }

            client = genai.Client(api_key=api_key)

            # Create prompt
            prompt = f"""
You are an expert financial advisor analyzing a portfolio.

**Portfolio Summary:**
{portfolio_summary}

**Risk Analysis:**
{risk_analysis}

**Market Context:**
{market_context if market_context else "No specific market context provided"}

Please provide a comprehensive investment strategy report with the following sections:

1. **Portfolio Health Assessment**: Overall evaluation of the current portfolio
2. **Risk Assessment**: Analysis of portfolio risks and diversification
3. **Strategic Recommendations**: Specific actionable recommendations
4. **Potential Concerns**: Key risks and areas to monitor
5. **Action Items**: Prioritized list of next steps

Format your response in clear, structured sections with bullet points.
"""

            # Generate response
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            strategy_text = response.text

            return {
                "success": True,
                "strategy_report": strategy_text,
                "model_used": "gemini-2.5-flash",
                "message": "Successfully generated AI strategy report"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate AI strategy report: {str(e)}"
            }
