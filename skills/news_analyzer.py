"""
News & Analyst Ratings Analyzer
Fetches company news, analyst ratings, and insider transactions
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List


def get_company_news(ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch recent company news from yfinance

    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of news items to return

    Returns:
        List of news items with title, publisher, link, timestamp
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news

        if not news:
            return []

        # Format news items
        news_items = []
        for item in news[:limit]:
            news_items.append({
                'title': item.get('title', 'N/A'),
                'publisher': item.get('publisher', 'Unknown'),
                'link': item.get('link', ''),
                'timestamp': datetime.fromtimestamp(item.get('providerPublishTime', 0)),
                'thumbnail': item.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '')
            })

        return news_items

    except Exception as e:
        return []


def get_analyst_ratings(ticker: str) -> Dict[str, Any]:
    """
    Fetch analyst recommendations and price targets

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with recommendations, price targets, and upgrades/downgrades
    """
    try:
        stock = yf.Ticker(ticker)

        # Get recommendations
        recommendations = stock.recommendations

        if recommendations is None or recommendations.empty:
            return {'error': 'No analyst data available'}

        # Recent recommendations (last 3 months)
        recent = recommendations[recommendations.index > datetime.now() - timedelta(days=90)]

        if recent.empty:
            recent = recommendations.tail(20)

        # Count recommendations by firm
        firm_counts = recent['Firm'].value_counts().head(10).to_dict()

        # Count recommendation types
        rec_counts = recent['To Grade'].value_counts().to_dict()

        # Get upgrades/downgrades
        upgrades = recent[recent['To Grade'].str.contains('Buy|Outperform|Overweight', case=False, na=False)]
        downgrades = recent[recent['To Grade'].str.contains('Sell|Underperform|Reduce', case=False, na=False)]

        # Calculate consensus
        total = len(recent)
        buy_count = len(upgrades)
        sell_count = len(downgrades)
        hold_count = total - buy_count - sell_count

        buy_pct = (buy_count / total * 100) if total > 0 else 0
        hold_pct = (hold_count / total * 100) if total > 0 else 0
        sell_pct = (sell_count / total * 100) if total > 0 else 0

        consensus = 'Buy' if buy_pct > 50 else 'Hold' if hold_pct > 30 else 'Sell'

        # Get price target (from stock info)
        info = stock.info
        target_high = info.get('targetHighPrice')
        target_low = info.get('targetLowPrice')
        target_mean = info.get('targetMeanPrice')
        current_price = info.get('currentPrice')

        upside_pct = ((target_mean - current_price) / current_price * 100) if target_mean and current_price else None

        return {
            'consensus': consensus,
            'buy_pct': buy_pct,
            'hold_pct': hold_pct,
            'sell_pct': sell_pct,
            'total_analysts': total,
            'target_high': target_high,
            'target_low': target_low,
            'target_mean': target_mean,
            'upside_pct': upside_pct,
            'recent_changes': {
                'upgrades': len(upgrades),
                'downgrades': len(downgrades)
            },
            'top_firms': firm_counts,
            'recommendation_breakdown': rec_counts,
            'last_updated': recent.index.max().strftime('%Y-%m-%d') if not recent.empty else None
        }

    except Exception as e:
        return {'error': str(e)}


def get_insider_transactions(ticker: str) -> Dict[str, Any]:
    """
    Fetch insider trading transactions

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with insider buy/sell activity
    """
    try:
        stock = yf.Ticker(ticker)

        # Get insider transactions
        insider = stock.insider_transactions

        if insider is None or insider.empty:
            return {'error': 'No insider transaction data available'}

        # Recent transactions (last 6 months)
        recent = insider.head(50)  # yfinance returns recent first

        # Separate buys and sells
        buys = recent[recent['Transaction'].str.contains('Buy|Purchase', case=False, na=False)]
        sells = recent[recent['Transaction'].str.contains('Sell|Sale', case=False, na=False)]

        buy_count = len(buys)
        sell_count = len(sells)

        # Calculate transaction values
        buy_value = buys['Value'].sum() if 'Value' in buys.columns else 0
        sell_value = sells['Value'].sum() if 'Value' in sells.columns else 0

        # Sentiment
        if buy_count > sell_count * 2:
            sentiment = 'Bullish'
        elif sell_count > buy_count * 2:
            sentiment = 'Bearish'
        else:
            sentiment = 'Neutral'

        # Top insiders
        top_buyers = buys.groupby('Insider')['Shares'].sum().nlargest(5).to_dict() if not buys.empty else {}
        top_sellers = sells.groupby('Insider')['Shares'].sum().nlargest(5).to_dict() if not sells.empty else {}

        return {
            'sentiment': sentiment,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'buy_value': buy_value,
            'sell_value': sell_value,
            'net_shares': buys['Shares'].sum() - sells['Shares'].sum() if 'Shares' in recent.columns else 0,
            'top_buyers': top_buyers,
            'top_sellers': top_sellers,
            'recent_transactions': recent.head(10).to_dict('records') if not recent.empty else []
        }

    except Exception as e:
        return {'error': str(e)}


def analyze_news_sentiment(news_items: List[Dict[str, Any]]) -> str:
    """
    Basic sentiment analysis from news titles (keyword-based)

    Args:
        news_items: List of news dictionaries

    Returns:
        Sentiment summary string
    """
    if not news_items:
        return "No news available"

    positive_words = ['gain', 'surge', 'jump', 'rally', 'beats', 'upgrade', 'rise', 'soar', 'high', 'record']
    negative_words = ['fall', 'drop', 'plunge', 'loss', 'miss', 'downgrade', 'decline', 'low', 'crash', 'cut']

    positive_count = 0
    negative_count = 0

    for item in news_items:
        title = item.get('title', '').lower()

        for word in positive_words:
            if word in title:
                positive_count += 1
                break

        for word in negative_words:
            if word in title:
                negative_count += 1
                break

    if positive_count > negative_count:
        return f"📈 긍정적 뉴스 ({positive_count}/{len(news_items)})"
    elif negative_count > positive_count:
        return f"📉 부정적 뉴스 ({negative_count}/{len(news_items)})"
    else:
        return f"➡️ 중립적 뉴스"
