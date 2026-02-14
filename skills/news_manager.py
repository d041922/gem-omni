"""OMNI News Intelligence Manager."""

from datetime import datetime
import logging
import os
from typing import Any, Dict, List

import yfinance as yf

logger = logging.getLogger(__name__)

try:
    from exa_py import Exa  # type: ignore
except Exception:  # pragma: no cover
    Exa = None


class NewsManager:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.exa = None
        api_key = os.getenv("EXA_API_KEY")
        if Exa and api_key and not api_key.startswith("YOUR_"):
            try:
                self.exa = Exa(api_key=api_key)
            except Exception as e:
                logger.error("Exa init failed: %s", e)

    def fetch_ticker_news(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        if self.exa:
            items = self._fetch_exa_news(ticker, limit)
            if items:
                return items
        return self._fetch_yfinance_news(ticker, limit)

    def _fetch_exa_news(self, ticker: str, limit: int) -> List[Dict[str, Any]]:
        if not self.exa:
            return []
        try:
            query = f"{ticker} stock financial news and outlook"
            response = self.exa.search_and_contents(
                query,
                type="auto",
                num_results=limit,
                highlights={"max_characters": 2000},
            )
            news_items = []
            for res in response.results:
                highlights = getattr(res, "highlights", None) or []
                text_content = " ".join(highlights)
                sentiment = self._simple_sentiment_analysis(f"{res.title} {text_content}")
                news_items.append(
                    {
                        "headline": res.title,
                        "url": res.url,
                        "published_at": getattr(res, "published_date", datetime.now().isoformat()),
                        "summary": (text_content[:250] + "...") if text_content else "No summary",
                        "sentiment": sentiment,
                        "source": "Exa",
                    }
                )
            return news_items
        except Exception as e:
            logger.warning("Exa fetch failed: %s", e)
            return []

    def _fetch_yfinance_news(self, ticker: str, limit: int) -> List[Dict[str, Any]]:
        try:
            t = yf.Ticker(ticker)
            yf_news = t.news[:limit]
            news_items = []
            for n in yf_news:
                title = n.get("title", n.get("headline", "No Title"))
                published = n.get("providerPublishTime", 0)
                news_items.append(
                    {
                        "headline": title,
                        "url": n.get("link", "#"),
                        "published_at": datetime.fromtimestamp(published).isoformat() if published else datetime.now().isoformat(),
                        "summary": f"Publisher: {n.get('publisher', 'Finance')}",
                        "sentiment": self._simple_sentiment_analysis(title),
                        "source": "yFinance",
                    }
                )
            return news_items
        except Exception as e:
            logger.error("yFinance fetch failed: %s", e)
            return []

    def _simple_sentiment_analysis(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["surge", "jump", "buy", "bull", "growth", "positive", "beat", "high", "good"]):
            return "Greed"
        if any(w in t for w in ["drop", "crash", "sell", "fear", "loss", "negative", "miss", "low", "bad"]):
            return "Fear"
        return "Neutral"
