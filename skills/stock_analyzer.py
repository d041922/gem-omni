"""
Single Stock Analysis Module - FINAL 무결성 Edition
Correctly imports news/translation logic from sentiment_analyzer.
"""
import os
from typing import Dict, List, Any

# Centralized imports to avoid ImportError
from skills.sentiment_analyzer import get_news_sentiment, translate_headlines

def search_stock_candidates(query: str) -> List[Dict[str, str]]:
    import requests
    from urllib.parse import quote
    query = query.replace('$', '').strip()
    if not query:
        return []
    candidates = []
    common = {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "테슬라": "TSLA", "애플": "AAPL", "엔비디아": "NVDA", "팔란티어": "PLTR"}
    if query in common:
        candidates.append({"symbol": common[query], "name": query, "exchange": "Priority"})
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={quote(query)}&quotesCount=10"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
        if res.get('quotes'):
            for q in res['quotes']:
                if q.get('quoteType') in ['EQUITY', 'ETF']:
                    candidates.append({"symbol": q.get('symbol', ''), "name": q.get('shortname', q.get('longname', '')), "exchange": q.get('exchange', 'Unknown')})
    except Exception as e:
        print(f"Stock search failed: {e}")
    return candidates

def calculate_fair_value_detailed(info: Dict[str, Any]) -> Dict[str, Any]:
    try:
        curr = info.get("currentPrice", info.get("regularMarketPrice", 0))
        target = info.get("targetMeanPrice", 0)
        eps = info.get("trailingEps", 0)
        growth = min(info.get("earningsQuarterlyGrowth", 0.1) * 100, 15)
        comp_a = target if target > 0 else curr * 1.05
        comp_b = eps * (8.5 + 2 * max(growth, 5))
        comp_c = eps * 30 
        fair = (comp_a * 0.5) + (comp_b * 0.25) + (comp_c * 0.25)
        upside = ((fair / curr) - 1) * 100 if curr > 0 else 0
        return {"fair_value": fair, "upside_pct": upside, "status": "저평가" if upside > 15 else "적정" if upside > -5 else "고평가", "components": {"Analyst Consensus": comp_a, "Graham Growth": comp_b, "P/E Multiple": comp_c}}
    except Exception:
         return {"fair_value": 0, "upside_pct": 0, "status": "N/A", "components": {}}

def analyze_stock(ticker: str) -> Dict[str, Any]:
    ticker = ticker.upper().strip()
    from core.data_manager import DataManager
    data_res = DataManager.get_stock_data(ticker, period="2y")
    if not data_res["success"]:
        return {"success": False, "error": data_res["error"]}
    df, info = data_res["history"], data_res["info"]
    latest = df.iloc[-1]
    
    # Use imported news/translation logic
    news_res = get_news_sentiment(ticker, max_items=5)
    headlines = translate_headlines(news_res.get("headlines", []))
    
    from google import genai
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        res = client.models.generate_content(model="gemini-2.0-flash", contents=f"{ticker} SWOT Summary (4 lines only S: W: O: T:)")
        swot = res.text.strip()
    except Exception:
         swot = "S: N/A\nW: N/A\nO: N/A\nT: N/A"

    summary = {
        "ticker": ticker, "name": info.get("longName", ticker),
        "current_price": float(latest['Close']), "price_change_pct": float((latest['Close']-df['Close'].iloc[-2])/df['Close'].iloc[-2]*100),
        "unit": "₩" if info.get("currency") == "KRW" else "$",
        "fair_value": calculate_fair_value_detailed(info), "swot_quick": swot,
        "performance": {"1w": float((latest['Close']/df['Close'].iloc[-6]-1)*100) if len(df)>5 else 0, "1m": float((latest['Close']/df['Close'].iloc[-22]-1)*100) if len(df)>21 else 0, "1y": float((latest['Close']/df['Close'].iloc[-253]-1)*100) if len(df)>252 else 0},
        "indicators": {"rsi": float(latest.get('rsi', 50)), "macd": float(latest.get('macd', 0)), "ma20": float(latest.get('ma20', 0)), "ma200": float(latest.get('ma200', 0))},
        "tech_summary": {"summary": "매수" if latest.get('rsi', 50) < 40 else "매도" if latest.get('rsi', 50) > 60 else "중립", "score": 0},
        "fundamentals": {"pe": info.get("trailingPE", 0), "peg": info.get("pegRatio", 0), "roe": info.get("returnOnEquity", 0)*100, "debt_status": "OK"},
        "analysts": {"target": info.get("targetMeanPrice", 0), "opinion": info.get("recommendationKey", "N/A").upper(), "count": info.get("numberOfAnalystOpinions", 0)},
        "news": headlines, "earnings": []
    }
    return {"success": True, "summary": summary, "data_file": "managed", "dataframe": df}

def generate_ai_analysis(analysis_result: Dict[str, Any]) -> str:
    from google import genai
    s = analysis_result["summary"]
    prompt = f"당신은 마스터의 재정 참모입니다. {s['name']} 데이터를 분석하여 SWOT 및 포트폴리오 전략을 한국어로 보고하세요."
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        return client.models.generate_content(model="gemini-2.0-flash", contents=prompt).text.strip()
    except Exception:
         return "AI 분석 일시적 오류"

def get_technical_insight(summary: Dict[str, Any]) -> str:
    """Helper to format technical analysis from summary"""
    t = summary.get('tech_summary', {})
    i = summary.get('indicators', {})
    return f"{t.get('summary', 'N/A')} (RSI: {i.get('rsi', 0):.1f})"

def get_fundamental_insight(summary: Dict[str, Any]) -> str:
    """Helper to format fundamental analysis from summary"""
    f = summary.get('fundamentals', {})
    fv = summary.get('fair_value', {})
    return f"Valuation: {fv.get('status', 'N/A')} (Upside: {fv.get('upside_pct', 0):.1f}%), P/E: {f.get('pe', 0):.1f}"
