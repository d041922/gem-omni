"""
Dev Crew Controller [Meta-System]
The Main Entry Point for Master's Commands.
"""
import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.dev_crew.interpreter import RequirementsAnalyst
from agents.dev_crew.pm import ProjectManager

def main():
    print("💎 GEM: OMNI Dev Crew System v1.0")
    print("Waiting for Master's command...")
    
    # In CLI mode, we take argument or input
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "Market 탭 UX 개선하고 스크리너 기능 완성해줘" # Default for test

    # 1. Interpret
    analyst = RequirementsAnalyst()
    spec = analyst.analyze(user_input)
    
    # 2. Plan & Execute
    pm = ProjectManager()
    roadmap = pm.create_roadmap(spec)
    
    # 3. Execution (Delegation)
    pm.execute_roadmap(roadmap)

if __name__ == "__main__":
    main()
