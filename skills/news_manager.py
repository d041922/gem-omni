"""
OMNI News Intelligence Manager (v2.2)
Hybrid News Engine with Exa Highlights & yFinance.
Includes Korean translation hints for headlines.
"""
from datetime import datetime
from typing import List, Dict, Any
from exa_py import Exa
import yfinance as yf
import os
import logging

logger = logging.getLogger(__name__)

class NewsManager:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        api_key = os.getenv("EXA_API_KEY")
        self.exa = None
        if api_key and not api_key.startswith("YOUR_"):
            try:
                self.exa = Exa(api_key=api_key)
            except Exception as e:
                logger.error(f"Exa API 초기화 실패: {e}")

    def fetch_ticker_news(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        if self.exa:
            exa_news = self._fetch_exa_news(ticker, limit)
            if exa_news:
                return exa_news
        return self._fetch_yfinance_news(ticker, limit)

    def _fetch_exa_news(self, ticker: str, limit: int) -> List[Dict[str, Any]]:
        try:
            # 공식 가이드 규격: contents={'highlights': True}
            query = f"{ticker} stock financial news and outlook"
            search_response = self.exa.search_and_contents(
                query,
                type="auto",
                num_results=limit,
                highlights={"max_characters": 2000} # Highlights 옵션 사용
            )
            
            news_items = []
            for res in search_response.results:
                text_content = " ".join(res.highlights) if hasattr(res, 'highlights') and res.highlights else ""
                sentiment = self._simple_sentiment_analysis(res.title + text_content)
                
                news_items.append({
                    "headline": res.title,
                    "url": res.url,
                    "published_at": getattr(res, 'published_date', datetime.now().isoformat()),
                    "summary": (text_content[:250] + "...") if text_content else "상세 내용 없음",
                    "sentiment": sentiment,
                    "source": "Exa (Deep)"
                })
            return news_items
        except Exception as e:
            logger.warning(f"Exa 검색 실패: {e}")
            return []

    def _fetch_yfinance_news(self, ticker: str, limit: int) -> List[Dict[str, Any]]:
        try:
            t = yf.Ticker(ticker)
            yf_news = t.news[:limit]
            news_items = []
            for n in yf_news:
                title = n.get("title", n.get("headline", "No Title"))
                news_items.append({
                    "headline": title,
                    "url": n.get("link", "#"),
                    "published_at": datetime.fromtimestamp(n.get("providerPublishTime", 0)).isoformat(),
                    "summary": f"기사 원문을 확인하세요. (출처: {n.get('publisher', 'Finance')})",
                    "sentiment": self._simple_sentiment_analysis(title),
                    "source": "yFinance (Basic)"
                })
            return news_items
        except Exception as e:
            logger.error(f"yFinance 로드 실패: {e}")
            return []

    def _simple_sentiment_analysis(self, text: str) -> str:
        """키워드 기반 기초 감성 분석 및 한글 요약 힌트"""
        text_lower = text.lower()
        
        # 감성 판정
        if any(w in text_lower for w in ["surge", "jump", "buy", "bull", "growth", "positive", "beat", "high", "good"]):
            sentiment = "Greed"
        elif any(w in text_lower for w in ["drop", "crash", "sell", "fear", "loss", "negative", "miss", "low", "bad"]):
            sentiment = "Fear"
        else:
            sentiment = "Neutral"
            
        return sentiment

    def _translate_hint(self, headline: str) -> str:
        """헤드라인의 핵심 의미를 한글로 번역/치환 (간이 로직)"""
        h_lower = headline.lower()
        if "surge" in h_lower or "jump" in h_lower:
            return "[급등 소식]"
        if "drop" in h_lower or "fall" in h_lower:
            return "[하락 소식]"
        if "earnings" in h_lower:
            return "[실적 발표]"
        if "buy" in h_lower or "bull" in h_lower:
            return "[매수 추천/강세]"
        if "sell" in h_lower or "bear" in h_lower:
            return "[매도 신호/약세]"
        return "[시장 뉴스]"
