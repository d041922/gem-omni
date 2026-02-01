"""
Valuation Engine [Safe Edition]
Strictly data-driven valuation without hardcoded defaults.
All dictionary accesses secured via .get().
"""
import yfinance as yf
from typing import Dict, Tuple

class ValuationEngine:
    def __init__(self):
        self.cyclical_sectors = ['Energy', 'Basic Materials', 'Industrials']

    def calculate_valuation_metrics(self, ticker: str) -> Dict:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info:
                return {'error': 'No info', 'ticker': ticker}
            
            is_korean = ticker.endswith(('.KS', '.KQ'))
            multiples = self._get_multiples_strictly(info)
            profitability = self._get_profitability_strictly(info)
            
            if is_korean:
                try:
                    from skills.kr_market_crawler import get_kr_stock_info
                    kr_data = get_kr_stock_info(ticker)
                    if kr_data:
                        if not multiples.get('pe_ratio'):
                            multiples['pe_ratio'] = kr_data.get('pe_ratio')
                        if not multiples.get('price_to_book'):
                            multiples['price_to_book'] = kr_data.get('price_to_book')
                        if not profitability.get('roe'):
                            profitability['roe'] = kr_data.get('roe')
                except Exception as e:
                    print(f"KR supplement error: {e}")

            has_data = any([multiples.get('pe_ratio'), multiples.get('price_to_book'), info.get('revenueGrowth')])
            if not has_data:
                return {
                    'ticker': ticker, 
                    'status': 'Insufficient Data', 
                    'valuation_score': 0.0, 
                    'assessment': 'unknown'
                }

            style, reason = self._determine_stock_style(info, multiples, profitability)
            
            if style == 'Growth':
                analysis = self._analyze_as_growth(info, multiples, profitability)
            elif style == 'Value':
                analysis = self._analyze_as_value(info, multiples, profitability)
            elif style == 'Cyclical':
                analysis = self._analyze_as_cyclical(stock, info, multiples)
            else:
                analysis = self._analyze_as_hybrid(info, multiples, profitability)

            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'style': style,
                'style_reason': reason,
                'multiples': multiples,
                'profitability': profitability,
                'valuation_score': float(analysis.get('score', 0.0)),
                'assessment': analysis.get('assessment', 'unknown'),
                'summary': analysis.get('summary', '')
            }
        except Exception as e:
            return {'error': str(e), 'ticker': ticker}

    def _get_multiples_strictly(self, info: Dict) -> Dict:
        pe = info.get('trailingPE') or info.get('forwardPE')
        if not pe:
            mcap = info.get('marketCap')
            income = info.get('netIncomeToCommon')
            if mcap and income and income > 0:
                pe = mcap / income
        
        peg = info.get('pegRatio')
        if (peg is None or peg == 0) and pe:
            growth = info.get('earningsQuarterlyGrowth')
            if growth and growth > 0:
                peg = pe / (growth * 100)

        return {
            'pe_ratio': pe if pe else 0.0,
            'peg_ratio': peg if peg else 0.0,
            'price_to_book': info.get('priceToBook', 0.0),
            'price_to_sales': info.get('priceToSalesTrailing12Months', 0.0)
        }

    def _get_profitability_strictly(self, info: Dict) -> Dict:
        return {
            'roe': info.get('returnOnEquity', 0.0) * 100 if info.get('returnOnEquity') else 0.0,
            'net_margin': info.get('profitMargins', 0.0) * 100 if info.get('profitMargins') else 0.0
        }

    def _determine_stock_style(self, info: Dict, multiples: Dict, profit: Dict) -> Tuple[str, str]:
        sector = info.get('sector', '')
        rev_growth = (info.get('revenueGrowth') or 0.0) * 100
        peg = multiples.get('peg_ratio', 0.0)
        pb = multiples.get('price_to_book', 0.0)

        if sector in self.cyclical_sectors:
            return 'Cyclical', f"{sector} 경기 민감주"
        if rev_growth > 15 or (0 < peg < 1.5):
            return 'Growth', "성장주"
        if 0 < pb < 2.5:
            return 'Value', "가치주"
        return 'Hybrid', "일반 종목"

    def _analyze_as_growth(self, info: Dict, multiples: Dict, profit: Dict) -> Dict:
        peg = multiples.get('peg_ratio', 0.0)
        roe = profit.get('roe', 0.0)
        pe = multiples.get('pe_ratio', 0.0)
        score, weights = 0.0, 0
        
        if peg and peg > 0:
            weights += 50
            if peg < 1.0:
                score += 50.0
            elif peg < 1.5:
                score += 30.0
        if roe and roe > 0:
            weights += 30
            if roe > 25:
                score += 30.0
            elif roe > 15:
                score += 15.0
        if pe and pe > 0:
            weights += 20
            if pe < 30:
                score += 20.0
            elif pe < 50:
                score += 10.0

        f_score = (score / weights * 10) if weights > 0 else 0.0
        return {
            'score': round(f_score, 1), 
            'assessment': 'undervalued' if f_score >= 7 else 'fair_value' if f_score >= 4 else 'overvalued', 
            'summary': f"성장주 분석 점수: {f_score:.1f}"
        }

    def _analyze_as_value(self, info: Dict, multiples: Dict, profit: Dict) -> Dict:
        pb = multiples.get('price_to_book', 0.0)
        pe = multiples.get('pe_ratio', 0.0)
        div = (info.get('dividendYield') or 0.0) * 100
        score, weights = 0.0, 0
        
        if pb and pb > 0:
            weights += 40
            if pb < 1.2:
                score += 40.0
            elif pb < 2.0:
                score += 20.0
        if pe and pe > 0:
            weights += 30
            if pe < 12:
                score += 30.0
            elif pe < 18:
                score += 15.0
        if div > 0:
            weights += 30
            if div > 4.0:
                score += 30.0
            elif div > 2.0:
                score += 15.0

        f_score = (score / weights * 10) if weights > 0 else 0.0
        return {
            'score': round(f_score, 1), 
            'assessment': 'undervalued' if f_score >= 7 else 'fair_value', 
            'summary': f"가치주 분석 점수: {f_score:.1f}"
        }

    def _analyze_as_cyclical(self, stock, info: Dict, multiples: Dict) -> Dict:
        try:
            hist = stock.history(period='5y')
            if hist.empty:
                return {'score': 0.0, 'assessment': 'unknown', 'summary': 'No history'}
            pos = hist['Close'].iloc[-1] / hist['Close'].mean()
            pb = multiples.get('price_to_book', 0.0)
            score = (5.0 if pos < 0.8 else 0.0) + (5.0 if 0 < pb < 1.2 else 0.0)
            return {
                'score': score, 
                'assessment': 'undervalued' if score >= 7 else 'fair_value', 
                'summary': f"경기주 분석 점수: {score}"
            }
        except Exception:
            return {'score': 0.0, 'assessment': 'unknown', 'summary': 'Error'}

    def _analyze_as_hybrid(self, info: Dict, multiples: Dict, profit: Dict) -> Dict:
        pe = multiples.get('pe_ratio', 0.0)
        roe = profit.get('roe', 0.0)
        score = (5.0 if 0 < pe < 20 else 0.0) + (5.0 if roe > 15 else 0.0)
        return {
            'score': score, 
            'assessment': 'fair_value' if score >= 5 else 'overvalued', 
            'summary': "하이브리드 분석 완료"
        }

def calculate_valuation_metrics(ticker: str) -> Dict:
    return ValuationEngine().calculate_valuation_metrics(ticker)
