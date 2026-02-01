"""
Earnings Analyzer [Safe Edition]
Handles financial trends with robust data validation and safe accesses.
"""
import yfinance as yf
from typing import Dict

class EarningsAnalyzer:
    def analyze_earnings_trend(self, ticker: str) -> Dict:
        try:
            stock = yf.Ticker(ticker)
            rev_trend = self._analyze_revenue_trend(stock)
            earn_trend = self._analyze_earnings_trend(stock)
            margin_anal = self._analyze_margins(stock)
            surprise_anal = self._analyze_surprises(stock)
            
            score = self._calculate_quality_score(rev_trend, earn_trend, margin_anal, surprise_anal)
            
            raw_history = []
            income_stmt = stock.quarterly_income_stmt
            if not income_stmt.empty:
                for date in income_stmt.columns:
                    raw_history.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'revenue': float(income_stmt.loc['Total Revenue', date]) if 'Total Revenue' in income_stmt.index else 0.0,
                        'net_income': float(income_stmt.loc['Net Income', date]) if 'Net Income' in income_stmt.index else 0.0,
                        'op_income': float(income_stmt.loc['Operating Income', date]) if 'Operating Income' in income_stmt.index else 0.0
                    })
                raw_history.sort(key=lambda x: x.get('date', ''))

            return {
                "ticker": ticker, "revenue_trend": rev_trend, "earnings_trend": earn_trend,
                "margin_analysis": margin_anal, "surprise_analysis": surprise_anal,
                "quality_score": float(score), "raw_history": raw_history
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e)}

    def _analyze_revenue_trend(self, stock) -> Dict:
        try:
            q = stock.quarterly_financials
            if q.empty:
                return {'error': 'No data'}
            row_idx = next((i for i in q.index if 'Total Revenue' in str(i) or 'Revenue' in str(i)), None)
            if not row_idx:
                return {'error': 'No revenue row'}
            revs = q.loc[row_idx].head(4).tolist()[::-1]
            if len(revs) < 2:
                return {'error': 'Short data'}
            qoq = [round(((revs[i]-revs[i-1])/revs[i-1]*100), 1) for i in range(1, len(revs)) if revs[i-1]!=0]
            return {'direction': 'accelerating' if len(qoq)>1 and qoq[-1]>qoq[-2] else 'stable', 'qoq_growth': qoq}
        except Exception:
             return {'error': 'Fail'}

    def _analyze_earnings_trend(self, stock) -> Dict:
        try:
            q = stock.quarterly_financials
            row_idx = next((i for i in q.index if 'Net Income' in str(i)), None)
            if not row_idx:
                return {'error': 'No net income'}
            nets = q.loc[row_idx].head(4).tolist()[::-1]
            qoq = [round(((nets[i]-nets[i-1])/abs(nets[i-1])*100), 1) for i in range(1, len(nets)) if nets[i-1]!=0]
            return {'direction': 'stable', 'qoq_growth': qoq}
        except Exception:
             return {'error': 'Fail'}

    def _analyze_margins(self, stock) -> Dict:
        try:
            q = stock.quarterly_financials
            rev_idx = next((i for i in q.index if 'Total Revenue' in str(i) or 'Revenue' in str(i)), None)
            net_idx = next((i for i in q.index if 'Net Income' in str(i)), None)
            if not rev_idx or not net_idx:
                return {'error': 'Missing rows'}
            revs, nets = q.loc[rev_idx].head(4).tolist()[::-1], q.loc[net_idx].head(4).tolist()[::-1]
            margins = [round((n/r*100), 1) for n, r in zip(nets, revs) if r!=0]
            return {'net_margin': margins, 'trend': 'improving' if len(margins)>1 and margins[-1]>margins[0] else 'stable'}
        except Exception:
             return {'error': 'Fail'}

    def _analyze_surprises(self, stock) -> Dict:
        return {'consistency': 'unknown'}

    def _calculate_quality_score(self, r, e, m, s) -> float:
        score = 5.0
        if r.get('direction') == 'accelerating':
            score += 2.0
        if m.get('trend') == 'improving':
            score += 1.0
        return min(score, 10.0)
