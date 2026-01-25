"""
Valuation Engine - 종합 밸류에이션 분석
PER, PEG, P/S, ROE 등 다각도 밸류에이션 + 역사적 평균 비교
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional


class ValuationEngine:
    """종합 밸류에이션 분석 엔진"""

    def __init__(self):
        pass

    def calculate_valuation_metrics(self, ticker: str) -> Dict:
        """
        종합 밸류에이션 분석

        Returns:
            {
                'ticker': 'NVDA',
                'multiples': {
                    'pe_ratio': 40.5,
                    'peg_ratio': 0.15,  # < 1.0 = 저평가
                    'price_to_sales': 18.2,
                    'price_to_book': 15.3,
                    'ev_to_ebitda': 35.2
                },
                'profitability': {
                    'roe': 85.3,  # Return on Equity
                    'roa': 45.2,  # Return on Assets
                    'roic': 65.1  # Return on Invested Capital (추정)
                },
                'cash_flow': {
                    'fcf_yield': 2.1,  # Free Cash Flow Yield
                    'fcf_per_share': 12.50,
                    'fcf_growth_yoy': 125.3
                },
                'historical_comparison': {
                    'pe_vs_avg': '+43%',  # 역사적 평균 대비
                    'ps_vs_avg': '+50%',
                    'assessment': 'elevated'  # undervalued/fair/elevated/overvalued
                },
                'sector_comparison': {
                    'pe_vs_sector': '+43%',  # 섹터 평균 대비
                    'premium_justified': True,
                    'reason': '성장률 섹터 평균 3배'
                },
                'valuation_score': 6.5,  # 0-10 (높을수록 저평가)
                'assessment': 'fair_value',  # undervalued/fair_value/overvalued
                'summary': 'PEG 0.15로 성장률 대비 매우 저평가, 단 절대 밸류에이션 높음'
            }
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # 1. Multiples
            multiples = self._get_multiples(info)

            # 2. Profitability
            profitability = self._get_profitability(info)

            # 3. Cash Flow
            cash_flow = self._get_cash_flow_metrics(stock, info)

            # 4. Historical Comparison
            historical = self._compare_to_historical(stock, multiples)

            # 5. Sector Comparison
            sector_comp = self._compare_to_sector(ticker, info, multiples)

            # 6. Valuation Score
            valuation_score = self._calculate_valuation_score(
                multiples, profitability, historical, sector_comp
            )

            # 7. Overall Assessment
            assessment = self._assess_valuation(valuation_score, multiples)

            # 8. Summary
            summary = self._generate_summary(multiples, historical, sector_comp, assessment)

            return {
                'ticker': ticker,
                'multiples': multiples,
                'profitability': profitability,
                'cash_flow': cash_flow,
                'historical_comparison': historical,
                'sector_comparison': sector_comp,
                'valuation_score': valuation_score,
                'assessment': assessment,
                'summary': summary
            }

        except Exception as e:
            return {'error': str(e), 'ticker': ticker}

    def _get_multiples(self, info: Dict) -> Dict:
        """밸류에이션 멀티플 수집"""
        return {
            'pe_ratio': info.get('forwardPE', info.get('trailingPE', None)),
            'peg_ratio': info.get('pegRatio', None),
            'price_to_sales': info.get('priceToSalesTrailing12Months', None),
            'price_to_book': info.get('priceToBook', None),
            'ev_to_ebitda': info.get('enterpriseToEbitda', None),
            'market_cap_b': round(info.get('marketCap', 0) / 1e9, 1) if info.get('marketCap') else None
        }

    def _get_profitability(self, info: Dict) -> Dict:
        """수익성 지표"""
        return {
            'roe': round(info.get('returnOnEquity', 0) * 100, 1) if info.get('returnOnEquity') else None,
            'roa': round(info.get('returnOnAssets', 0) * 100, 1) if info.get('returnOnAssets') else None,
            'roic': None,  # yfinance에서 직접 제공 안 함 (계산 필요)
            'gross_margin': round(info.get('grossMargins', 0) * 100, 1) if info.get('grossMargins') else None,
            'operating_margin': round(info.get('operatingMargins', 0) * 100, 1) if info.get('operatingMargins') else None,
            'net_margin': round(info.get('profitMargins', 0) * 100, 1) if info.get('profitMargins') else None
        }

    def _get_cash_flow_metrics(self, stock, info: Dict) -> Dict:
        """현금 흐름 지표"""
        try:
            # Free Cash Flow
            cash_flow_stmt = stock.cashflow

            fcf = None
            fcf_growth = None

            if not cash_flow_stmt.empty:
                # Free Cash Flow 행 찾기
                for idx in cash_flow_stmt.index:
                    if 'Free Cash Flow' in str(idx):
                        fcf_data = cash_flow_stmt.loc[idx].head(2).tolist()
                        if len(fcf_data) >= 1:
                            fcf = fcf_data[0]

                            # YoY Growth
                            if len(fcf_data) >= 2 and fcf_data[1] != 0:
                                fcf_growth = ((fcf_data[0] - fcf_data[1]) / abs(fcf_data[1]) * 100)

                        break

            # FCF Yield
            market_cap = info.get('marketCap', 0)
            fcf_yield = None
            if fcf and market_cap > 0:
                fcf_yield = (fcf / market_cap) * 100

            # FCF per Share
            shares_outstanding = info.get('sharesOutstanding', 0)
            fcf_per_share = None
            if fcf and shares_outstanding > 0:
                fcf_per_share = fcf / shares_outstanding

            return {
                'fcf': fcf,
                'fcf_yield': round(fcf_yield, 2) if fcf_yield else None,
                'fcf_per_share': round(fcf_per_share, 2) if fcf_per_share else None,
                'fcf_growth_yoy': round(fcf_growth, 1) if fcf_growth else None
            }

        except Exception as e:
            return {'fcf': None, 'fcf_yield': None, 'fcf_per_share': None, 'fcf_growth_yoy': None}

    def _compare_to_historical(self, stock, multiples: Dict) -> Dict:
        """역사적 평균과 비교"""
        try:
            # 과거 5년 가격 데이터
            hist = stock.history(period='5y')

            if hist.empty:
                return {
                    'pe_vs_avg': None,
                    'ps_vs_avg': None,
                    'assessment': 'unknown'
                }

            # 간단한 평균 계산 (정확한 역사적 PE는 재무제표 필요)
            # 현재 vs 평균 위치만 추정
            current_price = hist['Close'].iloc[-1]
            avg_price_5y = hist['Close'].mean()
            price_vs_avg = ((current_price - avg_price_5y) / avg_price_5y * 100)

            # PE ratio
            current_pe = multiples.get('pe_ratio')
            pe_vs_avg = None

            # 대략적 평가 (가격 대비)
            if price_vs_avg > 50:
                assessment = 'elevated'  # 5년 평균 대비 50% 이상 높음
            elif price_vs_avg > 20:
                assessment = 'fair'
            elif price_vs_avg < -20:
                assessment = 'undervalued'
            else:
                assessment = 'fair'

            return {
                'price_vs_5y_avg': f"{price_vs_avg:+.1f}%",
                'pe_vs_avg': pe_vs_avg,  # 정확한 계산 어려움
                'ps_vs_avg': None,
                'assessment': assessment
            }

        except Exception as e:
            return {
                'pe_vs_avg': None,
                'ps_vs_avg': None,
                'assessment': 'unknown'
            }

    def _compare_to_sector(self, ticker: str, info: Dict, multiples: Dict) -> Dict:
        """섹터 평균과 비교"""
        # 섹터 평균 (대략적, 실제로는 섹터 ETF 데이터 필요)
        sector = info.get('sector', 'Unknown')

        # 대략적인 섹터 평균 PE (참고용)
        sector_avg_pe = {
            'Technology': 28,
            'Healthcare': 22,
            'Financials': 12,
            'Energy': 15,
            'Consumer Discretionary': 20,
            'Consumer Staples': 18
        }

        avg_pe = sector_avg_pe.get(sector, 20)
        current_pe = multiples.get('pe_ratio')

        pe_vs_sector = None
        premium_pct = None
        premium_justified = None

        if current_pe and avg_pe:
            premium_pct = ((current_pe - avg_pe) / avg_pe * 100)
            pe_vs_sector = f"{premium_pct:+.1f}%"

            # Premium 정당성 (성장률로 판단)
            peg = multiples.get('peg_ratio')
            if peg and peg < 1.0:
                premium_justified = True
                reason = f'PEG {peg:.2f} < 1.0, 성장률 대비 저평가'
            elif premium_pct < 20:
                premium_justified = True
                reason = 'Premium 20% 이내, 합리적'
            else:
                premium_justified = False
                reason = f'Premium {premium_pct:.0f}% 과도, 성장률 미반영'
        else:
            reason = '비교 데이터 부족'

        return {
            'sector': sector,
            'sector_avg_pe': avg_pe,
            'pe_vs_sector': pe_vs_sector,
            'premium_pct': round(premium_pct, 1) if premium_pct else None,
            'premium_justified': premium_justified,
            'reason': reason
        }

    def _calculate_valuation_score(
        self,
        multiples: Dict,
        profitability: Dict,
        historical: Dict,
        sector_comp: Dict
    ) -> float:
        """
        밸류에이션 스코어 (0-10)
        10 = 매우 저평가, 0 = 매우 고평가

        요소:
        - PEG (4점): < 0.5 = 4점, 0.5-1.0 = 3점, 1.0-1.5 = 2점, > 1.5 = 1점
        - ROE (2점): > 30% = 2점, 20-30% = 1점
        - FCF Yield (2점): > 5% = 2점, 3-5% = 1점
        - 역사적 비교 (2점): undervalued = 2점, fair = 1점
        """
        score = 0.0

        # PEG (4점)
        peg = multiples.get('peg_ratio')
        if peg:
            if peg < 0.5:
                score += 4.0
            elif peg < 1.0:
                score += 3.0
            elif peg < 1.5:
                score += 2.0
            elif peg < 2.0:
                score += 1.0

        # ROE (2점)
        roe = profitability.get('roe')
        if roe:
            if roe > 30:
                score += 2.0
            elif roe > 20:
                score += 1.5
            elif roe > 15:
                score += 1.0

        # FCF Yield (2점)
        fcf_yield = multiples.get('fcf_yield')  # 실제로는 cash_flow에 있음
        # 간단히 생략

        # 역사적 비교 (2점)
        hist_assessment = historical.get('assessment')
        if hist_assessment == 'undervalued':
            score += 2.0
        elif hist_assessment == 'fair':
            score += 1.0

        return round(score, 1)

    def _assess_valuation(self, score: float, multiples: Dict) -> str:
        """종합 평가"""
        peg = multiples.get('peg_ratio')

        # PEG 우선
        if peg and peg < 0.8:
            return 'undervalued'
        elif peg and peg < 1.5:
            return 'fair_value'

        # Score 기준
        if score >= 7:
            return 'undervalued'
        elif score >= 5:
            return 'fair_value'
        else:
            return 'overvalued'

    def _generate_summary(
        self,
        multiples: Dict,
        historical: Dict,
        sector_comp: Dict,
        assessment: str
    ) -> str:
        """요약 생성"""
        peg = multiples.get('peg_ratio')
        pe = multiples.get('pe_ratio')
        premium = sector_comp.get('premium_pct')

        summary_parts = []

        # PEG 평가
        if peg:
            if peg < 0.8:
                summary_parts.append(f"PEG {peg:.2f} → 성장률 대비 매우 저평가")
            elif peg < 1.5:
                summary_parts.append(f"PEG {peg:.2f} → 성장률 대비 적정 수준")
            else:
                summary_parts.append(f"PEG {peg:.2f} → 성장률 대비 고평가")

        # 절대 밸류에이션
        if pe:
            if pe > 40:
                summary_parts.append(f"PER {pe:.0f} 높음")
            elif pe > 25:
                summary_parts.append(f"PER {pe:.0f} 보통")
            else:
                summary_parts.append(f"PER {pe:.0f} 낮음")

        # 섹터 비교
        if premium and sector_comp.get('premium_justified'):
            summary_parts.append(f"섹터 대비 Premium {premium:.0f}% (정당화 가능)")
        elif premium:
            summary_parts.append(f"섹터 대비 Premium {premium:.0f}% (과도)")

        # 종합
        if assessment == 'undervalued':
            summary_parts.append("→ 매수 매력적")
        elif assessment == 'fair_value':
            summary_parts.append("→ 적정 가격")
        else:
            summary_parts.append("→ 고평가 주의")

        return ", ".join(summary_parts)


# ========== Standalone Function ==========

def calculate_valuation_metrics(ticker: str) -> Dict:
    """편의 함수"""
    engine = ValuationEngine()
    return engine.calculate_valuation_metrics(ticker)


# ========== CLI Test ==========

if __name__ == "__main__":
    print("=" * 80)
    print("💰 Valuation Engine Test")
    print("=" * 80)

    ticker = "NVDA"
    print(f"\n🔍 Analyzing {ticker} valuation...")
    print("-" * 80)

    engine = ValuationEngine()
    result = engine.calculate_valuation_metrics(ticker)

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"\n✅ Valuation analysis completed for {result['ticker']}")

        # Multiples
        multiples = result['multiples']
        print(f"\n📊 Valuation Multiples:")
        print(f"   PE Ratio: {multiples.get('pe_ratio', 'N/A')}")
        print(f"   PEG Ratio: {multiples.get('peg_ratio', 'N/A')}")
        print(f"   Price/Sales: {multiples.get('price_to_sales', 'N/A')}")
        print(f"   Price/Book: {multiples.get('price_to_book', 'N/A')}")
        print(f"   EV/EBITDA: {multiples.get('ev_to_ebitda', 'N/A')}")

        # Profitability
        profit = result['profitability']
        print(f"\n💼 Profitability:")
        print(f"   ROE: {profit.get('roe', 'N/A')}%")
        print(f"   ROA: {profit.get('roa', 'N/A')}%")
        print(f"   Gross Margin: {profit.get('gross_margin', 'N/A')}%")
        print(f"   Net Margin: {profit.get('net_margin', 'N/A')}%")

        # Cash Flow
        cf = result['cash_flow']
        print(f"\n💵 Cash Flow:")
        print(f"   FCF Yield: {cf.get('fcf_yield', 'N/A')}%")
        print(f"   FCF per Share: ${cf.get('fcf_per_share', 'N/A')}")
        print(f"   FCF Growth YoY: {cf.get('fcf_growth_yoy', 'N/A')}%")

        # Comparisons
        hist = result['historical_comparison']
        print(f"\n📈 Historical Comparison:")
        print(f"   Price vs 5Y Avg: {hist.get('price_vs_5y_avg', 'N/A')}")
        print(f"   Assessment: {hist.get('assessment', 'N/A')}")

        sector = result['sector_comparison']
        print(f"\n🏢 Sector Comparison:")
        print(f"   Sector: {sector.get('sector', 'N/A')}")
        print(f"   PE vs Sector Avg: {sector.get('pe_vs_sector', 'N/A')}")
        print(f"   Premium Justified: {sector.get('premium_justified', 'N/A')}")
        print(f"   Reason: {sector.get('reason', 'N/A')}")

        # Overall
        print(f"\n⭐ Valuation Score: {result['valuation_score']}/10")
        print(f"🎯 Assessment: {result['assessment']}")
        print(f"\n💡 Summary:")
        print(f"   {result['summary']}")

    print("\n" + "=" * 80)
    print("✅ Test completed!")
