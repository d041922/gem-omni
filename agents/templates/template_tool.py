"""
Template Tool [Safe Edition]
Clean starting point for new custom tools.
"""
from pydantic import BaseModel, Field

class ToolInput(BaseModel):
    query: str = Field(..., description="The query to process")

class TemplateTool:
    def __init__(self):
        self.name = "Template Tool"

    def execute(self, query: str) -> str:
        return f"Result for {query}"