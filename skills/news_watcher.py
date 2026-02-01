"""
News Watcher [Safe Edition]
Monitors news feeds with robust parsing.
"""
from typing import List, Dict

def parse_news_feed(feed_data: List[Dict]) -> List[Dict]:
    results = []
    for item in feed_data:
        # Safe extraction
        results.append({
            "title": item.get("title", "No Title"),
            "url": item.get("link", "#")
        })
    return results