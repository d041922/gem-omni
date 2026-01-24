"""
Template Crew for New Domain
Replace {DOMAIN} with your domain name (e.g., Health, Relationships, Education)
"""
from crewai import Crew, Task, Process
import sys
import os
from typing import Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import your agents
# from agents.crewai_agents.{domain}_agent1 import agent1
# from agents.crewai_agents.{domain}_agent2 import agent2


class {Domain}Crew:
    """
    {Domain}Crew: Brief description of what this crew does

    This crew orchestrates:
    1. First major responsibility
    2. Second major responsibility
    3. Third major responsibility
    """

    def __init__(self, memory_system=None, **kwargs):
        """
        Initialize {Domain}Crew

        Args:
            memory_system: Optional memory system for context persistence
            **kwargs: Additional configuration parameters
        """
        self.memory = memory_system

        # Define Tasks
        self.task1 = Task(
            description="""Detailed instructions for task 1:
1. Specific step 1
2. Specific step 2
3. Specific step 3

Return a structured summary including:
- Field 1 description
- Field 2 description
- Any warnings or issues""",
            agent=None,  # Replace with your agent: agent1
            expected_output="Description of expected output format"
        )

        self.task2 = Task(
            description="""Detailed instructions for task 2:
1. Use the data from task 1
2. Perform analysis/processing
3. Generate insights

Provide a comprehensive report with:
- Summary statistics
- Key findings
- Recommendations""",
            agent=None,  # Replace with your agent: agent2
            expected_output="Description of expected output format",
            context=[self.task1]  # Uses output from task1
        )

        # Create Crew
        self.crew = Crew(
            agents=[],  # Add your agents here: [agent1, agent2]
            tasks=[self.task1, self.task2],
            verbose=True,
            process=Process.sequential,
            memory=False  # Disable if using custom memory system
        )

    def execute_workflow(self) -> Dict[str, Any]:
        """
        Execute the full {domain} workflow

        Returns:
            Dictionary containing workflow results
        """
        try:
            # Execute crew workflow
            result = self.crew.kickoff()

            # Parse result
            return {
                "success": True,
                "result": str(result),
                "message": f"Successfully completed {domain} workflow"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to complete {domain} workflow: {str(e)}"
            }

    def task1_only(self) -> Dict[str, Any]:
        """
        Execute only the first task (for testing or partial workflows)

        Returns:
            Dictionary containing task1 results
        """
        try:
            result = self.task1.execute_sync()
            return {
                "success": True,
                "result": result,
                "message": "Task 1 completed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Task 1 failed: {str(e)}"
            }
