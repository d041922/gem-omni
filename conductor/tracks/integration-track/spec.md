# Spec: System-Wide Tool Integration

## Purpose
Integrate Conductor, Security, Review, Stitch, Skillz, and Workspace extensions into the OMNI project core (SOP, Commander, and Rules).

## Goal
Transform the agent into a "Proactive Manager" that follows a strict safety and quality protocol automatically.

## Integration Points
1. **SOP (`core/AGENT_SOP.md`)**: Define mandatory steps for each tool.
2. **Commander (`scripts/omni_commander.py`)**: Add `--plan`, `--review`, and `--secure` flags for integrated orchestration.
3. **Rules (`core/RULES.md`)**: Enforce the use of these tools in the "Agent Constitution".
4. **Skills (`.gemini/skills/`)**: Register local skills to the `skillz` system.
