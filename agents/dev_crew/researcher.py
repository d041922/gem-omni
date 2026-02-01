"""
Research Specialist Agent [Meta-System]
Uses Dev Tools to gather information and produce actionable research reports.
"""
import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.dev_tools.library_hunter import hunt_libraries
from agents.dev_tools.site_analyzer import analyze_site_structure

class ResearchAgent:
    def __init__(self):
        self.name = "🕵️ Research Specialist"
        
    def research_feature(self, feature_name: str, context: str) -> str:
        """
        Conducts comprehensive research for a specific feature.
        """
        print(f"{self.name}: Starting research on '{feature_name}'...")
        
        # 1. Tech Stack Research
        print(f"   -> Hunting libraries for {feature_name}...")
        # In a real agent loop, this would trigger the actual search tool.
        # Here we simulate the agent's thought process calling the tool wrapper.
        hunt_libraries(feature_name, context)
        
        # 2. UI/UX Reference (Simulation)
        print("   -> Analyzing references...")
        # Mocking a reference URL for this task
        ref_url = "https://www.investing.com/stock-screener/"
        analyze_site_structure(ref_url, "filters and grid layout")
        
        # 3. Synthesis (Report Generation)
        report = f"""# 🕵️ Research Report: {feature_name}

## 1. Technology Recommendations ({context})
Based on the requirement, here are the best libraries:

### Option A: st.data_editor (Native)
- **Pros**: Built-in, fast, editable.
- **Cons**: Limited complex filtering UI.
- **Verdict**: Good for simple V1.

### Option B: streamlit-aggrid (External)
- **Pros**: Powerful Excel-like filtering, sorting, pagination.
- **Cons**: External dependency, heavier load.
- **Verdict**: **Recommended** for a pro-level screener.

## 2. UI/UX Reference (Investing.com Style)
- **Layout**: Left Sidebar (Filters) + Main Area (Results Grid).
- **Key Components**:
  - **Multi-select Filters**: Sector, Industry, PE Range.
  - **Dynamic Columns**: Toggle visibility of metrics.
  - **Visual Indicators**: Color-coded changes (Red/Green).

## 3. Implementation Strategy
1.  Use `AgGrid` for the main result table.
2.  Implement a 'Filter Panel' on the left (or expandable top section).
3.  Add 'Preset Scans' (e.g., "Undervalued Growth") as quick buttons.
"""
        return report

    def save_report(self, title: str, content: str):
        """Saves the report to the docs/research directory."""
        path = os.path.join("docs", "explorations", f"{title}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Report saved to: {path}")

if __name__ == "__main__":
    agent = ResearchAgent()
    
    # Task: Research for Market Screener
    result = agent.research_feature("Stock Screener Grid", "Streamlit")
    agent.save_report("SCREENER_RESEARCH", result)
