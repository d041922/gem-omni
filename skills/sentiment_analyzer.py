"""
Advanced Sentiment & News Intelligence [GEM: OMNI]
Handles news extraction and Gemini-based translation.
"""
import os
from typing import Dict, List, Any
import logging
from google import genai

logging.getLogger('google_genai').setLevel(logging.ERROR)

def get_news_sentiment(ticker: str, max_items: int = 5) -> Dict[str, Any]:
    """Fetch raw news headlines from yfinance (stable path)"""
    import yfinance as yf
    try:
        stock = yf.Ticker(ticker)
        raw_news = stock.news
        headlines = []
        for item in raw_news[:
            max_items]:
            content = item.get("content", item)
            provider = content.get("provider", {})
            headlines.append({
                "title": content.get("title", ""),
                "publisher": provider.get("displayName", content.get("publisher", "Unknown")),
                "link": content.get("canonicalUrl", {}).get("url", content.get("link", "")),
                "published": content.get("pubDate", "").replace('T', ' ').replace('Z', '')
            })
        return {"ticker": ticker, "headlines": headlines}
    except Exception:
        return {"ticker": ticker, "headlines": []}

def translate_headlines(headlines: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Gemini-powered Korean translation for stock news"""
    if not headlines:
        return []
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        text = "\n".join([f"{i}. {h['title']}" for i, h in enumerate(headlines)])
        prompt = f"Translate these stock news titles into natural Korean. Return only the list of translated titles:\n\n{text}"
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        lines = [line.split('. ', 1)[-1].strip() for line in res.text.strip().split('\n') if line.strip()]
        for i, h in enumerate(headlines):
            h['title_ko'] = lines[i] if i < len(lines) else h['title']
    except Exception:
        for h in headlines:
            h['title_ko'] = h['title']
    return headlines
