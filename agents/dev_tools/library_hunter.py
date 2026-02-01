"""
Library Hunter [Dev Tool]
Finds the best Python libraries for a specific requirement using Context7 & Search.
"""

class LibraryHunter:
    def __init__(self):
        self.name = "Library Hunter"

    def find_libraries(self, requirement: str, environment: str = "Streamlit") -> str:
        """
        Searches for libraries matching the requirement.
        
        Args:
            requirement: What we need (e.g., "Interactive Data Grid", "Financial Charts")
            environment: Context (e.g., "Streamlit", "Python CLI")
            
        Returns:
            List of recommended libraries with pros/cons.
        """
        prompt = f"""
        [SYSTEM ACTION]
        1. Search for '{requirement}' libraries compatible with {environment}.
        2. Use Context7 to check documentation and popularity.
        3. Compare top 3 candidates based on:
           - Ease of use
           - Feature set (does it meet '{requirement}'?)
           - Maintenance status
        4. Recommend the best one for our project.
        """
        return prompt

# Standalone function
def hunt_libraries(req: str, environment: str = "Streamlit") -> str:
    hunter = LibraryHunter()
    return hunter.find_libraries(req, environment)
