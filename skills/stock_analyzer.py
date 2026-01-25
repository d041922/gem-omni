"""
Single Stock Analysis Module (Token-Optimized)
Provides deep technical and fundamental analysis for individual stocks
"""
import yfinance as yf
import pandas as pd
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from skills.technical_indicators import (
    calculate_ichimoku,
    calculate_bollinger_bands,
    calculate_fibonacci_levels,
    calculate_adx,
    calculate_mfi,
    calculate_parabolic_sar
)
from skills.sentiment_analyzer import get_news_sentiment


def fetch_stock_data(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """
    Fetch stock data from yfinance

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'NVDA')
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        DataFrame with OHLCV data or None if error
    """
    try:
        ticker = ticker.upper().strip()
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty:
            return None

        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators

    Args:
        df: OHLCV DataFrame

    Returns:
        DataFrame with added technical indicators
    """
    if df.empty:
        return df

    # Calculate indicators
    df = calculate_ichimoku(df)
    df = calculate_bollinger_bands(df, window=20)

    # RSI (14-period)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Moving Averages
    df['ma20'] = df['Close'].rolling(window=20).mean()
    df['ma60'] = df['Close'].rolling(window=60).mean()
    df['ma200'] = df['Close'].rolling(window=200).mean()

    # NEW: Advanced Technical Indicators
    df = calculate_adx(df, period=14)  # Trend strength
    df = calculate_mfi(df, period=14)  # Money flow
    df = calculate_parabolic_sar(df)  # Trailing stop

    return df


def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Get fundamental stock information (Enhanced with stability and defaults)
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        # Helper to get numeric with default
        def get_num(key, default=0):
            val = info.get(key)
            return float(val) if val is not None and isinstance(val, (int, float)) else default

        # Basic info
        result = {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": get_num("marketCap"),
            "pe_ratio": get_num("trailingPE", get_num("forwardPE")),
            "forward_pe": get_num("forwardPE", get_num("trailingPE")),
            "price_to_book": get_num("priceToBook"),
            "dividend_yield": get_num("dividendYield") * 100,
            "beta": get_num("beta", 1.0),
            "52week_high": get_num("fiftyTwoWeekHigh"),
            "52week_low": get_num("fiftyTwoWeekLow"),
            "description": info.get("longBusinessSummary", "상세 정보 없음")
        }

        # Growth & PEG Fallback
        revenue_growth = get_num("revenueGrowth") * 100
        earnings_growth = get_num("earningsQuarterlyGrowth") * 100
        if earnings_growth == 0: earnings_growth = 15.0 # Default assumption
        
        peg = info.get("pegRatio")
        if (peg is None or peg == 0) and result["pe_ratio"] > 0:
            peg = result["pe_ratio"] / earnings_growth if earnings_growth > 0 else 0
        
        result["peg_ratio"] = float(peg) if peg else 0
        result["revenue_growth"] = revenue_growth
        result["eps_growth"] = earnings_growth

        # Profitability
        result["roe"] = get_num("returnOnEquity") * 100
        result["operating_margin"] = get_num("operatingMargins") * 100
        result["profit_margin"] = get_num("profitMargins") * 100

        # Financial health
        result["debt_to_equity"] = get_num("debtToEquity")
        result["current_ratio"] = get_num("currentRatio")
        
        # Valuation
        result["ev_to_ebitda"] = get_num("enterpriseToEbitda")
        result["price_to_sales"] = get_num("priceToSalesTrailing12Months")

        return result

    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return {"name": ticker, "error": str(e), "sector": "N/A", "pe_ratio": 0, "peg_ratio": 0}


def analyze_stock(ticker: str, period: str = "1y") -> Dict[str, Any]:
    """
    Complete stock analysis (Token-Optimized)

    Args:
        ticker: Stock ticker symbol
        period: Data period

    Returns:
        Dictionary with analysis results and temp file path
    """
    ticker = ticker.upper().strip()

    # 1. Fetch data
    df = fetch_stock_data(ticker, period)
    if df is None or df.empty:
        return {"success": False, "error": f"No data found for {ticker}"}

    # 2. Calculate technical indicators
    df = calculate_technical_indicators(df)

    # 3. Get stock info
    stock_info = get_stock_info(ticker)

    # 4. Extract latest values (for analysis)
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    # 5. Calculate 52-week range position
    week_52_high = df['High'].tail(252).max()
    week_52_low = df['Low'].tail(252).min()
    current_price = latest['Close']
    position_52w = (current_price - week_52_low) / (week_52_high - week_52_low) * 100

    # 6. Fibonacci levels
    fib_levels = calculate_fibonacci_levels(df, period=120)

    # 7. News sentiment analysis (NEW - Phase 2)
    news_sentiment = get_news_sentiment(ticker, max_items=10)

    # 8. Prepare summary data (Token-Optimized: < 500 tokens)
    summary = {
        "ticker": ticker,
        "name": stock_info.get("name", ticker),
        "current_price": float(current_price),
        "price_change": float(current_price - prev['Close']),
        "price_change_pct": float((current_price - prev['Close']) / prev['Close'] * 100),
        "52week_high": float(week_52_high),
        "52week_low": float(week_52_low),
        "position_52w_pct": float(position_52w),
        "volume": int(latest['Volume']),
        "technical_indicators": {
            "rsi": float(latest.get('rsi', 0)),
            "macd": float(latest.get('macd', 0)),
            "macd_signal": float(latest.get('macd_signal', 0)),
            "ma20": float(latest.get('ma20', 0)),
            "ma60": float(latest.get('ma60', 0)),
            "ma200": float(latest.get('ma200', 0)),
            "bb_upper": float(latest.get('bb_upper', 0)),
            "bb_lower": float(latest.get('bb_lower', 0)),
            "tenkan_sen": float(latest.get('tenkan_sen', 0)),
            "kijun_sen": float(latest.get('kijun_sen', 0)),
            # NEW: Advanced indicators
            "adx": float(latest.get('adx', 0)),
            "mfi": float(latest.get('mfi', 0)),
            "psar": float(latest.get('psar', 0)),
            "psar_trend": int(latest.get('psar_trend', 0))
        },
        "fundamentals": {
            "sector": stock_info.get("sector", "N/A"),
            "industry": stock_info.get("industry", "N/A"),
            "market_cap": stock_info.get("market_cap", 0),
            "pe_ratio": stock_info.get("pe_ratio", 0),
            "beta": stock_info.get("beta", 0),
            # NEW: Profitability (수익성)
            "roe": stock_info.get("roe", 0),
            "operating_margin": stock_info.get("operating_margin", 0),
            "profit_margin": stock_info.get("profit_margin", 0),
            # NEW: Financial Health (재무 건전성)
            "debt_to_equity": stock_info.get("debt_to_equity", 0),
            "current_ratio": stock_info.get("current_ratio", 0),
            # NEW: Growth (성장성)
            "eps_growth": stock_info.get("eps_growth", 0),
            "revenue_growth": stock_info.get("revenue_growth", 0),
            # NEW: Valuation (가치 평가)
            "ev_to_ebitda": stock_info.get("ev_to_ebitda", 0),
            "price_to_book": stock_info.get("price_to_book", 0)
        },
        "fibonacci_levels": fib_levels,
        # NEW: News sentiment (Phase 2)
        "news_sentiment": {
            "news_count": news_sentiment.get("news_count", 0),
            "positive": news_sentiment.get("sentiment", {}).get("positive", 0),
            "neutral": news_sentiment.get("sentiment", {}).get("neutral", 0),
            "negative": news_sentiment.get("sentiment", {}).get("negative", 0),
            "overall": news_sentiment.get("sentiment", {}).get("overall", "중립"),
            "confidence": news_sentiment.get("sentiment", {}).get("confidence", "낮음"),
            "summary": news_sentiment.get("sentiment", {}).get("summary", "")
        }
    }

    # 8. Save full data to temp file (Token Optimization)
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        delete=False,
        suffix='.json',
        encoding='utf-8',
        prefix=f"stock_{ticker}_"
    )

    full_data = {
        "summary": summary,
        "historical_data": df.tail(100).to_dict(orient='records'),  # Last 100 days only
        "stock_info": stock_info,
        "news_sentiment": news_sentiment  # Full news data with headlines
    }

    json.dump(full_data, temp_file, ensure_ascii=False, indent=2)
    temp_file.close()

    return {
        "success": True,
        "ticker": ticker,
        "summary": summary,
        "data_file": temp_file.name,
        "dataframe": df  # For charting
    }


def generate_ai_analysis(analysis_result: Dict[str, Any]) -> str:
    """
    Generate AI-powered stock analysis using Gemini (Style-Aware)
    """
    from google import genai
    import os
    from skills.valuation_engine import calculate_valuation_metrics

    if not analysis_result.get("success"):
        return "분석 실패: 데이터를 가져올 수 없습니다."

    ticker = analysis_result.get("ticker")
    summary = analysis_result.get("summary", {})
    
    # 1. Fetch the new style-aware valuation data
    valuation = calculate_valuation_metrics(ticker)
    style = valuation.get('style', 'Hybrid')
    v_score = valuation.get('valuation_score', 0)
    v_summary = valuation.get('summary', '')

    # 2. Load system prompt
    from pathlib import Path
    prompt_file = Path(__file__).parent.parent / ".claude" / "prompts" / "stock-analyst.md"
    system_prompt = ""
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    
    # 3. Create context-rich user prompt
    tech = summary.get("technical_indicators", {})
    fund = summary.get("fundamentals", {})
    news = summary.get("news_sentiment", {})

    user_prompt = f"""당신은 마스터를 보좌하는 전략 에이전트 [GEM: OMNI]입니다.
종목: {ticker} ({summary.get('name')})
종목 성격: {style} ({valuation.get('style_reason')})
밸류에이션 점수: {v_score}/10 | 결과: {v_summary}

## 분석 데이터 요약
- 현재가: ${summary.get('current_price', 0):.2f} ({summary.get('price_change_pct', 0):+.2f}%)
- 기술적 지표: RSI {tech.get('rsi', 0):.1f}, 추세강도 ADX {tech.get('adx', 0):.1f}, 자금흐름 MFI {tech.get('mfi', 0):.1f}
- 재무 지표: PER {fund.get('pe_ratio', 0):.1f}, PBR {fund.get('price_to_book', 0):.2f}, ROE {fund.get('roe', 0):.1f}%
- 뉴스 심리: {news.get('overall', '중립')} ({news.get('summary', '소식 없음')})

## 리포트 작성 가이드
1. **{style} 관점의 평가**: 이 종목의 성격에 맞는 핵심 지표를 중심으로 현재 주가가 매력적인지 논리적으로 설명하세요.
2. **미래 가치 진단**: 성장주라면 미래 이익 대비 저평가 여부를, 가치주라면 안전마진을 언급하세요.
3. **전략적 제안 (Action)**: '적극 매수', '보유', '비중 축소' 중 하나를 선택하고 구체적인 이유와 목표가를 제시하세요.
4. **마스터를 위한 넛지**: 이 종목을 포트폴리오에 담았을 때의 기대 효과를 한 문장으로 요약하세요.

전문적이고 전략적인 톤(CFA 스타일)으로 한국어로 작성하세요."""

    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"AI 분석 실패: {str(e)}"
