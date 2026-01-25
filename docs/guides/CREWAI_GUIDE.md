# CrewAI Usage Guide for GEM: OMNI

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Creating Agents](#creating-agents)
4. [Creating Tools](#creating-tools)
5. [Creating Crews](#creating-crews)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Introduction

CrewAI is a multi-agent orchestration framework that allows you to create teams of AI agents that work together to accomplish complex tasks. In GEM: OMNI, we use CrewAI to power the finance domain analysis.

## Core Concepts

### 1. Agents

Agents are AI-powered team members with specific roles and expertise.

**Key Components**:
- **Role**: What the agent does (e.g., "Data Analyst")
- **Goal**: What the agent aims to achieve
- **Backstory**: Context and expertise (helps with LLM reasoning)
- **Tools**: Functions the agent can use
- **Verbose**: Whether to show detailed logs
- **Allow Delegation**: Whether agent can delegate to others

### 2. Tools

Tools are functions that agents can use to interact with external systems.

**Key Components**:
- **name**: Human-readable tool name
- **description**: What the tool does (helps agent decide when to use it)
- **args_schema**: Pydantic model defining input parameters
- **_run()**: The actual function implementation

### 3. Tasks

Tasks are specific jobs assigned to agents.

**Key Components**:
- **description**: Detailed instructions for the agent
- **agent**: Which agent will execute this task
- **expected_output**: What format the output should be in
- **context**: List of previous tasks whose outputs this task depends on

### 4. Crews

Crews are teams of agents working together on a set of tasks.

**Key Components**:
- **agents**: List of agents in the crew
- **tasks**: List of tasks to execute
- **process**: Sequential or hierarchical execution
- **verbose**: Show detailed logs
- **memory**: Enable built-in memory

## Creating Agents

### Example: Creating a Data Analyst Agent

```python
from crewai import Agent
from agents.tools.data_tools import DataLoaderTool

data_analyst = Agent(
    role="Senior Data Analyst",
    goal="Load and validate data from multiple sources accurately",
    backstory="""You are a veteran data analyst with 15 years of experience.
    You've worked at Google and Meta, handling petabyte-scale data pipelines.
    You are obsessed with data quality and never compromise on accuracy.""",
    tools=[
        DataLoaderTool()
    ],
    verbose=True,
    allow_delegation=False  # This agent works alone
)
```

### Agent Personality Tips

1. **Be Specific**: Give detailed backstories with years of experience
2. **Add Context**: Mention companies, achievements, specializations
3. **Set Expectations**: Describe their work style (meticulous, fast, cautious, etc.)
4. **Avoid Jargon**: Use clear, professional language

### When to Use allow_delegation=True

Use delegation when:
- Agent might need help from specialists
- Task is complex and benefits from collaboration
- You have a hierarchical team structure

Don't use delegation when:
- Agent is highly specialized
- Task is straightforward
- You want predictable execution flow

## Creating Tools

### Example: Creating a Database Query Tool

```python
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd

class DatabaseQueryInput(BaseModel):
    """Input for database query tool"""
    query: str = Field(..., description="SQL query to execute")
    database: str = Field(default="production", description="Database name")

class DatabaseQueryTool(BaseTool):
    name: str = "Execute Database Query"
    description: str = (
        "Executes SQL queries on the specified database. "
        "Returns results as a pandas DataFrame. "
        "Use this tool to fetch data from the database."
    )
    args_schema: Type[BaseModel] = DatabaseQueryInput

    def _run(self, query: str, database: str = "production") -> dict:
        """
        Execute a database query

        Args:
            query: SQL query string
            database: Database name

        Returns:
            Dictionary with success status and results
        """
        try:
            # Your database logic here
            # df = execute_query(query, database)

            return {
                "success": True,
                "data": df.to_dict(orient='records'),
                "row_count": len(df),
                "message": f"Query executed successfully on {database}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute query: {str(e)}"
            }
```

### Tool Design Best Practices

1. **Clear Descriptions**: Agents use descriptions to decide when to use the tool
2. **Error Handling**: Always return success/failure status
3. **Structured Output**: Use dictionaries with consistent schema
4. **Input Validation**: Use Pydantic models for type safety
5. **Helpful Messages**: Include human-readable messages in output

### Tool Naming Conventions

- Use imperative verbs: "Fetch", "Calculate", "Generate", "Analyze"
- Be specific: "Fetch Historical Stock Prices" not just "Get Data"
- Include domain: "Calculate Portfolio Beta" not just "Calculate Beta"

## Creating Crews

### Example: Creating an Analysis Crew

```python
from crewai import Crew, Task, Process
from agents.crewai_agents.data_analyst import data_analyst
from agents.crewai_agents.report_writer import report_writer

class AnalysisCrew:
    def __init__(self, memory_system=None):
        self.memory = memory_system

        # Define tasks
        self.data_task = Task(
            description="""
            Load data from the following sources:
            1. PostgreSQL database (last 30 days)
            2. CSV files in /data/imports
            3. API endpoint: https://api.example.com/metrics

            Validate data quality and handle missing values.
            Return a clean, merged dataset.
            """,
            agent=data_analyst,
            expected_output="Clean dataset with summary statistics"
        )

        self.report_task = Task(
            description="""
            Analyze the dataset and create a comprehensive report including:
            1. Key metrics and trends
            2. Anomaly detection
            3. Forecasts and predictions
            4. Actionable recommendations

            Format the report in Markdown.
            """,
            agent=report_writer,
            expected_output="Markdown report with analysis and recommendations",
            context=[self.data_task]  # Uses output from data_task
        )

        # Create crew
        self.crew = Crew(
            agents=[data_analyst, report_writer],
            tasks=[self.data_task, self.report_task],
            verbose=True,
            process=Process.sequential,
            memory=False
        )

    def run_analysis(self):
        """Execute the full analysis workflow"""
        result = self.crew.kickoff()
        return result
```

### Task Context (Data Flow)

Tasks can use outputs from previous tasks via the `context` parameter:

```python
task_2 = Task(
    description="Use the data from task 1 to calculate metrics",
    agent=analyst,
    context=[task_1]  # task_2 receives task_1's output
)

task_3 = Task(
    description="Create report using data and metrics",
    agent=writer,
    context=[task_1, task_2]  # task_3 receives both outputs
)
```

### Process Types

**Sequential** (most common):
```python
process=Process.sequential
```
- Tasks execute one after another
- Each task can use previous task outputs
- Predictable execution flow

**Hierarchical**:
```python
process=Process.hierarchical
```
- Manager agent assigns tasks to workers
- More dynamic but less predictable
- Good for complex, adaptive workflows

## Best Practices

### 1. Agent Design

✅ **Do**:
- Give agents specific, narrow responsibilities
- Provide detailed backstories
- Use professional language
- Set clear goals

❌ **Don't**:
- Create "do everything" agents
- Use vague descriptions
- Mix multiple responsibilities
- Forget to specify expertise

### 2. Tool Design

✅ **Do**:
- Return structured, consistent outputs
- Handle errors gracefully
- Validate inputs
- Log important events

❌ **Don't**:
- Return unstructured strings
- Raise exceptions without handling
- Skip input validation
- Forget error messages

### 3. Task Descriptions

✅ **Do**:
- Be specific about requirements
- List steps explicitly
- Define expected output format
- Provide examples when helpful

❌ **Don't**:
- Use vague instructions
- Assume agent knows context
- Skip output format specification
- Make tasks too broad

### 4. Crew Organization

✅ **Do**:
- Keep crews focused on single domain
- Order tasks logically
- Use context to pass data between tasks
- Test incrementally (task by task)

❌ **Don't**:
- Mix unrelated domains
- Create circular dependencies
- Forget to set task context
- Try to test entire crew at once

## Troubleshooting

### Issue: Agent doesn't use the right tool

**Solution**:
- Improve tool description (be more specific)
- Clarify when the tool should be used
- Add examples to tool description
- Check if agent has access to the tool

### Issue: Task output is not what I expected

**Solution**:
- Make task description more specific
- Add "expected_output" with clear format
- Provide examples in description
- Check if agent has necessary context

### Issue: Crew is slow

**Solution**:
- Profile which task is slow
- Optimize tool implementations
- Consider caching frequently accessed data
- Use faster LLM model (e.g., Gemini Flash)

### Issue: Agent keeps making errors

**Solution**:
- Improve error handling in tools
- Add validation in tool inputs
- Make task description clearer
- Check if agent backstory sets right expectations

### Issue: Tasks not sharing data

**Solution**:
- Check `context` parameter in Task
- Ensure previous task returns data in expected format
- Verify task execution order
- Add logging to debug data flow

## Advanced Topics

### Memory Management

CrewAI has built-in memory, but we use custom MemorySystem:

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=False  # Disable built-in memory
)

# Use custom memory in tools
class CustomTool(BaseTool):
    def _run(self):
        memory = self.get_memory_system()
        # Use memory...
```

### Async Execution

For non-blocking crew execution:

```python
import asyncio

async def run_crew_async():
    result = await crew.kickoff_async()
    return result

# Usage
result = asyncio.run(run_crew_async())
```

### Error Recovery

Implement retry logic in tools:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustTool(BaseTool):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _run(self, ...):
        # Tool implementation
        pass
```

## Resources

- **Official Docs**: https://docs.crewai.com/
- **GitHub**: https://github.com/crewAIInc/crewAI
- **Examples**: https://github.com/crewAIInc/crewAI-examples
- **Discord**: https://discord.gg/X4JWnZnxPb

## Next Steps

1. Read the [Architecture Document](ARCHITECTURE.md)
2. Review existing agents in `agents/crewai_agents/`
3. Study tool implementations in `agents/tools/`
4. Try modifying FinanceCrew in `agents/crews/finance_crew.py`
5. Create your own crew for a new domain!
