"""
AI-Powered Market Buy Recommendations
Comprehensive analysis: Fundamentals + Technicals + Valuation

NOT just momentum screening - this analyzes:
  - Fundamental strength (earnings, margins, growth)
  - Technical setup (ADX, RSI, trend strength)
  - Valuation (PER, PEG, sector comparison)
  - Portfolio fit (Core/Satellite, sector balance)
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def generate_buy_recommendations(
    screener_data: List[Dict],
    sector_data: Dict,
    user_portfolio: Optional[pd.DataFrame] = None
) -> List[Dict[str, Any]]:
    """
    Generate AI-powered buy recommendations

    Args:
        screener_data: Momentum screening results from MarketScreener
        sector_data: Sector rotation data from SectorAnalyzer
        user_portfolio: User's current portfolio (optional)

    Returns:
        List of recommendations sorted by score:
        [
            {
                'ticker': 'NVDA',
                'name': 'NVIDIA Corporation',
                'signal': 'Strong Buy' | 'Buy' | 'Watch',
                'entry_price': 125.5,
                'target_price': 145.0,
                'risk_level': 'Low' | 'Medium' | 'High',
                'rationale': '...',
                'portfolio_fit': '...',
                'score': 8.5  # 0-10
            }
        ]
    """
    recommendations = []

    # Get top momentum stocks
    candidates = screener_data[:20]  # Top 20 from momentum screening

    for stock in candidates:
        ticker = stock['ticker']

        # Analyze comprehensively
        analysis = analyze_stock_comprehensive(ticker, stock, sector_data, user_portfolio)

        if analysis and analysis['score'] >= 6.0:  # Minimum threshold
            recommendations.append(analysis)

    # Sort by score
    recommendations.sort(key=lambda x: -x['score'])

    return recommendations[:10]  # Top 10


def analyze_stock_comprehensive(
    ticker: str,
    momentum_data: Dict,
    sector_data: Dict,
    user_portfolio: Optional[pd.DataFrame]
) -> Optional[Dict[str, Any]]:
    """
    Comprehensive stock analysis combining multiple factors

    Returns None if analysis fails or stock doesn't meet criteria
    """
    try:
        # Fetch stock data
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period='3mo')

        if hist.empty or len(hist) < 20:
            return None

        # Calculate current price
        current_price = hist['Close'].iloc[-1]

        # --- 1. Fundamental Analysis (40% weight) ---
        fundamental_score = analyze_fundamentals(info)

        # --- 2. Technical Analysis (30% weight) ---
        technical_score = analyze_technicals(hist, momentum_data)

        # --- 3. Valuation Analysis (20% weight) ---
        valuation_score = analyze_valuation(info)

        # --- 4. Portfolio Fit Analysis (10% weight) ---
        portfolio_score = analyze_portfolio_fit(ticker, info, sector_data, user_portfolio)

        # --- Weighted Total Score ---
        total_score = (
            fundamental_score * 0.4 +
            technical_score * 0.3 +
            valuation_score * 0.2 +
            portfolio_score * 0.1
        )

        # Determine signal
        if total_score >= 8.0:
            signal = 'Strong Buy'
        elif total_score >= 7.0:
            signal = 'Buy'
        else:
            signal = 'Watch'

        # Calculate target price (simple: +15% for Strong Buy, +10% for Buy)
        upside_pct = 0.15 if signal == 'Strong Buy' else 0.10
        target_price = current_price * (1 + upside_pct)

        # Risk level
        beta = info.get('beta', 1.0)
        if beta > 1.5:
            risk_level = 'High'
        elif beta > 1.0:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        # Generate rationale
        rationale = generate_rationale(info, fundamental_score, technical_score, valuation_score)

        # Portfolio fit explanation
        portfolio_fit = generate_portfolio_fit(ticker, info, sector_data, user_portfolio, portfolio_score)

        return {
            'ticker': ticker,
            'name': info.get('longName', ticker),
            'signal': signal,
            'entry_price': current_price,
            'target_price': target_price,
            'risk_level': risk_level,
            'rationale': rationale,
            'portfolio_fit': portfolio_fit,
            'score': total_score,
            'fundamental_score': fundamental_score,
            'technical_score': technical_score,
            'valuation_score': valuation_score,
            'portfolio_score': portfolio_score
        }

    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None


def analyze_fundamentals(info: Dict) -> float:
    """
    Analyze fundamental strength (0-10 score)

    Factors:
    - Revenue growth
    - Profit margins
    - ROE
    - Debt levels
    """
    score = 5.0  # Neutral base

    # Revenue growth (YoY)
    revenue_growth = info.get('revenueGrowth', 0)
    if revenue_growth > 0.20:  # >20% growth
        score += 1.5
    elif revenue_growth > 0.10:  # >10% growth
        score += 1.0
    elif revenue_growth < 0:  # Declining
        score -= 1.0

    # Profit margins
    net_margin = info.get('profitMargins', 0)
    if net_margin > 0.20:  # >20% margin
        score += 1.5
    elif net_margin > 0.10:  # >10% margin
        score += 1.0
    elif net_margin < 0:  # Unprofitable
        score -= 1.5

    # ROE (Return on Equity)
    roe = info.get('returnOnEquity', 0)
    if roe > 0.20:  # >20% ROE
        score += 1.0
    elif roe > 0.15:  # >15% ROE
        score += 0.5

    # Debt to Equity
    debt_to_equity = info.get('debtToEquity', 100)
    if debt_to_equity < 30:  # Low debt
        score += 0.5
    elif debt_to_equity > 100:  # High debt
        score -= 0.5

    return max(0, min(10, score))


def analyze_technicals(hist: pd.DataFrame, momentum_data: Dict) -> float:
    """
    Analyze technical strength (0-10 score)

    Factors:
    - ADX (trend strength)
    - RSI (momentum)
    - Moving average cross
    - Volume surge
    """
    score = 5.0  # Neutral base

    # RSI from momentum data
    rsi = momentum_data.get('rsi', 50)
    if 40 <= rsi <= 60:  # Healthy momentum
        score += 1.5
    elif rsi > 70:  # Overbought
        score -= 1.0
    elif rsi < 30:  # Oversold (opportunity)
        score += 1.0

    # ADX (trend strength) - calculated from momentum_data if available
    # For simplicity, we'll use moving average cross as proxy
    if len(hist) >= 60:
        ma20 = hist['Close'].rolling(20).mean().iloc[-1]
        ma60 = hist['Close'].rolling(60).mean().iloc[-1]
        current_price = hist['Close'].iloc[-1]

        # Golden cross
        if ma20 > ma60 and current_price > ma20:
            score += 2.0
        # Death cross
        elif ma20 < ma60:
            score -= 1.0

    # Volume surge
    volume_surge = momentum_data.get('volume_surge', 1.0)
    if volume_surge > 2.0:  # 2x volume
        score += 1.0
    elif volume_surge > 1.5:  # 1.5x volume
        score += 0.5

    # Price momentum (1M)
    if len(hist) >= 20:
        price_1m_ago = hist['Close'].iloc[-20]
        price_change = (hist['Close'].iloc[-1] - price_1m_ago) / price_1m_ago
        if price_change > 0.10:  # >10% gain
            score += 1.0
        elif price_change > 0.05:  # >5% gain
            score += 0.5
        elif price_change < -0.10:  # >10% loss
            score -= 1.0

    return max(0, min(10, score))


def analyze_valuation(info: Dict) -> float:
    """
    Analyze valuation (0-10 score)

    Factors:
    - PER
    - PEG ratio
    - Price to Sales
    """
    score = 5.0  # Neutral base

    # PER (P/E ratio)
    pe = info.get('trailingPE', 999)
    if pe < 15:  # Cheap
        score += 2.0
    elif pe < 25:  # Fair
        score += 1.0
    elif pe > 50:  # Expensive
        score -= 1.5

    # PEG ratio (best valuation metric)
    peg = info.get('pegRatio', None)
    if peg and peg > 0:
        if peg < 1.0:  # Undervalued
            score += 2.0
        elif peg < 1.5:  # Fair
            score += 1.0
        elif peg > 2.5:  # Overvalued
            score -= 1.5

    # Price to Sales
    ps = info.get('priceToSalesTrailing12Months', 999)
    if ps < 2:  # Cheap
        score += 1.0
    elif ps > 10:  # Expensive
        score -= 1.0

    return max(0, min(10, score))


def analyze_portfolio_fit(
    ticker: str,
    info: Dict,
    sector_data: Dict,
    user_portfolio: Optional[pd.DataFrame]
) -> float:
    """
    Analyze portfolio fit (0-10 score)

    Factors:
    - Sector momentum (from sector_data)
    - Diversification benefit
    - Position size risk
    """
    score = 5.0  # Neutral base

    # Sector momentum
    sector = info.get('sector', 'Unknown')
    leading_sectors = [s['name'] for s in sector_data.get('leading_sectors', [])]

    if sector in leading_sectors:
        score += 2.0  # Hot sector
    elif sector in [s['name'] for s in sector_data.get('lagging_sectors', [])]:
        score -= 1.0  # Weak sector

    # Check if already in portfolio
    if user_portfolio is not None and not user_portfolio.empty:
        # Check if ticker exists
        ticker_cols = ['종목코드', '티커코드', 'ticker']
        ticker_col = None
        for col in ticker_cols:
            if col in user_portfolio.columns:
                ticker_col = col
                break

        if ticker_col:
            existing = user_portfolio[user_portfolio[ticker_col].str.upper() == ticker.upper()]
            if not existing.empty:
                score -= 2.0  # Already holding (diversification penalty)

        # Sector concentration check
        if '카테고리' in user_portfolio.columns and '평가금액(KRW)' in user_portfolio.columns:
            total_value = user_portfolio['평가금액(KRW)'].sum()
            sector_value = user_portfolio[user_portfolio['카테고리'].str.contains(sector, na=False)]['평가금액(KRW)'].sum()
            sector_pct = (sector_value / total_value * 100) if total_value > 0 else 0

            if sector_pct > 40:  # Sector already concentrated
                score -= 1.5

    return max(0, min(10, score))


def generate_rationale(info: Dict, fund_score: float, tech_score: float, val_score: float) -> str:
    """Generate investment rationale text"""
    rationale_parts = []

    # Fundamentals
    if fund_score >= 7.5:
        revenue_growth = info.get('revenueGrowth', 0) * 100
        rationale_parts.append(f"✅ 강력한 펀더멘털 (매출 성장 {revenue_growth:.1f}%, 높은 마진율)")
    elif fund_score < 5.0:
        rationale_parts.append("⚠️ 펀더멘털 약화 우려")

    # Technicals
    if tech_score >= 7.5:
        rationale_parts.append("✅ 강한 추세 (골든크로스, 거래량 증가)")
    elif tech_score < 5.0:
        rationale_parts.append("⚠️ 기술적 약세 (추세 불명확)")

    # Valuation
    if val_score >= 7.5:
        peg = info.get('pegRatio', None)
        if peg and peg < 1.0:
            rationale_parts.append(f"✅ 저평가 (PEG {peg:.2f})")
    elif val_score < 5.0:
        rationale_parts.append("⚠️ 밸류에이션 부담")

    # Company info
    sector = info.get('sector', 'Unknown')
    market_cap_b = info.get('marketCap', 0) / 1e9
    rationale_parts.append(f"📊 {sector} 섹터, 시총 ${market_cap_b:.1f}B")

    return " | ".join(rationale_parts)


def generate_portfolio_fit(
    ticker: str,
    info: Dict,
    sector_data: Dict,
    user_portfolio: Optional[pd.DataFrame],
    portfolio_score: float
) -> str:
    """Generate portfolio fit explanation"""
    from skills.asset_classifier import classify_asset

    sector = info.get('sector', 'Unknown')
    asset_type = classify_asset(ticker, sector, info.get('longName', ''))

    fit_parts = []

    # Asset type
    if asset_type == 'Core':
        fit_parts.append("📊 Core 자산 (방어적 포지션)")
    else:
        fit_parts.append("🚀 Satellite 자산 (공격적 포지션)")

    # Sector fit
    leading_sectors = [s['name'] for s in sector_data.get('leading_sectors', [])]
    if sector in leading_sectors:
        fit_parts.append(f"✅ {sector} 섹터 강세")

    # Already holding check
    if user_portfolio is not None and not user_portfolio.empty:
        ticker_cols = ['종목코드', '티커코드', 'ticker']
        ticker_col = None
        for col in ticker_cols:
            if col in user_portfolio.columns:
                ticker_col = col
                break

        if ticker_col:
            existing = user_portfolio[user_portfolio[ticker_col].str.upper() == ticker.upper()]
            if not existing.empty:
                fit_parts.append("⚠️ 이미 보유 중 (추가 매수 신중)")
            else:
                fit_parts.append("✅ 신규 매수 가능 (분산 효과)")

    # Suggested allocation
    if asset_type == 'Core':
        fit_parts.append("권장 비중: 포트폴리오의 5-10%")
    else:
        fit_parts.append("권장 비중: Satellite 내 최대 10%")

    return " | ".join(fit_parts)


# Example usage
if __name__ == '__main__':
    # Test with sample data
    sample_screener = [
        {'ticker': 'NVDA', 'name': 'NVIDIA', 'rsi': 65, 'volume_surge': 1.8},
        {'ticker': 'AAPL', 'name': 'Apple', 'rsi': 55, 'volume_surge': 1.2},
    ]

    sample_sector = {
        'leading_sectors': [{'name': 'Technology', 'momentum_score': 8}],
        'neutral_sectors': [],
        'lagging_sectors': []
    }

    recommendations = generate_buy_recommendations(sample_screener, sample_sector, None)

    print("=== AI Buy Recommendations ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['ticker']} - {rec['signal']} (Score: {rec['score']:.1f})")
        print(f"   Entry: ${rec['entry_price']:.2f} → Target: ${rec['target_price']:.2f}")
        print(f"   {rec['rationale']}")
