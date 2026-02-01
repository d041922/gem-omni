"""
Deep Research Agent v3.0: Autonomous Searcher
Uses Gemini Grounding (Google Search) to fetch real-time knowledge without stopping.
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional

# Path Setup
current_file = Path(__file__).resolve()
root_dir = current_file.parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.dev_tools.key_loader import load_google_api_key

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class DeepResearchAgent:
    def __init__(self):
        self.root_dir = root_dir
        self.memory_path = self.root_dir / "memory" / "research_repo"
        self.api_key = load_google_api_key()
        
        if HAS_GENAI and self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def check_local_knowledge(self, query: str) -> Optional[str]:
        """Checks local markdown files for keywords."""
        query_words = set(query.lower().split())
        best_match = None
        max_hits = 0

        if self.memory_path.exists():
            for f in self.memory_path.rglob("*.md"):
                try:
                    content = f.read_text(encoding="utf-8").lower()
                    hits = sum(1 for w in query_words if w in content)
                    if hits > max_hits:
                        max_hits = hits
                        best_match = str(f)
                except:
                    continue
        
        # Threshold: At least 1 keyword match
        return best_match if max_hits > 0 else None

    def perform_search(self, topic: str) -> str:
        """
        Executes Google Search via Gemini Grounding and saves the result.
        Returns the path to the saved research file.
        """
        if not self.client:
            print("⚠️ [Research] AI Client offline. Cannot search.")
            return None

        print(f"🕵️ [Research] Searching web for: '{topic}'...")
        
        # Use Gemini with Google Search Tool
        prompt = f"""
        Research the following topic thoroughly:
        Topic: "{topic}"

        Provide a comprehensive technical summary including:
        1. Key Concepts / Architecture
        2. Best Practices / Implementation Steps
        3. Code Snippets (if applicable) 
        
        Format as Markdown.
        """
        
        try:
            # Enable Google Search Tool with latest model
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type="text/plain"
                )
            )
            
            content = response.text
            
            # Save to file
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '_')).replace(' ', '_')
            filename = f"auto_research_{safe_topic}_{datetime.now().strftime('%H%M')}.md"
            save_path = self.memory_path / "devtool" / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(f"# Auto-Research: {topic}\n**Date**: {datetime.now()}\n\n{content}")
            
            print(f"✅ [Research] Knowledge acquired: {save_path.name}")
            return str(save_path)

        except Exception as e:
            print(f"❌ [Research] Search failed: {e}")
            return None

import datetime
from datetime import datetime