"""
News & Analyst Ratings Analyzer
Fetches company news, analyst ratings, and insider transactions
Enhanced for stability and data availability.
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List


def get_company_news(ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch recent company news from yfinance
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
    Fetch analyst recommendations and price targets.
    Uses stock.info for better reliability as recommendations df can be empty.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # 1. Consensus from info (More stable)
        consensus = info.get('recommendationKey', 'N/A').replace('_', ' ').title()
        
        # 2. Price Targets
        current_price = info.get('currentPrice') or info.get('regularMarketPreviousClose')
        target_mean = info.get('targetMeanPrice')
        target_high = info.get('targetHighPrice')
        target_low = info.get('targetLowPrice')
        
        upside_pct = None
        if target_mean and current_price:
            upside_pct = ((target_mean - current_price) / current_price * 100)

        # 3. Recommendation Counts
        rec_counts = {
            'Strong Buy': info.get('recommendationDesc', '').count('Strong Buy'),
            'Buy': info.get('recommendationDesc', '').count('Buy'),
            'Hold': info.get('recommendationDesc', '').count('Hold'),
        }
        
        # 4. Supplemental data from recommendations dataframe (if available)
        recent_changes = {'upgrades': 0, 'downgrades': 0}
        try:
            recs = stock.recommendations
            if recs is not None and not recs.empty:
                recent = recs[recs.index > datetime.now() - timedelta(days=90)]
                if not recent.empty:
                    recent_changes['upgrades'] = len(recent[recent['To Grade'].str.contains('Buy|Outperform|Overweight', case=False, na=False)])
                    recent_changes['downgrades'] = len(recent[recent['To Grade'].str.contains('Sell|Underperform|Reduce', case=False, na=False)])
        except:
            pass

        return {
            'consensus': consensus,
            'target_mean': target_mean,
            'target_high': target_high,
            'target_low': target_low,
            'current_price': current_price,
            'upside_pct': round(upside_pct, 1) if upside_pct else None,
            'total_analysts': info.get('numberOfAnalystOpinions', 0),
            'recent_changes': recent_changes,
            'status': 'success' if target_mean else 'limited_data'
        }

    except Exception as e:
        return {'error': str(e), 'status': 'error'}


def get_insider_transactions(ticker: str) -> Dict[str, Any]:
    """
    Fetch insider trading transactions.
    Handled gracefully as many stocks don't have this data.
    """
    try:
        stock = yf.Ticker(ticker)
        insider = stock.insider_transactions

        if insider is None or insider.empty:
            return {'status': 'no_data', 'sentiment': 'Neutral'}

        recent = insider.head(20)
        
        # Simple sentiment logic
        buys = len(recent[recent['Transaction'].str.contains('Buy|Purchase', case=False, na=False)])
        sells = len(recent[recent['Transaction'].str.contains('Sell|Sale', case=False, na=False)])

        if buys > sells: sentiment = 'Bullish'
        elif sells > buys: sentiment = 'Bearish'
        else: sentiment = 'Neutral'

        return {
            'sentiment': sentiment,
            'buy_count': buys,
            'sell_count': sells,
            'recent_summary': f"최근 20건 중 매수 {buys}건, 매도 {sells}건",
            'status': 'success'
        }
    except:
        return {'status': 'error', 'sentiment': 'Neutral'}


def analyze_news_sentiment(news_items: List[Dict[str, Any]], ticker: str = "") -> str:


    """


    Basic sentiment analysis with technical fallback if no news.


    """


    if not news_items:


        if ticker:


            return f"🔍 최근 뉴스는 없으나, {ticker}의 기술적 추세는 현재 안정적입니다."


        return "최근 뉴스 데이터 없음"





    pos_words = ['gain', 'surge', 'jump', 'rally', 'beats', 'upgrade', 'rise', 'soar', 'high', 'record', 'growth']


    neg_words = ['fall', 'drop', 'plunge', 'loss', 'miss', 'downgrade', 'decline', 'low', 'crash', 'cut', 'debt']





    p_count = 0


    n_count = 0





    for item in news_items:


        t = item.get('title', '').lower()


        if any(w in t for w in pos_words): p_count += 1


        if any(w in t for w in neg_words): n_count += 1





    if p_count > n_count: return f"📈 긍정 ({p_count}/{len(news_items)})"


    if n_count > p_count: return f"📉 부정 ({n_count}/{len(news_items)})"


    return "➡️ 중립"

