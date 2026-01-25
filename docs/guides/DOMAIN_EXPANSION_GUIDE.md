# Domain Expansion Guide for GEM: OMNI

## Overview

GEM: OMNI is designed to manage 8 life domains. Currently, the **Finance** domain is fully implemented using CrewAI. This guide shows you how to add new domains.

## 8 Target Domains

1. ✅ **Finance** - Portfolio management, investment strategy
2. ⬜ **Health** - Fitness tracking, nutrition, medical records
3. ⬜ **Relationships** - Social connections, family, networking
4. ⬜ **Education** - Learning goals, skill development, courses
5. ⬜ **Career** - Job search, professional development, projects
6. ⬜ **Productivity** - Task management, time tracking, habits
7. ⬜ **Lifestyle** - Travel, hobbies, entertainment
8. ⬜ **Spiritual** - Meditation, mindfulness, personal values

## Quick Start: Adding a New Domain

Let's use **Health** as an example to show how to add a new domain.

### Step 1: Define Your Domain Requirements

Answer these questions:

1. **What data sources will you use?**
   - Example: Fitbit API, Apple Health, manual input

2. **What agents do you need?**
   - Example: Health Tracker (data sync), Health Analyst (analysis), Coach (recommendations)

3. **What are the key workflows?**
   - Example: Daily sync → Weekly analysis → Monthly coaching

4. **What outputs do you want?**
   - Example: Health dashboard, trend reports, personalized tips

### Step 2: Create Tools

Create `agents/tools/health_tools.py`:

```python
from crewai_tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field

class FitbitDataInput(BaseModel):
    date_range: str = Field(default="7d", description="Date range (e.g., 7d, 30d)")

class FitbitDataTool(BaseTool):
    name: str = "Fetch Fitbit Data"
    description: str = (
        "Fetches health metrics from Fitbit API including steps, heart rate, sleep. "
        "Returns daily data for the specified date range. "
        "Use this tool to get current health metrics."
    )
    args_schema: Type[BaseModel] = FitbitDataInput

    def _run(self, date_range: str = "7d") -> Dict[str, Any]:
        try:
            # Your Fitbit API logic here
            # data = fetch_from_fitbit(date_range)

            return {
                "success": True,
                "steps": 8500,
                "heart_rate_avg": 72,
                "sleep_hours": 7.5,
                "date_range": date_range,
                "message": "Successfully fetched Fitbit data"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to fetch Fitbit data: {str(e)}"
            }
```

### Step 3: Create Agents

Create `agents/crewai_agents/health_tracker_agent.py`:

```python
from crewai import Agent
from agents.tools.health_tools import FitbitDataTool

def create_health_tracker_agent() -> Agent:
    return Agent(
        role="Health Data Tracking Specialist",
        goal="Accurately track and sync health metrics from multiple sources",
        backstory="""You are a health data specialist with 10 years of experience
        working with wearable devices and health tracking systems. You worked at
        Apple Health and Fitbit, ensuring data accuracy and privacy.

        Your expertise includes:
        - Wearable device data integration
        - Health metrics normalization
        - Data validation and quality checks
        - Privacy and HIPAA compliance

        You are meticulous about data accuracy and user privacy.""",
        tools=[FitbitDataTool()],
        verbose=True,
        allow_delegation=False
    )

health_tracker_agent = create_health_tracker_agent()
```

Create more agents as needed (analyst, coach, etc.)

### Step 4: Create Crew

Create `agents/crews/health_crew.py`:

```python
from crewai import Crew, Task, Process
from agents.crewai_agents.health_tracker_agent import health_tracker_agent

class HealthCrew:
    def __init__(self, memory_system=None):
        self.memory = memory_system

        self.tracking_task = Task(
            description="""
            Fetch health metrics for the past 7 days:
            1. Get steps, heart rate, sleep data from Fitbit
            2. Validate data completeness
            3. Calculate daily averages

            Return a summary with:
            - Average daily steps
            - Average heart rate
            - Average sleep hours
            - Data quality score
            """,
            agent=health_tracker_agent,
            expected_output="Health metrics summary for past 7 days"
        )

        self.crew = Crew(
            agents=[health_tracker_agent],
            tasks=[self.tracking_task],
            verbose=True,
            process=Process.sequential
        )

    def get_health_summary(self):
        result = self.crew.kickoff()
        return {
            "success": True,
            "summary": str(result),
            "message": "Health summary generated"
        }
```

### Step 5: Register in Main Controller

Edit `main.py`:

```python
from agents.crews.health_crew import HealthCrew

class GeminiOmniSystem:
    def _register_agents(self):
        # Existing finance crew
        self.agents['finance'] = FinanceCrew(...)

        # Add health crew
        self.agents['health'] = HealthCrew(memory_system=self.memory)
        logger.info("Agent registered: HealthCrew")
```

Update routing logic:

```python
def route_request(self, user_input: str):
    # Existing finance routing
    if "재정" in user_input or "주식" in user_input:
        # ... finance logic

    # Add health routing
    elif "건강" in user_input or "운동" in user_input or "수면" in user_input:
        health_crew = self.agents.get('health')
        if health_crew:
            print("\n[GEM: OMNI] HealthCrew 실행 중...")
            result = health_crew.get_health_summary()
            print(f"\n[GEM: OMNI] {result['summary']}\n")
```

### Step 6: Test Your Domain

Create `tests/test_health_crew.py`:

```python
from agents.crews.health_crew import HealthCrew

def test_health_crew():
    crew = HealthCrew(memory_system=None)
    result = crew.get_health_summary()

    assert result['success'] == True
    assert 'summary' in result
    print(f"Health Summary: {result['summary']}")

if __name__ == "__main__":
    test_health_crew()
```

Run test:
```bash
python tests/test_health_crew.py
```

### Step 7: Add to Streamlit UI (Optional)

Edit `app.py` to add a Health tab:

```python
tab1, tab2 = st.tabs(["💰 Finance", "🏃 Health"])

with tab1:
    # Existing finance UI
    ...

with tab2:
    st.markdown("## Health Dashboard")
    if st.button("📊 Get Health Summary"):
        with st.spinner("Analyzing health data..."):
            result = st.session_state.health_crew.get_health_summary()
            st.markdown(result['summary'])
```

## Using Templates

We provide templates to speed up development:

### 1. Copy Template Files

```bash
# Copy and rename templates
cp agents/templates/template_agent.py agents/crewai_agents/health_tracker_agent.py
cp agents/templates/template_tool.py agents/tools/health_tools.py
cp agents/templates/template_crew.py agents/crews/health_crew.py
```

### 2. Search and Replace

Replace placeholders in the copied files:

- `{DOMAIN}` → `Health`
- `{domain}` → `health`
- `{ACTION}` → `Fetch` (or other action)
- `{Object}` → `Data` (or other object)

### 3. Customize

- Update agent backstories
- Add your specific tools
- Define your workflows
- Adjust task descriptions

## Domain-Specific Considerations

### Health Domain

**Data Sources**: Fitbit, Apple Health, Google Fit, MyFitnessPal
**Privacy**: HIPAA compliance, data encryption
**Key Metrics**: Steps, heart rate, sleep, nutrition, weight

### Relationships Domain

**Data Sources**: Calendar, contacts, social media APIs
**Privacy**: Contact consent, relationship sensitivity
**Key Metrics**: Interaction frequency, relationship quality scores

### Education Domain

**Data Sources**: Coursera API, Udemy, GitHub contributions
**Key Metrics**: Course completion, skill proficiency, certificates

### Career Domain

**Data Sources**: LinkedIn, GitHub, project management tools
**Key Metrics**: Job applications, skill growth, network expansion

### Productivity Domain

**Data Sources**: Todoist, Notion, RescueTime
**Key Metrics**: Tasks completed, time spent, habit streaks

## Best Practices

### 1. Start Simple

- Begin with 1-2 agents
- Focus on one workflow
- Add complexity gradually

### 2. Reuse Patterns from Finance

- Similar data sync workflow
- Analysis → Risk → Strategy pattern works for many domains
- Adapt rather than reinvent

### 3. Test Incrementally

- Test tools individually
- Test agents individually
- Test crew as a whole
- Test integration with main system

### 4. Document as You Go

- Update ARCHITECTURE.md
- Add domain-specific guide
- Document data sources and APIs

### 5. Consider Data Privacy

- Encrypt sensitive data
- Follow regulations (HIPAA, GDPR)
- Get user consent
- Implement access controls

## Common Challenges

### Challenge 1: API Rate Limits

**Solution**: Implement caching and rate limiting

```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def fetch_data_cached(param):
    time.sleep(0.1)  # Rate limiting
    return fetch_data(param)
```

### Challenge 2: Data Inconsistency

**Solution**: Add validation layer

```python
def validate_health_data(data):
    if data['heart_rate'] < 40 or data['heart_rate'] > 200:
        return False, "Heart rate out of normal range"
    return True, "Valid"
```

### Challenge 3: Long-Running Tasks

**Solution**: Use async execution or background tasks

```python
import asyncio

async def long_task():
    result = await crew.kickoff_async()
    return result
```

## Example: Complete Health Domain

See the full example in `examples/health_domain/` (to be added).

## Next Steps

1. Choose your next domain
2. Define requirements
3. Copy templates
4. Implement tools and agents
5. Test thoroughly
6. Integrate with main system
7. Add UI (optional)
8. Document your domain

## Getting Help

- Read [ARCHITECTURE.md](ARCHITECTURE.md)
- Study [CREWAI_GUIDE.md](CREWAI_GUIDE.md)
- Review finance domain implementation
- Check CrewAI examples: https://github.com/crewAIInc/crewAI-examples

## Contributing

If you implement a new domain:

1. Test thoroughly
2. Document the domain
3. Create a pull request
4. Share your experience

Together we can build all 8 domains!
