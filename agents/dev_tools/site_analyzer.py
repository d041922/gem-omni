"""
Site Structure Analyzer [Dev Tool]
Analyzes a URL to extract UI/UX patterns for benchmarking.
Uses 'web_fetch' capability to get content and LLM to parse structure.
"""

class SiteStructureAnalyzer:
    def __init__(self):
        self.name = "Site Structure Analyzer"

    def analyze(self, url: str, focus_area: str = "layout") -> str:
        """
        Fetches a URL and analyzes its structure focusing on UI components.
        
        Args:
            url: Target URL (e.g., investing.com screener)
            focus_area: What to look for (layout, filters, charts, navigation)
            
        Returns:
            Structured text describing the UI components found.
        """
        # Note: In a real scenario, this would call the `web_fetch` tool.
        # Since I am writing the tool code itself, I provide the interface for the Agent to use.
        
        prompt = f"""
        [SYSTEM ACTION]
        1. Fetch content from: {url}
        2. Analyze the HTML/Structure focusing on: '{focus_area}'
        3. Extract the following:
           - Navigation structure (Sidebar vs Topbar)
           - Data presentation (Table, Grid, List)
           - Interactive elements (Filters, Search, Sort)
           - Visual hierarchy (What stands out?)
        4. Return a summary for a UI Designer.
        """
        return prompt

# Standalone function
def analyze_site_structure(url: str, focus: str = "layout") -> str:
    analyzer = SiteStructureAnalyzer()
    return analyzer.analyze(url, focus)
