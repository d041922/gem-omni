"""
Earnings Analyzer - 실적 추세 깊이 분석
yfinance 데이터로 과거 4분기 실적 추세, 마진율, 서프라이즈 분석
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime


class EarningsAnalyzer:
    """실적 추세 분석 엔진"""

    def __init__(self):
        pass

    def analyze_earnings_trend(self, ticker: str) -> Dict:
        """
        종합 실적 추세 분석

        Returns:
            {
                'ticker': 'NVDA',
                'revenue_trend': {
                    'direction': 'accelerating',  # accelerating/decelerating/stable
                    'qoq_growth': [10, 22, 34, 41],  # 과거 4분기 QoQ
                    'yoy_growth': [50, 126, 206, 265],  # 과거 4분기 YoY
                    'latest_qoq': 41.2,
                    'latest_yoy': 265.3,
                    'avg_qoq': 26.8,
                    'summary': '4분기 연속 성장 가속, 강력한 모멘텀'
                },
                'earnings_trend': {...},  # 순이익 동일 구조
                'margin_analysis': {
                    'gross_margin': [64.2, 63.8, 64.5, 65.1],
                    'operating_margin': [54.1, 55.3, 56.2, 57.8],
                    'net_margin': [48.3, 49.1, 50.2, 51.5],
                    'trend': 'improving',
                    'summary': '마진율 지속 개선, 가격 결정력 강화'
                },
                'surprise_analysis': {
                    'beat_rate': 1.0,  # 4/4 가이던스 상회
                    'avg_surprise': 12.5,  # 평균 서프라이즈 %
                    'latest_surprise': 15.2,
                    'consistency': 'high',
                    'summary': '지속적 가이던스 상회, 예측 가능성 높음'
                },
                'quality_score': 8.5,  # 0-10 실적 품질 스코어
                'recommendation': 'strong_growth'  # strong_growth/moderate_growth/slowing/declining
            }
        """
        try:
            stock = yf.Ticker(ticker)

            # 1. Revenue Trend
            revenue_trend = self._analyze_revenue_trend(stock)

            # 2. Earnings Trend
            earnings_trend = self._analyze_earnings_trend(stock)

            # 3. Margin Analysis
            margin_analysis = self._analyze_margins(stock)

            # 4. Surprise Analysis
            surprise_analysis = self._analyze_surprises(stock)

            # 5. Quality Score
            quality_score = self._calculate_quality_score(
                revenue_trend, earnings_trend, margin_analysis, surprise_analysis
            )

            # 6. Recommendation
            recommendation = self._generate_recommendation(
                revenue_trend, earnings_trend, margin_analysis
            )

            return {
                'ticker': ticker,
                'revenue_trend': revenue_trend,
                'earnings_trend': earnings_trend,
                'margin_analysis': margin_analysis,
                'surprise_analysis': surprise_analysis,
                'quality_score': quality_score,
                'recommendation': recommendation
            }

        except Exception as e:
            return {'error': str(e), 'ticker': ticker}

    def _analyze_revenue_trend(self, stock) -> Dict:
        """매출 추세 분석"""
        try:
            # yfinance quarterly financials
            quarterly = stock.quarterly_financials

            if quarterly.empty:
                return {'error': 'No quarterly data available'}

            # Revenue 행 찾기 (Total Revenue 또는 Revenue)
            revenue_row = None
            for idx in quarterly.index:
                if 'Total Revenue' in str(idx) or 'Revenue' in str(idx):
                    revenue_row = idx
                    break

            if revenue_row is None:
                return {'error': 'Revenue data not found'}

            # 최근 4분기 (내림차순으로 정렬됨)
            revenues = quarterly.loc[revenue_row].head(4).tolist()
            revenues.reverse()  # 시간 순서대로

            if len(revenues) < 2:
                return {'error': 'Insufficient data'}

            # QoQ 성장률
            qoq_growth = []
            for i in range(1, len(revenues)):
                qoq = ((revenues[i] - revenues[i-1]) / revenues[i-1] * 100)
                qoq_growth.append(round(qoq, 1))

            # YoY 성장률 (전년 동기 대비)
            yoy_growth = []
            if len(revenues) == 4:
                # 간단히 계산 (정확한 YoY는 8분기 데이터 필요)
                # 최근 vs 4분기 전
                for i in range(len(revenues)):
                    if i == 0:
                        yoy = None
                    else:
                        yoy = ((revenues[i] - revenues[0]) / revenues[0] * 100)
                        yoy_growth.append(round(yoy, 1))

            # 추세 판단
            if len(qoq_growth) >= 2:
                if qoq_growth[-1] > qoq_growth[-2]:
                    direction = 'accelerating'
                elif qoq_growth[-1] < qoq_growth[-2] - 5:
                    direction = 'decelerating'
                else:
                    direction = 'stable'
            else:
                direction = 'unknown'

            # 요약
            if direction == 'accelerating':
                summary = f'{len(qoq_growth)}분기 연속 성장 가속, 강력한 모멘텀'
            elif direction == 'decelerating':
                summary = '성장 둔화 신호, 주의 필요'
            else:
                summary = '안정적 성장 추세 유지'

            return {
                'direction': direction,
                'qoq_growth': qoq_growth,
                'yoy_growth': yoy_growth if yoy_growth else None,
                'latest_qoq': qoq_growth[-1] if qoq_growth else None,
                'avg_qoq': round(sum(qoq_growth) / len(qoq_growth), 1) if qoq_growth else None,
                'summary': summary
            }

        except Exception as e:
            return {'error': str(e)}

    def _analyze_earnings_trend(self, stock) -> Dict:
        """순이익 추세 분석"""
        try:
            quarterly = stock.quarterly_financials

            if quarterly.empty:
                return {'error': 'No quarterly data available'}

            # Net Income 행 찾기
            earnings_row = None
            for idx in quarterly.index:
                if 'Net Income' in str(idx):
                    earnings_row = idx
                    break

            if earnings_row is None:
                return {'error': 'Earnings data not found'}

            # 최근 4분기
            earnings = quarterly.loc[earnings_row].head(4).tolist()
            earnings.reverse()

            if len(earnings) < 2:
                return {'error': 'Insufficient data'}

            # QoQ 성장률
            qoq_growth = []
            for i in range(1, len(earnings)):
                if earnings[i-1] != 0:
                    qoq = ((earnings[i] - earnings[i-1]) / abs(earnings[i-1]) * 100)
                    qoq_growth.append(round(qoq, 1))

            # 추세 판단
            if len(qoq_growth) >= 2:
                if qoq_growth[-1] > qoq_growth[-2]:
                    direction = 'accelerating'
                elif qoq_growth[-1] < qoq_growth[-2] - 10:
                    direction = 'decelerating'
                else:
                    direction = 'stable'
            else:
                direction = 'unknown'

            summary = self._generate_earnings_summary(direction, qoq_growth)

            return {
                'direction': direction,
                'qoq_growth': qoq_growth,
                'latest_qoq': qoq_growth[-1] if qoq_growth else None,
                'avg_qoq': round(sum(qoq_growth) / len(qoq_growth), 1) if qoq_growth else None,
                'summary': summary
            }

        except Exception as e:
            return {'error': str(e)}

    def _analyze_margins(self, stock) -> Dict:
        """마진율 분석"""
        try:
            quarterly = stock.quarterly_financials

            if quarterly.empty:
                return {'error': 'No quarterly data available'}

            # 필요한 데이터 찾기
            revenue_row = None
            gross_profit_row = None
            operating_income_row = None
            net_income_row = None

            for idx in quarterly.index:
                idx_str = str(idx)
                if 'Total Revenue' in idx_str or idx_str == 'Total Revenue':
                    revenue_row = idx
                elif 'Gross Profit' in idx_str:
                    gross_profit_row = idx
                elif 'Operating Income' in idx_str:
                    operating_income_row = idx
                elif 'Net Income' in idx_str:
                    net_income_row = idx

            if revenue_row is None:
                return {'error': 'Revenue data not found'}

            revenues = quarterly.loc[revenue_row].head(4).tolist()
            revenues.reverse()

            # Gross Margin
            gross_margins = []
            if gross_profit_row:
                gross_profits = quarterly.loc[gross_profit_row].head(4).tolist()
                gross_profits.reverse()
                gross_margins = [round((gp / rev * 100), 1) for gp, rev in zip(gross_profits, revenues) if rev != 0]

            # Operating Margin
            operating_margins = []
            if operating_income_row:
                operating_incomes = quarterly.loc[operating_income_row].head(4).tolist()
                operating_incomes.reverse()
                operating_margins = [round((oi / rev * 100), 1) for oi, rev in zip(operating_incomes, revenues) if rev != 0]

            # Net Margin
            net_margins = []
            if net_income_row:
                net_incomes = quarterly.loc[net_income_row].head(4).tolist()
                net_incomes.reverse()
                net_margins = [round((ni / rev * 100), 1) for ni, rev in zip(net_incomes, revenues) if rev != 0]

            # 추세 판단
            trend = 'stable'
            if gross_margins and len(gross_margins) >= 2:
                if gross_margins[-1] > gross_margins[0]:
                    trend = 'improving'
                elif gross_margins[-1] < gross_margins[0] - 2:
                    trend = 'declining'

            summary = self._generate_margin_summary(trend, gross_margins, net_margins)

            return {
                'gross_margin': gross_margins if gross_margins else None,
                'operating_margin': operating_margins if operating_margins else None,
                'net_margin': net_margins if net_margins else None,
                'trend': trend,
                'summary': summary
            }

        except Exception as e:
            return {'error': str(e)}

    def _analyze_surprises(self, stock) -> Dict:
        """실적 서프라이즈 분석 (애널리스트 예상 vs 실제)"""
        try:
            # yfinance earnings API
            earnings = stock.earnings_dates

            if earnings is None or earnings.empty:
                return {
                    'beat_rate': None,
                    'avg_surprise': None,
                    'latest_surprise': None,
                    'consistency': 'unknown',
                    'summary': '애널리스트 예상 데이터 없음'
                }

            # EPS Estimate vs EPS Actual
            if 'EPS Estimate' not in earnings.columns or 'Reported EPS' not in earnings.columns:
                return {
                    'beat_rate': None,
                    'avg_surprise': None,
                    'latest_surprise': None,
                    'consistency': 'unknown',
                    'summary': '서프라이즈 데이터 불충분'
                }

            # 최근 4분기
            recent = earnings.head(4)
            surprises = []
            beats = 0

            for idx, row in recent.iterrows():
                estimate = row['EPS Estimate']
                actual = row['Reported EPS']

                if pd.notna(estimate) and pd.notna(actual) and estimate != 0:
                    surprise_pct = ((actual - estimate) / abs(estimate) * 100)
                    surprises.append(surprise_pct)

                    if actual > estimate:
                        beats += 1

            if not surprises:
                return {
                    'beat_rate': None,
                    'avg_surprise': None,
                    'latest_surprise': None,
                    'consistency': 'unknown',
                    'summary': '서프라이즈 계산 불가'
                }

            beat_rate = beats / len(surprises)
            avg_surprise = sum(surprises) / len(surprises)
            latest_surprise = surprises[0] if surprises else None

            # 일관성 판단
            if beat_rate >= 0.75:
                consistency = 'high'
            elif beat_rate >= 0.5:
                consistency = 'moderate'
            else:
                consistency = 'low'

            summary = self._generate_surprise_summary(beat_rate, avg_surprise, consistency)

            return {
                'beat_rate': round(beat_rate, 2),
                'avg_surprise': round(avg_surprise, 1),
                'latest_surprise': round(latest_surprise, 1) if latest_surprise else None,
                'consistency': consistency,
                'summary': summary
            }

        except Exception as e:
            return {
                'error': str(e),
                'beat_rate': None,
                'avg_surprise': None,
                'latest_surprise': None,
                'consistency': 'unknown',
                'summary': '서프라이즈 분석 실패'
            }

    def _calculate_quality_score(
        self,
        revenue_trend: Dict,
        earnings_trend: Dict,
        margin_analysis: Dict,
        surprise_analysis: Dict
    ) -> float:
        """
        실적 품질 스코어 (0-10)

        요소:
        - Revenue 성장 추세 (3점)
        - Earnings 성장 추세 (3점)
        - Margin 추세 (2점)
        - Surprise 일관성 (2점)
        """
        score = 0.0

        # Revenue 추세 (3점)
        if revenue_trend.get('direction') == 'accelerating':
            score += 3.0
        elif revenue_trend.get('direction') == 'stable':
            score += 2.0
        elif revenue_trend.get('direction') == 'decelerating':
            score += 1.0

        # Earnings 추세 (3점)
        if earnings_trend.get('direction') == 'accelerating':
            score += 3.0
        elif earnings_trend.get('direction') == 'stable':
            score += 2.0
        elif earnings_trend.get('direction') == 'decelerating':
            score += 1.0

        # Margin 추세 (2점)
        if margin_analysis.get('trend') == 'improving':
            score += 2.0
        elif margin_analysis.get('trend') == 'stable':
            score += 1.0

        # Surprise 일관성 (2점)
        if surprise_analysis.get('consistency') == 'high':
            score += 2.0
        elif surprise_analysis.get('consistency') == 'moderate':
            score += 1.0

        return round(score, 1)

    def _generate_recommendation(
        self,
        revenue_trend: Dict,
        earnings_trend: Dict,
        margin_analysis: Dict
    ) -> str:
        """추천 생성"""
        rev_dir = revenue_trend.get('direction', 'unknown')
        earn_dir = earnings_trend.get('direction', 'unknown')
        margin_trend = margin_analysis.get('trend', 'unknown')

        # Strong Growth: 모두 가속/개선
        if rev_dir == 'accelerating' and earn_dir == 'accelerating' and margin_trend == 'improving':
            return 'strong_growth'

        # Moderate Growth: 안정적
        elif rev_dir in ['accelerating', 'stable'] and earn_dir in ['accelerating', 'stable']:
            return 'moderate_growth'

        # Slowing: 둔화
        elif rev_dir == 'decelerating' or earn_dir == 'decelerating':
            return 'slowing'

        # Declining: 하락
        else:
            return 'declining'

    # ===== Helper Methods =====

    def _generate_earnings_summary(self, direction: str, qoq_growth: List) -> str:
        if direction == 'accelerating':
            return '순이익 성장 가속, 수익성 개선'
        elif direction == 'decelerating':
            return '순이익 성장 둔화, 주의 필요'
        else:
            return '순이익 안정적 성장'

    def _generate_margin_summary(self, trend: str, gross_margins: List, net_margins: List) -> str:
        if trend == 'improving':
            return '마진율 지속 개선, 가격 결정력 강화'
        elif trend == 'declining':
            return '마진율 하락, 경쟁 압박 또는 비용 증가'
        else:
            return '마진율 안정적 유지'

    def _generate_surprise_summary(self, beat_rate: float, avg_surprise: float, consistency: str) -> str:
        if consistency == 'high':
            return f'지속적 가이던스 상회 (Beat Rate {beat_rate*100:.0f}%), 예측 가능성 높음'
        elif consistency == 'moderate':
            return f'가끔 가이던스 상회, 평균 서프라이즈 {avg_surprise:.1f}%'
        else:
            return '가이던스 하회 빈번, 예측 불확실성 높음'


# ========== Standalone Function ==========

def analyze_earnings_trend(ticker: str) -> Dict:
    """편의 함수"""
    analyzer = EarningsAnalyzer()
    return analyzer.analyze_earnings_trend(ticker)


# ========== CLI Test ==========

if __name__ == "__main__":
    print("=" * 80)
    print("📊 Earnings Analyzer Test")
    print("=" * 80)

    ticker = "NVDA"
    print(f"\n🔍 Analyzing {ticker} earnings trend...")
    print("-" * 80)

    analyzer = EarningsAnalyzer()
    result = analyzer.analyze_earnings_trend(ticker)

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"\n✅ Analysis completed for {result['ticker']}")
        print(f"\n📈 Revenue Trend:")
        rev = result['revenue_trend']
        print(f"   Direction: {rev.get('direction', 'N/A')}")
        print(f"   QoQ Growth: {rev.get('qoq_growth', 'N/A')}")
        print(f"   Latest QoQ: {rev.get('latest_qoq', 'N/A')}%")
        print(f"   Summary: {rev.get('summary', 'N/A')}")

        print(f"\n💰 Earnings Trend:")
        earn = result['earnings_trend']
        print(f"   Direction: {earn.get('direction', 'N/A')}")
        print(f"   QoQ Growth: {earn.get('qoq_growth', 'N/A')}")
        print(f"   Summary: {earn.get('summary', 'N/A')}")

        print(f"\n📊 Margin Analysis:")
        margin = result['margin_analysis']
        print(f"   Gross Margin: {margin.get('gross_margin', 'N/A')}")
        print(f"   Net Margin: {margin.get('net_margin', 'N/A')}")
        print(f"   Trend: {margin.get('trend', 'N/A')}")
        print(f"   Summary: {margin.get('summary', 'N/A')}")

        print(f"\n🎯 Surprise Analysis:")
        surprise = result['surprise_analysis']
        print(f"   Beat Rate: {surprise.get('beat_rate', 'N/A')}")
        print(f"   Avg Surprise: {surprise.get('avg_surprise', 'N/A')}%")
        print(f"   Consistency: {surprise.get('consistency', 'N/A')}")
        print(f"   Summary: {surprise.get('summary', 'N/A')}")

        print(f"\n⭐ Quality Score: {result['quality_score']}/10")
        print(f"💡 Recommendation: {result['recommendation']}")

    print("\n" + "=" * 80)
    print("✅ Test completed!")
