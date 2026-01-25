"""
Sector Rotation Analyzer - 섹터 자금 흐름 및 모멘텀 분석
11개 S&P 섹터 ETF 추적하여 리딩/래깅 섹터 파악
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta


class SectorAnalyzer:
    """섹터 로테이션 분석 엔진"""

    # S&P 11개 섹터 ETF
    SECTOR_ETFS = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financials': 'XLF',
        'Energy': 'XLE',
        'Consumer Discretionary': 'XLY',
        'Consumer Staples': 'XLP',
        'Industrials': 'XLI',
        'Materials': 'XLB',
        'Real Estate': 'XLRE',
        'Utilities': 'XLU',
        'Communication Services': 'XLC'
    }

    def __init__(self, cache_dir: str = "tmp/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "sector_rotation.json"
        self.cache_ttl = 300  # 5분

    def _load_cache(self) -> Optional[Dict]:
        """캐시 로드"""
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)

            cached_time = datetime.fromisoformat(cache.get('timestamp', '2000-01-01'))
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cache

            return None
        except Exception as e:
            print(f"Cache load error: {e}")
            return None

    def _save_cache(self, data: Dict):
        """캐시 저장"""
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Cache save error: {e}")

    def analyze_sector_rotation(self) -> Dict:
        """
        섹터 로테이션 분석

        Returns:
            {
                'leading_sectors': [
                    {
                        'name': 'Technology',
                        'ticker': 'XLK',
                        'momentum_score': 8.5,
                        'return_1m': 5.2,
                        'return_3m': 12.3,
                        'volume_trend': 'increasing',
                        'status': 'strong'
                    },
                    ...
                ],
                'lagging_sectors': [...],
                'neutral_sectors': [...],
                'money_flow': {
                    'from': ['Energy', 'Financials'],
                    'to': ['Technology', 'Healthcare'],
                    'summary': 'Tech 섹터로 자금 유입 중'
                },
                'recommendations': [...]
            }
        """
        # 캐시 확인
        cache = self._load_cache()
        if cache and 'analysis' in cache:
            print("📦 Using cached sector rotation analysis")
            return cache['analysis']

        print(f"🔍 Analyzing rotation across {len(self.SECTOR_ETFS)} sectors...")

        # 1. 각 섹터 ETF 데이터 수집
        sector_data = []
        for sector_name, ticker in self.SECTOR_ETFS.items():
            try:
                data = self._analyze_single_sector(sector_name, ticker)
                if data:
                    sector_data.append(data)
            except Exception as e:
                print(f"⚠️ {sector_name} analysis failed: {e}")
                continue

        if not sector_data:
            return {'error': 'No sector data available'}

        # 2. 섹터 분류 (리딩/래깅/중립)
        sectors_df = pd.DataFrame(sector_data)
        leading, lagging, neutral = self._classify_sectors(sectors_df)

        # 3. Money Flow 분석
        money_flow = self._analyze_money_flow(leading, lagging)

        # 4. 투자 추천
        recommendations = self._generate_recommendations(leading, lagging, sectors_df)

        result = {
            'leading_sectors': leading,
            'lagging_sectors': lagging,
            'neutral_sectors': neutral,
            'money_flow': money_flow,
            'recommendations': recommendations,
            'summary': self._generate_summary(leading, lagging, money_flow)
        }

        # 캐시 저장
        self._save_cache({'analysis': result})

        print(f"✅ Sector rotation analysis completed")
        return result

    def _analyze_single_sector(self, sector_name: str, ticker: str) -> Optional[Dict]:
        """개별 섹터 분석"""
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period='6mo')

            if hist.empty or len(hist) < 60:
                return None

            # 수익률 계산
            current_price = hist['Close'].iloc[-1]
            price_1m_ago = hist['Close'].iloc[-20] if len(hist) >= 20 else hist['Close'].iloc[0]
            price_3m_ago = hist['Close'].iloc[-60] if len(hist) >= 60 else hist['Close'].iloc[0]

            return_1m = ((current_price - price_1m_ago) / price_1m_ago * 100)
            return_3m = ((current_price - price_3m_ago) / price_3m_ago * 100)

            # 거래량 추세
            volume_recent = hist['Volume'].iloc[-10:].mean()
            volume_past = hist['Volume'].iloc[-60:-10].mean()
            volume_ratio = volume_recent / volume_past if volume_past > 0 else 1

            if volume_ratio > 1.2:
                volume_trend = 'increasing'
            elif volume_ratio < 0.8:
                volume_trend = 'decreasing'
            else:
                volume_trend = 'stable'

            # 상대 강도 (RSI)
            rsi = self._calculate_rsi(hist['Close'], period=14)

            # 모멘텀 스코어 계산
            momentum_score = self._calculate_sector_momentum(
                return_1m, return_3m, volume_ratio, rsi
            )

            # 상태 판단
            if momentum_score >= 7:
                status = 'strong'
            elif momentum_score >= 5:
                status = 'moderate'
            elif momentum_score >= 3:
                status = 'weak'
            else:
                status = 'very_weak'

            return {
                'name': sector_name,
                'ticker': ticker,
                'current_price': float(current_price),
                'return_1m': float(return_1m),
                'return_3m': float(return_3m),
                'volume_trend': volume_trend,
                'volume_ratio': float(volume_ratio),
                'rsi': float(rsi) if rsi else None,
                'momentum_score': float(momentum_score),
                'status': status
            }

        except Exception as e:
            print(f"Error analyzing {sector_name}: {e}")
            return None

    def _classify_sectors(self, df: pd.DataFrame) -> tuple:
        """섹터를 리딩/래깅/중립으로 분류"""
        # 모멘텀 스코어 기준
        leading = df[df['momentum_score'] >= 6].sort_values('momentum_score', ascending=False).to_dict('records')
        lagging = df[df['momentum_score'] < 4].sort_values('momentum_score', ascending=True).to_dict('records')
        neutral = df[(df['momentum_score'] >= 4) & (df['momentum_score'] < 6)].to_dict('records')

        return leading, lagging, neutral

    def _analyze_money_flow(self, leading: List[Dict], lagging: List[Dict]) -> Dict:
        """자금 흐름 분석"""
        from_sectors = [s['name'] for s in lagging[:3]]  # 상위 3개 약세
        to_sectors = [s['name'] for s in leading[:3]]   # 상위 3개 강세

        if not to_sectors:
            summary = "섹터 간 자금 흐름 미약"
        elif len(to_sectors) == 1:
            summary = f"{to_sectors[0]} 섹터로 자금 집중 유입"
        else:
            summary = f"{', '.join(to_sectors[:2])} 섹터로 자금 유입 중"

        return {
            'from': from_sectors,
            'to': to_sectors,
            'summary': summary
        }

    def _generate_recommendations(
        self,
        leading: List[Dict],
        lagging: List[Dict],
        all_sectors: pd.DataFrame
    ) -> List[Dict]:
        """투자 추천 생성"""
        recommendations = []

        # 1. 리딩 섹터 추가 매수
        if leading:
            top_leader = leading[0]
            recommendations.append({
                'action': 'overweight',
                'sector': top_leader['name'],
                'ticker': top_leader['ticker'],
                'reason': f"모멘텀 스코어 {top_leader['momentum_score']:.1f}, "
                         f"1개월 수익률 {top_leader['return_1m']:+.1f}%",
                'priority': 'high'
            })

        # 2. 래깅 섹터 비중 축소
        if lagging:
            bottom_lagger = lagging[0]
            recommendations.append({
                'action': 'underweight',
                'sector': bottom_lagger['name'],
                'ticker': bottom_lagger['ticker'],
                'reason': f"모멘텀 약화 {bottom_lagger['momentum_score']:.1f}, "
                         f"1개월 수익률 {bottom_lagger['return_1m']:+.1f}%",
                'priority': 'medium'
            })

        # 3. 과매도 반등 기회
        oversold = all_sectors[
            (all_sectors['rsi'] < 35) &
            (all_sectors['return_3m'] > 0)  # 중기는 상승 추세
        ]
        if not oversold.empty:
            candidate = oversold.iloc[0]
            recommendations.append({
                'action': 'buy_dip',
                'sector': candidate['name'],
                'ticker': candidate['ticker'],
                'reason': f"RSI {candidate['rsi']:.1f} 과매도, "
                         f"3개월 수익률 {candidate['return_3m']:+.1f}% (회복 가능성)",
                'priority': 'medium'
            })

        return recommendations

    def _generate_summary(
        self,
        leading: List[Dict],
        lagging: List[Dict],
        money_flow: Dict
    ) -> str:
        """요약 생성"""
        if not leading and not lagging:
            return "섹터 간 모멘텀 차이 미약, 중립 국면"

        summary_parts = []

        if leading:
            top_3 = [s['name'] for s in leading[:3]]
            summary_parts.append(f"강세 섹터: {', '.join(top_3)}")

        if lagging:
            bottom_3 = [s['name'] for s in lagging[:3]]
            summary_parts.append(f"약세 섹터: {', '.join(bottom_3)}")

        summary_parts.append(money_flow['summary'])

        return " | ".join(summary_parts)

    def get_sector_momentum(self, sector_name: str) -> Optional[float]:
        """특정 섹터의 모멘텀 스코어 조회"""
        analysis = self.analyze_sector_rotation()

        for sector_list in [analysis['leading_sectors'], analysis['neutral_sectors'], analysis['lagging_sectors']]:
            for sector in sector_list:
                if sector['name'] == sector_name:
                    return sector['momentum_score']

        return None

    def recommend_sector_allocation(
        self,
        current_allocation: Dict[str, float]
    ) -> Dict:
        """
        현재 섹터 배분 기준으로 리밸런싱 제안

        Args:
            current_allocation: {'Technology': 45.0, 'Healthcare': 10.0, ...}

        Returns:
            {
                'current': {...},
                'recommended': {...},
                'changes': [
                    {'sector': 'Technology', 'from': 45, 'to': 35, 'change': -10},
                    ...
                ]
            }
        """
        analysis = self.analyze_sector_rotation()

        # 목표 배분 계산
        recommended = {}
        total_leading = len(analysis['leading_sectors'])
        total_lagging = len(analysis['lagging_sectors'])

        for sector_name, current_pct in current_allocation.items():
            # 리딩 섹터는 증액, 래깅 섹터는 감액
            is_leading = any(s['name'] == sector_name for s in analysis['leading_sectors'])
            is_lagging = any(s['name'] == sector_name for s in analysis['lagging_sectors'])

            if is_leading:
                # +5% 증액 (최대 40%)
                recommended[sector_name] = min(current_pct + 5, 40)
            elif is_lagging:
                # -5% 감액 (최소 5%)
                recommended[sector_name] = max(current_pct - 5, 5)
            else:
                # 유지
                recommended[sector_name] = current_pct

        # 합계 100% 정규화
        total = sum(recommended.values())
        if total > 0:
            recommended = {k: (v / total * 100) for k, v in recommended.items()}

        # 변경 사항 계산
        changes = []
        for sector_name in current_allocation:
            from_pct = current_allocation[sector_name]
            to_pct = recommended.get(sector_name, from_pct)
            change = to_pct - from_pct

            if abs(change) > 0.5:  # 0.5% 이상 변경만
                changes.append({
                    'sector': sector_name,
                    'from': round(from_pct, 1),
                    'to': round(to_pct, 1),
                    'change': round(change, 1)
                })

        changes.sort(key=lambda x: abs(x['change']), reverse=True)

        return {
            'current': current_allocation,
            'recommended': recommended,
            'changes': changes
        }

    # ========== Helper Methods ==========

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """RSI 계산"""
        if len(prices) < period + 1:
            return None

        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1] if not rsi.empty else None

    def _calculate_sector_momentum(
        self,
        return_1m: float,
        return_3m: float,
        volume_ratio: float,
        rsi: Optional[float]
    ) -> float:
        """
        섹터 모멘텀 스코어 계산 (0-10)

        요소:
        - 1개월 수익률 (40%)
        - 3개월 수익률 (30%)
        - 거래량 추세 (20%)
        - RSI (10%)
        """
        score = 0.0

        # 1개월 수익률 (4점)
        if return_1m >= 5:
            score += 4.0
        elif return_1m >= 3:
            score += 3.0
        elif return_1m >= 1:
            score += 2.0
        elif return_1m >= 0:
            score += 1.0

        # 3개월 수익률 (3점)
        if return_3m >= 15:
            score += 3.0
        elif return_3m >= 10:
            score += 2.0
        elif return_3m >= 5:
            score += 1.0

        # 거래량 추세 (2점)
        if volume_ratio >= 1.3:
            score += 2.0
        elif volume_ratio >= 1.1:
            score += 1.0

        # RSI (1점)
        if rsi:
            if 40 <= rsi <= 70:
                score += 1.0
            elif rsi > 70:
                score += 0.5  # 과매수 주의

        return min(score, 10.0)


# ========== Standalone Functions ==========

def analyze_sector_rotation() -> Dict:
    """편의 함수: 섹터 로테이션 분석"""
    analyzer = SectorAnalyzer()
    return analyzer.analyze_sector_rotation()


def get_sector_momentum(sector_name: str) -> Optional[float]:
    """편의 함수: 특정 섹터 모멘텀"""
    analyzer = SectorAnalyzer()
    return analyzer.get_sector_momentum(sector_name)


def recommend_sector_allocation(current_allocation: Dict[str, float]) -> Dict:
    """편의 함수: 섹터 배분 추천"""
    analyzer = SectorAnalyzer()
    return analyzer.recommend_sector_allocation(current_allocation)


# ========== CLI Test ==========

if __name__ == "__main__":
    print("=" * 80)
    print("🔄 Sector Rotation Analyzer Test")
    print("=" * 80)

    analyzer = SectorAnalyzer()

    # Test 1: Full Analysis
    print("\n📊 Sector Rotation Analysis")
    print("-" * 80)
    analysis = analyzer.analyze_sector_rotation()

    print("\n🟢 Leading Sectors (Strong Momentum):")
    for i, sector in enumerate(analysis['leading_sectors'], 1):
        print(f"  {i}. {sector['name']:25s} ({sector['ticker']}) | "
              f"Score {sector['momentum_score']:.1f} | "
              f"1M {sector['return_1m']:+6.2f}% | "
              f"3M {sector['return_3m']:+6.2f}%")

    print("\n🔴 Lagging Sectors (Weak Momentum):")
    for i, sector in enumerate(analysis['lagging_sectors'], 1):
        print(f"  {i}. {sector['name']:25s} ({sector['ticker']}) | "
              f"Score {sector['momentum_score']:.1f} | "
              f"1M {sector['return_1m']:+6.2f}% | "
              f"3M {sector['return_3m']:+6.2f}%")

    print("\n💰 Money Flow:")
    print(f"  From: {', '.join(analysis['money_flow']['from'])}")
    print(f"  To:   {', '.join(analysis['money_flow']['to'])}")
    print(f"  Summary: {analysis['money_flow']['summary']}")

    print("\n💡 Recommendations:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        action_emoji = "📈" if rec['action'] == 'overweight' else "📉" if rec['action'] == 'underweight' else "💎"
        print(f"  {i}. {action_emoji} {rec['action'].upper()}: {rec['sector']} ({rec['ticker']})")
        print(f"     Reason: {rec['reason']}")

    print("\n" + "=" * 80)
    print("✅ Test completed!")
