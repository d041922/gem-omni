"""
Valuation Engine - 엄격한 데이터 기반 밸류에이션 분석
추측성 기본값이나 평균값을 배제하고, 실제 수집된 팩터 데이터로만 분석함.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Tuple


class ValuationEngine:
    def __init__(self):
        self.cyclical_sectors = ['Energy', 'Basic Materials', 'Industrials']

    def calculate_valuation_metrics(self, ticker: str) -> Dict:
        """종합 밸류에이션 분석"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            is_korean = ticker.endswith(('.KS', '.KQ'))
            
            # 1. 기초 데이터 수집
            multiples = self._get_multiples_strictly(info)
            profitability = self._get_profitability_strictly(info)
            
            # 2. 한국 주식 데이터 보정 (네이버 크롤러 활용)
            if is_korean:
                from skills.kr_market_crawler import get_kr_stock_info
                kr_data = get_kr_stock_info(ticker)
                # yfinance 데이터가 없을 때만 크롤링 데이터로 보완
                if kr_data:
                    if not multiples.get('pe_ratio'): multiples['pe_ratio'] = kr_data.get('pe_ratio')
                    if not multiples.get('price_to_book'): multiples['price_to_book'] = kr_data.get('price_to_book')
                    if not profitability.get('roe'): profitability['roe'] = kr_data.get('roe')

            # 3. 필수 데이터 존재 여부 확인
            has_fundamental_data = any([
                multiples.get('pe_ratio'), 
                multiples.get('price_to_book'), 
                info.get('revenueGrowth')
            ])

            if not has_fundamental_data:
                return {
                    'ticker': ticker,
                    'status': 'Insufficient Data',
                    'summary': f"'{ticker}' 종목은 분석에 필요한 핵심 재무 지표(PER, P/B 등)를 불러올 수 없습니다. (데이터 소스: yfinance)",
                    'valuation_score': 0,
                    'assessment': 'unknown'
                }

            # 3. 종목 스타일 판별 (실제 데이터 기반)
            style, style_reason = self._determine_stock_style(info, multiples, profitability)
            
            # 4. 스타일별 분석 (데이터가 있는 항목만 계산)
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
                'style_reason': style_reason,
                'multiples': multiples,
                'profitability': profitability,
                'style_analysis': analysis,
                'valuation_score': analysis.get('score', 0),
                'assessment': analysis.get('assessment', 'unknown'),
                'summary': analysis.get('summary', '')
            }

        except Exception as e:
            return {'error': str(e), 'ticker': ticker}

    def _get_multiples_strictly(self, info: Dict) -> Dict:
        """실제 공시/시장 데이터만 수집 (추측성 Default 제거 및 PEG 보완)"""
        pe = info.get('trailingPE') or info.get('forwardPE')
        
        # 산술적으로 확실한 경우에만 직접 계산 허용
        if not pe:
            mcap = info.get('marketCap')
            income = info.get('netIncomeToCommon')
            if mcap and income and income > 0:
                pe = mcap / income # 공식: 시가총액 / 순이익
        
        # PEG 보완 계산
        peg = info.get('pegRatio')
        if (peg is None or peg == 0) and pe:
            growth = info.get('earningsQuarterlyGrowth')
            if growth and growth > 0:
                peg = pe / (growth * 100) # growth는 0.15 형태이므로 100 곱함

        return {
            'pe_ratio': pe,
            'peg_ratio': peg,
            'price_to_book': info.get('priceToBook'),
            'price_to_sales': info.get('priceToSalesTrailing12Months')
        }

    def _get_profitability_strictly(self, info: Dict) -> Dict:
        return {
            'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
            'net_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None
        }

    def _determine_stock_style(self, info: Dict, multiples: Dict, profit: Dict) -> Tuple[str, str]:
        sector = info.get('sector', '')
        revenue_growth = (info.get('revenueGrowth') or 0) * 100
        peg = multiples.get('peg_ratio')
        pb = multiples.get('price_to_book')
        roe = profit.get('roe')

        if sector in self.cyclical_sectors:
            return 'Cyclical', f"{sector} 섹터 기반 경기 민감주"

        # 데이터가 있는 경우에만 성장주 판별
        if revenue_growth > 15 or (peg and peg < 1.5):
            return 'Growth', "높은 성장성 지표 기반 성장주"

        if pb and pb < 2.5:
            return 'Value', "자산 가치(P/B) 기반 가치주"

        return 'Hybrid', "복합적 지표를 가진 일반 종목"

    def _analyze_as_growth(self, info: Dict, multiples: Dict, profit: Dict) -> Dict:
        peg = multiples.get('peg_ratio')
        roe = profit.get('roe')
        pe = multiples.get('pe_ratio')
        
        # 데이터가 없는 항목은 점수에서 제외
        score = 0
        weights = 0
        
        if peg:
            weights += 50
            if peg < 1.0: score += 50
            elif peg < 1.5: score += 30
            
        if roe:
            weights += 30
            if roe > 25: score += 30
            elif roe > 15: score += 15
            
        if pe:
            weights += 20
            if pe < 30: score += 20
            elif pe < 50: score += 10

        final_score = (score / weights * 10) if weights > 0 else 0
        assessment = 'undervalued' if final_score >= 7 else 'fair_value' if final_score >= 4 else 'overvalued'
        
        missing = []
        if not peg: missing.append("PEG")
        if not roe: missing.append("ROE")
        
        summary = f"성장주 분석: 실측 데이터 기반 점수 {final_score:.1f}/10 ({assessment})."
        if missing: summary += f" (참고: {', '.join(missing)} 데이터 부재로 분석 제한됨)"
        
        # Format metrics
        metrics = {}
        if peg is not None: metrics['PEG'] = f"{peg:.2f}"
        else: metrics['PEG'] = "N/A"
        
        if roe is not None: metrics['ROE'] = f"{roe:.1f}%"
        else: metrics['ROE'] = "N/A"
        
        return {'score': round(final_score, 1), 'assessment': assessment, 'summary': summary, 'key_metrics': metrics}

    def _analyze_as_value(self, info: Dict, multiples: Dict, profit: Dict) -> Dict:
        pb = multiples.get('price_to_book')
        pe = multiples.get('pe_ratio')
        div = (info.get('dividendYield') or 0) * 100
        
        score = 0
        weights = 0
        
        if pb:
            weights += 40
            if pb < 1.2: score += 40
            elif pb < 2.0: score += 20
            
        if pe:
            weights += 30
            if pe < 12: score += 30
            elif pe < 18: score += 15
            
        if div > 0:
            weights += 30
            if div > 4.0: score += 30
            elif div > 2.0: score += 15

        final_score = (score / weights * 10) if weights > 0 else 0
        assessment = 'undervalued' if final_score >= 7 else 'fair_value' if final_score >= 4 else 'overvalued'
        
        metrics = {}
        if pb: metrics['P/B'] = f"{pb:.2f}"
        if div: metrics['배당'] = f"{div:.1f}%"
        if pe: metrics['PER'] = f"{pe:.1f}"

        return {'score': round(final_score, 1), 'assessment': assessment, 'summary': f"가치주 분석: 실측 데이터 기반 점수 {final_score:.1f}/10", 'key_metrics': metrics}

    def _analyze_as_cyclical(self, stock, info: Dict, multiples: Dict) -> Dict:
        # 경기주는 과거 데이터가 필수
        try:
            hist = stock.history(period='5y')
            if hist.empty: raise ValueError("No history")
            curr = hist['Close'].iloc[-1]
            avg = hist['Close'].mean()
            pos = curr / avg
            
            pb = multiples.get('price_to_book')
            score = 0
            if pos < 0.8: score += 5
            if pb and pb < 1.2: score += 5
            
            assessment = 'undervalued' if score >= 7 else 'fair_value'
            return {'score': float(score), 'assessment': assessment, 'summary': f"경기주 분석: 과거 5년 평균가 대비 {pos:.1f}x 위치 (점수: {score}/10)"}
        except:
            return {'score': 0, 'assessment': 'unknown', 'summary': "과거 주가 데이터 부재로 경기 사이클 분석 불가"}

    def _analyze_as_hybrid(self, info: Dict, multiples: Dict, profit: Dict) -> Dict:
        pe = multiples.get('pe_ratio')
        roe = profit.get('roe')
        metrics = {}
        
        if pe: metrics['PER'] = f"{pe:.1f}"
        if roe: metrics['ROE'] = f"{roe:.1f}%"

        if pe and roe:
            score = (5 if pe < 20 else 0) + (5 if roe > 15 else 0)
            return {'score': float(score), 'assessment': 'fair_value' if score >= 5 else 'overvalued', 'summary': "일반 종목 분석 수행 완료", 'key_metrics': metrics}
        return {'score': 0, 'assessment': 'unknown', 'summary': "기초 데이터 부족으로 분석 불가", 'key_metrics': metrics}

    def _get_cash_flow_metrics(self, stock, info: Dict) -> Dict:
        # 현금흐름은 있으면 좋고 없으면 0
        try:
            cf = stock.cashflow
            if not cf.empty and 'Free Cash Flow' in cf.index:
                fcf = cf.loc['Free Cash Flow'].iloc[0]
                mcap = info.get('marketCap', 0)
                return {'fcf_yield': round(fcf / mcap * 100, 2) if mcap > 0 else 0}
        except: pass
        return {'fcf_yield': 0}

def calculate_valuation_metrics(ticker: str) -> Dict:
    return ValuationEngine().calculate_valuation_metrics(ticker)
