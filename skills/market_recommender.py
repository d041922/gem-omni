"""
AI-Powered Market Buy Recommendations [Safe Edition]
Comprehensive analysis: Fundamentals + Technicals + Valuation.
Strictly uses .get() for all dictionary and dataframe accesses.
"""
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from skills.asset_classifier import AssetClassifier

def generate_buy_recommendations(
    screener_data: List[Dict],
    sector_data: Dict,
    user_portfolio: Optional[pd.DataFrame] = None
) -> List[Dict[str, Any]]:
    recommendations = []
    candidates = screener_data[:20] if screener_data else []

    for stock in candidates:
        ticker = stock.get('ticker')
        if not ticker:
            continue
        analysis = analyze_stock_comprehensive(ticker, stock, sector_data, user_portfolio)
        if analysis and analysis.get('score', 0) >= 6.0:
            recommendations.append(analysis)

    recommendations.sort(key=lambda x: -x.get('score', 0))
    return recommendations[:10]

def analyze_stock_comprehensive(
    ticker: str,
    momentum_data: Dict,
    sector_data: Dict,
    user_portfolio: Optional[pd.DataFrame]
) -> Optional[Dict[str, Any]]:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            return None
        hist = stock.history(period='3mo')
        if hist.empty or len(hist) < 20:
            return None

        current_price = float(hist['Close'].iloc[-1])
        f_score = analyze_fundamentals(info)
        t_score = analyze_technicals(hist, momentum_data)
        v_score = analyze_valuation(info)
        p_score = analyze_portfolio_fit(ticker, info, sector_data, user_portfolio)

        total_score = (f_score * 0.4 + t_score * 0.3 + v_score * 0.2 + p_score * 0.1)
        signal = 'Strong Buy' if total_score >= 8.0 else 'Buy' if total_score >= 7.0 else 'Watch'
        target_price = current_price * (1.15 if signal == 'Strong Buy' else 1.10)
        
        beta = info.get('beta', 1.0)
        risk = 'High' if beta > 1.5 else 'Medium' if beta > 1.0 else 'Low'

        return {
            'ticker': ticker,
            'name': info.get('longName', ticker),
            'signal': signal,
            'entry_price': current_price,
            'target_price': target_price,
            'risk_level': risk,
            'rationale': generate_rationale(info, f_score, t_score, v_score),
            'portfolio_fit': generate_portfolio_fit(ticker, info, sector_data, user_portfolio, p_score),
            'score': float(total_score)
        }
    except Exception as e:
        print(f"Error in comprehensive analysis for {ticker}: {e}")
        return None

def analyze_fundamentals(info: Dict) -> float:
    score = 5.0
    rev_growth = info.get('revenueGrowth', 0)
    if rev_growth > 0.20:
        score += 1.5
    elif rev_growth > 0.10:
        score += 1.0
    elif rev_growth < 0:
        score -= 1.0

    net_margin = info.get('profitMargins', 0)
    if net_margin > 0.20:
        score += 1.5
    elif net_margin > 0.10:
        score += 1.0
    elif net_margin < 0:
        score -= 1.5

    roe = info.get('returnOnEquity', 0)
    if roe > 0.20:
        score += 1.0
    elif roe > 0.15:
        score += 0.5

    debt = info.get('debtToEquity', 100)
    if debt < 30:
        score += 0.5
    elif debt > 100:
        score -= 0.5
    return max(0.0, min(10.0, score))

def analyze_technicals(hist: pd.DataFrame, momentum_data: Dict) -> float:
    score = 5.0
    rsi = momentum_data.get('rsi', 50)
    if 40 <= rsi <= 60:
        score += 1.5
    elif rsi > 70:
        score -= 1.0
    elif rsi < 30:
        score += 1.0

    if len(hist) >= 60:
        ma20 = hist['Close'].rolling(20).mean().iloc[-1]
        ma60 = hist['Close'].rolling(60).mean().iloc[-1]
        if ma20 > ma60:
            score += 2.0
        elif ma20 < ma60:
            score -= 1.0

    vol_surge = momentum_data.get('volume_surge', 1.0)
    if vol_surge > 2.0:
        score += 1.0
    elif vol_surge > 1.5:
        score += 0.5
    return max(0.0, min(10.0, score))

def analyze_valuation(info: Dict) -> float:
    score = 5.0
    pe = info.get('trailingPE', 999)
    if pe < 15:
        score += 2.0
    elif pe < 25:
        score += 1.0
    elif pe > 50:
        score -= 1.5

    peg = info.get('pegRatio')
    if peg and peg > 0:
        if peg < 1.0:
            score += 2.0
        elif peg < 1.5:
            score += 1.0
        elif peg > 2.5:
            score -= 1.5
    return max(0.0, min(10.0, score))

def analyze_portfolio_fit(ticker: str, info: Dict, sector_data: Dict, user_portfolio: Optional[pd.DataFrame]) -> float:
    score = 5.0
    sector = info.get('sector', 'Unknown')
    leading = [s.get('name') for s in sector_data.get('leading_sectors', []) if s.get('name')]
    lagging = [s.get('name') for s in sector_data.get('lagging_sectors', []) if s.get('name')]

    if sector in leading:
        score += 2.0
    elif sector in lagging:
        score -= 1.0

    if user_portfolio is not None and not user_portfolio.empty:
        t_cols = [c for c in user_portfolio.columns if c in ['종목코드', '티커코드', 'ticker']]
        if t_cols:
            existing = user_portfolio[user_portfolio[t_cols[0]].astype(str).str.upper() == ticker.upper()]
            if not existing.empty:
                score -= 2.0
    return max(0.0, min(10.0, score))

def generate_rationale(info: Dict, f_score: float, t_score: float, v_score: float) -> str:
    parts = []
    if f_score >= 7.5:
        parts.append(f"✅ 강한 재무 (성장 {info.get('revenueGrowth', 0)*100:.1f}%)")
    if t_score >= 7.5:
        parts.append("✅ 기술적 우위")
    if v_score >= 7.5:
        parts.append(f"✅ 저평가 (PEG {info.get('pegRatio', 0):.2f})")
    return " | ".join(parts) if parts else "중립 의견"

def generate_portfolio_fit(ticker: str, info: Dict, sector_data: Dict, user_portfolio: Optional[pd.DataFrame], p_score: float) -> str:
    classifier = AssetClassifier()
    asset_type = classifier.classify(ticker, info.get('sector', ''), info.get('longName', ''))
    return f"분류: {asset_type} | 스코어: {p_score:.1f}"