"""
Search Tool for Agents [GEM: OMNI]
Tavily AI Search를 사용하여 에이전트에게 최신 시장 정보를 제공합니다.
LLM이 이해하기 쉬운 요약된 텍스트 형태로 결과를 반환합니다.
"""
import os
import logging
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from tavily import TavilyClient

# Configure Logger
logger = logging.getLogger("SearchTool")

class SearchToolInput(BaseModel):
    query: str = Field(..., description="The search query to find information about (e.g., 'Samsung Electronics recent news').")
    max_results: int = Field(default=3, description="Number of search results to return.")

class TavilySearchTool(BaseTool):
    name: str = "Deep Market Search"
    description: str = (
        "A specialized search engine for financial markets. "
        "Use this to find real-time news, market sentiment, or specific events "
        "that are not available in the internal database. "
        "Returns concise, fact-based summaries."
    )
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str, max_results: int = 3) -> str:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Error: TAVILY_API_KEY not found in environment variables. Please set it in .env file."

        try:
            client = TavilyClient(api_key=api_key)
            # 'search' returns a dict with 'results' list
            response = client.search(
                query=query, 
                search_depth="advanced", # 'advanced' or 'basic'
                max_results=max_results,
                include_answer=True # Let Tavily generate a short answer
            )
            
            # Construct a readable context
            context_parts = []
            
            # 1. Direct Answer (if available)
            if response.get('answer'):
                context_parts.append(f"**Quick Answer:** {response['answer']}")
                context_parts.append("---")

            # 2. Detailed Results
            for res in response.get('results', []):
                title = res.get('title', 'No Title')
                content = res.get('content', '')
                url = res.get('url', '')
                date = res.get('published_date', 'Unknown Date')
                
                context_parts.append(f"### {title} ({date})")
                context_parts.append(f"- URL: {url}")
                context_parts.append(f"- Summary: {content[:300]}...") # Limit content length
                context_parts.append("")
            
            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return f"Search failed due to an error: {str(e)}"

# Standalone function for non-agent usage
def get_market_news(query: str, max_results: int = 3) -> str:
    tool = TavilySearchTool()
    return tool._run(query, max_results)
