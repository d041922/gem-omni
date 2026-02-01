"""
BlueprintMaker [Dev Tool] v6.0: Data-Driven Architect
[Update History]
- v6.0: Removed all hardcoded metrics (SHA-256, fake latencies). 
        Now generates specs/plans strictly based on 'digested_data' provided by IntelligenceIngester.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional

class BlueprintMaker:
    def __init__(self):
        self.root_dir = Path(os.getcwd())

    def _format_list_to_markdown(self, items: List[str], default_msg: str) -> str:
        if not items:
            return f"- {default_msg}"
        return "\n".join([f"- {item}" for item in items])

    def create_conductor_files(self, digested_data: Dict, target_feature: str, track_id: str):
        """
        Generates spec.md and plan.md based ONLY on digested_data.
        No hallucinated metrics allowed.
        """
        
        # 1. Extract Real Data (Safe Get)
        summary = digested_data.get("research_summary_ko", "No research summary provided.")
        
        # Extract features/tasks - Expecting a list of dictionaries or strings
        # Data structure adaptation: Handle if ingester returns simple strings or complex dicts
        raw_practices = digested_data.get("best_practices", [])
        clean_tasks = []
        
        if raw_practices and isinstance(raw_practices[0], dict):
            for p in raw_practices:
                feat = p.get('feature', 'Unknown Feature')
                desc = p.get('description', '')
                clean_tasks.append(f"{feat}: {desc}")
        elif raw_practices and isinstance(raw_practices[0], str):
            clean_tasks = raw_practices
        
        # Extract Metrics - Expecting real metrics or None
        raw_metrics = digested_data.get("metrics", [])
        
        # 2. Build Briefing (Spec Header)
        briefing_section = (
            f"💎 **[Mission Analysis]** {target_feature}\n\n"
            f"🧪 **[Context Summary]**\n{summary}\n\n"
            f"📊 **[Target Metrics (KPI)]**\n"
            f"{self._format_list_to_markdown(raw_metrics, 'N/A (No specific metrics found in research)')}\n"
        )

        # 3. Build Gap Analysis Table (Spec Body)
        # Only build table if we have structured task data
        table_section = ""
        if clean_tasks:
            table_section = "\n## 📋 Implementation Requirements\n| Feature | Requirement |\n| :--- | :--- |\n"
            for task_str in clean_tasks:
                parts = task_str.split(":", 1)
                feat = parts[0]
                desc = parts[1] if len(parts) > 1 else "Implement as required"
                table_section += f"| {feat} | {desc.strip()} |\n"
        else:
            table_section = "\n## 📋 Implementation Requirements\n- No specific requirements extracted from intelligence.\n"

        # 4. Build Spec Content
        spec_content = f"# Spec: {target_feature} (Track: {track_id})\n\n{briefing_section}{table_section}"

        # 5. Build Execution Plan (Plan Body)
        # Dynamic task generation
        execution_tasks = ""
        if clean_tasks:
            for idx, task in enumerate(clean_tasks):
                execution_tasks += f"- [ ] Task {idx+1}: Implement {task.split(':')[0].strip()}\n"
        else:
             execution_tasks = "- [ ] Task 1: Analyze codebase (Fallback task due to missing intelligence)\n"

        plan_content = f"# Plan: {target_feature}\n\n## Phase 1: Preparation\n- [ ] Task 0: Verify workspace and dependencies.\n\n## Phase 2: Implementation (Data-Driven)\n{execution_tasks}## Phase 3: Verification\n- [ ] Task Final: Run verification script and validate outputs.\n"
        
        return spec_content, plan_content, briefing_section
