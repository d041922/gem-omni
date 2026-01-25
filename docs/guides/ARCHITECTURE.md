# GEM: OMNI Architecture (CrewAI-based)

## Overview

GEM: OMNI is a personal AI agent system for managing 8 life domains. The finance domain has been redesigned using **CrewAI**, a production-grade multi-agent framework.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                          │
│         (CLI: main.py, Web UI: app.py)                     │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│               GeminiOmniSystem (Master)                     │
│         - Agent lifecycle management                         │
│         - Request routing                                    │
│         - Memory management                                  │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
┌───────▼──────────┐                   ┌─────────▼──────────┐
│  FinanceCrew     │                   │  Future Crews      │
│  (CrewAI)        │                   │  - HealthCrew      │
│                  │                   │  - RelationshipCrew│
└──────────────────┘                   │  - ...             │
        │                              └────────────────────┘
        │
        ├─ DataSyncAgent ──────┬─ GSheetLoaderTool
        │                      └─ KISAccountTool
        │
        ├─ AnalystAgent ────────── PortfolioMetricsCalculatorTool
        │
        ├─ RiskAgent ──────────── QuantRiskAnalysisTool
        │
        └─ StrategyAgent ──────── GeminiStrategyTool
```

## Components

### 1. Master Controller (main.py)

**GeminiOmniSystem**
- Manages all domain crews
- Routes user requests to appropriate crew
- Handles memory persistence

### 2. FinanceCrew (agents/crews/finance_crew.py)

**Purpose**: Comprehensive portfolio analysis and strategy generation

**Agents**:
1. **DataSyncAgent** (20-year veteran data engineer)
   - Tools: GSheetLoaderTool, KISAccountTool
   - Role: Load and synchronize portfolio data

2. **AnalystAgent** (CFA, 15-year portfolio manager)
   - Tools: PortfolioMetricsCalculatorTool
   - Role: Calculate metrics and analyze performance

3. **RiskAgent** (MIT PhD, 12-year quant analyst)
   - Tools: QuantRiskAnalysisTool
   - Role: Assess portfolio risk (beta, correlations)

4. **StrategyAgent** (CIO, 25-year investment strategist)
   - Tools: GeminiStrategyTool
   - Role: Generate AI-powered strategy reports

**Workflow** (Sequential):
```
Data Sync → Portfolio Analysis → Risk Assessment → Strategy Generation
```

### 3. Tools (agents/tools/)

Tools wrap existing skills into CrewAI BaseTool format:

- **gsheet_tools.py**: Google Sheets integration
- **kis_tools_wrapper.py**: KIS brokerage API
- **portfolio_tools.py**: Portfolio calculations
- **quant_tools.py**: Risk analysis (beta, correlation)
- **ai_strategy_tools.py**: Gemini AI strategy generation

### 4. Memory System (core/memory.py)

**MemorySystem**
- User profile storage
- Conversation history
- Portfolio state persistence
- JSON-based storage in `memory/` directory

### 5. User Interfaces

**CLI (main.py)**
```bash
python main.py
>>> 재정 분석해줘
```

**Web UI (app.py)**
- Streamlit-based dashboard
- Run Full Audit button triggers FinanceCrew
- Displays strategy report and metrics

## Why CrewAI?

### vs Custom Implementation

| Feature | Custom | CrewAI |
|---------|--------|--------|
| Development Speed | Slow | Fast (5.76x) |
| Error Handling | Manual | Automatic |
| Memory Management | Custom | Built-in |
| Community Support | None | Active |
| Scalability | Difficult | Easy |

### vs LangGraph

| Feature | LangGraph | CrewAI |
|---------|-----------|--------|
| Learning Curve | High (graph-based) | Low (role-based) |
| Use Case | Complex conditional flows | Sequential team workflows |
| Ease of Extension | Requires graph redesign | Add new agents |

## Data Flow Example

```
1. User: "재정 분석해줘"
   ↓
2. GeminiOmniSystem.route_request()
   ↓
3. FinanceCrew.generate_full_report()
   ↓
4. Task 1: DataSyncAgent
   - Loads from Google Sheets (GSheetLoaderTool)
   - Fetches from KIS API (KISAccountTool)
   - Output: Portfolio data
   ↓
5. Task 2: AnalystAgent
   - Calculates metrics (PortfolioMetricsCalculatorTool)
   - Input: Task 1 output (context)
   - Output: Portfolio analysis
   ↓
6. Task 3: RiskAgent
   - Analyzes risk (QuantRiskAnalysisTool)
   - Input: Task 2 output (context)
   - Output: Risk assessment
   ↓
7. Task 4: StrategyAgent
   - Generates strategy (GeminiStrategyTool)
   - Input: Task 2 + Task 3 output (context)
   - Output: AI strategy report
   ↓
8. Return to user: Complete analysis report
```

## Extension Guide

### Adding a New Domain (e.g., Health)

1. **Create Agents** (agents/crewai_agents/)
```python
# health_tracker_agent.py
from crewai import Agent
from agents.tools.health_tools import FitbitTool

health_tracker = Agent(
    role="Health Data Specialist",
    goal="Track and analyze health metrics",
    tools=[FitbitTool()],
    ...
)
```

2. **Create Tools** (agents/tools/)
```python
# health_tools.py
from crewai_tools import BaseTool

class FitbitTool(BaseTool):
    name = "Fetch Fitbit Data"
    ...
```

3. **Create Crew** (agents/crews/)
```python
# health_crew.py
from crewai import Crew

class HealthCrew:
    def __init__(self):
        self.crew = Crew(
            agents=[health_tracker, ...],
            tasks=[...],
            process=Process.sequential
        )
```

4. **Register in Main**
```python
# main.py
self.agents['health'] = HealthCrew(memory_system=self.memory)
```

## Safety Features

### Git Version Control
- All changes tracked in Git
- Backup branch: `backup-original`
- Rollback: `git checkout backup-original`

### Claude Code Hooks
- PreToolUse: Warns before modifying critical files
- PostToolUse: Auto syntax check after file write
- UserPromptSubmit: Detects dangerous operations

### Safety Rules (rules/050-safety-protocol.mdc)
- One file at a time
- Commit immediately after changes
- Three-strike error rule
- Test-first development

## Technology Stack

- **Framework**: CrewAI 1.8.1
- **LLM**: Gemini 2.0 Flash
- **Data Sources**: Google Sheets API, KIS API
- **UI**: Streamlit
- **Memory**: JSON files
- **Version Control**: Git

## Performance

- **Workflow Execution**: ~30-60 seconds (4 sequential tasks)
- **Data Sync**: ~2-5 seconds
- **Portfolio Analysis**: ~3-8 seconds
- **Risk Assessment**: ~10-20 seconds (downloads historical data)
- **AI Strategy**: ~5-10 seconds (Gemini API)

## Future Enhancements

1. **Parallel Task Execution** (where possible)
2. **Real-time Data Streaming** (websockets)
3. **Advanced Memory** (vector embeddings)
4. **Multi-language Support** (i18n)
5. **Mobile App** (React Native)

## References

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/crewAIInc/crewAI)
- [Gemini API Docs](https://ai.google.dev/docs)
