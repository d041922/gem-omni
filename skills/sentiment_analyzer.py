"""
News Sentiment Analysis Module
Analyzes news sentiment using yfinance + Gemini API
"""
import yfinance as yf
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from google import genai


def fetch_news_headlines(ticker: str, max_items: int = 10) -> List[Dict[str, str]]:
    """
    Fetch recent news headlines from yfinance

    Args:
        ticker: Stock ticker symbol
        max_items: Maximum number of news items to fetch

    Returns:
        List of news items with title, publisher, and link
    """
    try:
        stock = yf.Ticker(ticker.upper())
        news = stock.news

        if not news:
            return []

        # Extract relevant fields
        headlines = []
        for item in news[:max_items]:
            headlines.append({
                "title": item.get("title", ""),
                "publisher": item.get("publisher", "Unknown"),
                "link": item.get("link", ""),
                "published": datetime.fromtimestamp(
                    item.get("providerPublishTime", 0)
                ).strftime("%Y-%m-%d %H:%M")
            })

        return headlines

    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []


def analyze_sentiment_with_gemini(headlines: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Analyze sentiment of news headlines using Gemini API

    Args:
        headlines: List of news items with title and publisher

    Returns:
        Dictionary with sentiment scores and analysis
    """
    if not headlines:
        return {
            "positive": 0,
            "neutral": 100,
            "negative": 0,
            "overall": "중립",
            "confidence": "낮음",
            "summary": "뉴스 없음"
        }

    # Prepare headlines text
    headlines_text = "\n".join([
        f"{i+1}. [{item['publisher']}] {item['title']}"
        for i, item in enumerate(headlines)
    ])

    # Sentiment analysis prompt
    prompt = f"""다음 뉴스 헤드라인들을 분석하여 전체적인 시장 심리를 평가하세요.

뉴스 헤드라인:
{headlines_text}

분석 요구사항:
1. 각 헤드라인의 감성 (긍정/중립/부정) 판단
2. 전체 긍정/중립/부정 비율 계산
3. 종합 평가 (긍정적/중립적/부정적)
4. 신뢰도 (높음/보통/낮음)
5. 한 줄 요약

출력 형식 (JSON):
{{
    "positive": 숫자 (0-100),
    "neutral": 숫자 (0-100),
    "negative": 숫자 (0-100),
    "overall": "긍정적" 또는 "중립적" 또는 "부정적",
    "confidence": "높음" 또는 "보통" 또는 "낮음",
    "summary": "한 줄 요약 (30자 이내)"
}}

JSON만 출력하세요. 다른 설명은 불필요합니다."""

    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )

        # Parse JSON response
        import json
        result_text = response.text.strip()

        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        result = json.loads(result_text)

        # Validate and normalize
        result["positive"] = min(100, max(0, result.get("positive", 0)))
        result["neutral"] = min(100, max(0, result.get("neutral", 0)))
        result["negative"] = min(100, max(0, result.get("negative", 0)))

        # Normalize to sum 100
        total = result["positive"] + result["neutral"] + result["negative"]
        if total > 0:
            result["positive"] = round(result["positive"] / total * 100, 1)
            result["neutral"] = round(result["neutral"] / total * 100, 1)
            result["negative"] = round(result["negative"] / total * 100, 1)

        return result

    except Exception as e:
        print(f"Error analyzing sentiment with Gemini: {e}")
        return {
            "positive": 33,
            "neutral": 34,
            "negative": 33,
            "overall": "중립",
            "confidence": "낮음",
            "summary": "분석 실패"
        }


def get_news_sentiment(ticker: str, max_items: int = 10) -> Dict[str, Any]:
    """
    Complete news sentiment analysis for a stock

    Args:
        ticker: Stock ticker symbol
        max_items: Maximum number of news items to analyze

    Returns:
        Dictionary with news headlines and sentiment analysis
    """
    # 1. Fetch news headlines
    headlines = fetch_news_headlines(ticker, max_items)

    # 2. Analyze sentiment
    sentiment = analyze_sentiment_with_gemini(headlines)

    # 3. Return combined result
    return {
        "ticker": ticker.upper(),
        "news_count": len(headlines),
        "headlines": headlines[:5],  # Return top 5 for display
        "sentiment": sentiment
    }
