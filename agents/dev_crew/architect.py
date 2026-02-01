"""
Architect Agent [Meta-System]
Translates research into actionable blueprints and manages system integrity.
"""
import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.dev_tools.blueprint_maker import generate_blueprint

class ArchitectAgent:
    def __init__(self):
        self.name = "🏗️ Project Architect"

    def design_feature(self, feature_name: str, research_filename: str):
        """
        Generates a blueprint based on research findings.
        """
        print(f"{self.name}: Designing architecture for '{feature_name}'...")
        
        research_path = os.path.join("docs", "explorations", f"{research_filename}.md")
        
        # Call tool to generate plan
        plan_content = generate_blueprint(research_path, feature_name)
        
        # Save to planning
        output_filename = f"{feature_name.upper().replace(' ', '_')}_PLAN.md"
        output_path = os.path.join("docs", "planning", output_filename)
        
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError:
                pass # Already exists or permission error
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(plan_content)
            
        print(f"✅ Implementation Plan saved to: {output_path}")
        return output_path

if __name__ == "__main__":
    architect = ArchitectAgent()
    architect.design_feature("Market Screener Grid", "SCREENER_RESEARCH")
