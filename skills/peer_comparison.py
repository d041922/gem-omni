"""
Peer Comparison Engine - 경쟁사 비교 분석
동일 섹터 내 상대 평가 및 시장 점유율 분석
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional


class PeerComparison:
    """경쟁사 비교 분석 엔진"""

    # 섹터별 주요 경쟁사 매핑
    SECTOR_PEERS = {
        'Technology': {
            'NVDA': ['AMD', 'INTC', 'AVGO', 'QCOM'],
            'AAPL': ['MSFT', 'GOOGL', 'META', 'AMZN'],
            'AMD': ['NVDA', 'INTC', 'QCOM', 'MRVL'],
            'TSLA': ['F', 'GM', 'RIVN', 'LCID']
        },
        'Healthcare': {
            'JNJ': ['PFE', 'MRK', 'ABBV', 'LLY'],
            'PFE': ['JNJ', 'MRK', 'ABBV', 'BMY']
        },
        'Financials': {
            'JPM': ['BAC', 'WFC', 'C', 'GS'],
            'BAC': ['JPM', 'WFC', 'C', 'USB']
        }
    }

    def __init__(self):
        pass

    def compare_within_sector(self, ticker: str) -> Dict:
        """
        섹터 내 경쟁사 비교

        Returns:
            {
                'ticker': 'NVDA',
                'sector': 'Technology',
                'peers': [
                    {
                        'ticker': 'AMD',
                        'name': 'Advanced Micro Devices',
                        'market_cap_b': 180.5,
                        'revenue_growth_yoy': 18.2,
                        'earnings_growth_yoy': 25.3,
                        'gross_margin': 50.2,
                        'net_margin': 15.3,
                        'pe_ratio': 32.5,
                        'peg_ratio': 1.3,
                        'relative_strength': 0.68  # NVDA 대비
                    },
                    ...
                ],
                'comparison_summary': {
                    'growth_rank': 1,  # 1위/5개
                    'margin_rank': 1,
                    'valuation_rank': 3,
                    'overall_rank': 1,
                    'market_share_pct': 82.5,
                    'competitive_advantage': 'dominant',  # dominant/strong/moderate/weak
                    'summary': 'NVDA는 섹터 내 압도적 1위, AMD 대비 14배 빠른 성장'
                },
                'peer_table': pd.DataFrame  # 비교 테이블
            }
        """
        try:
            # 1. 주 종목 정보
            main_stock = yf.Ticker(ticker)
            main_info = main_stock.info
            sector = main_info.get('sector', 'Unknown')

            # 2. 경쟁사 리스트 가져오기
            peers = self._get_peers(ticker, sector)

            if not peers:
                return {'error': 'No peers found for this ticker'}

            # 3. 주 종목 메트릭
            main_metrics = self._get_stock_metrics(ticker, main_stock)

            # 4. 각 경쟁사 메트릭
            peer_metrics = []
            for peer_ticker in peers:
                try:
                    peer_stock = yf.Ticker(peer_ticker)
                    metrics = self._get_stock_metrics(peer_ticker, peer_stock)
                    if metrics:
                        peer_metrics.append(metrics)
                except:
                    continue

            if not peer_metrics:
                return {'error': 'Unable to fetch peer data'}

            # 5. 상대 비교
            all_stocks = [main_metrics] + peer_metrics
            comparison_df = pd.DataFrame(all_stocks)

            # 6. 순위 계산
            comparison_summary = self._calculate_rankings(ticker, comparison_df)

            # 7. 시장 점유율 추정 (시가총액 기준)
            market_share = self._estimate_market_share(ticker, comparison_df)
            comparison_summary['market_share_pct'] = market_share

            # 8. 경쟁 우위 평가
            competitive_advantage = self._assess_competitive_advantage(
                comparison_summary, main_metrics, peer_metrics
            )
            comparison_summary['competitive_advantage'] = competitive_advantage

            # 9. 요약 생성
            summary = self._generate_comparison_summary(
                ticker, comparison_summary, main_metrics, peer_metrics
            )
            comparison_summary['summary'] = summary

            return {
                'ticker': ticker,
                'sector': sector,
                'main_metrics': main_metrics,
                'peers': peer_metrics,
                'comparison_summary': comparison_summary,
                'peer_table': comparison_df
            }

        except Exception as e:
            return {'error': str(e), 'ticker': ticker}

    def _get_peers(self, ticker: str, sector: str) -> List[str]:
        """경쟁사 리스트 가져오기"""
        # 1. 사전 정의된 경쟁사 확인
        for sector_peers in self.SECTOR_PEERS.values():
            if ticker in sector_peers:
                return sector_peers[ticker]

        # 2. 없으면 섹터 기반 자동 선정 (향후 확장)
        # 현재는 주요 종목만 지원
        return []

    def _get_stock_metrics(self, ticker: str, stock) -> Optional[Dict]:
        """개별 종목 메트릭 수집"""
        try:
            info = stock.info

            # 기본 정보
            name = info.get('longName', info.get('shortName', ticker))
            market_cap = info.get('marketCap', 0)

            # 성장률 (quarterly financials)
            quarterly = stock.quarterly_financials
            revenue_growth = None
            earnings_growth = None

            if not quarterly.empty:
                # Revenue growth
                for idx in quarterly.index:
                    if 'Total Revenue' in str(idx) or 'Revenue' in str(idx):
                        revenues = quarterly.loc[idx].head(4).tolist()
                        if len(revenues) >= 2:
                            revenue_growth = ((revenues[0] - revenues[1]) / revenues[1] * 100)
                        break

                # Earnings growth
                for idx in quarterly.index:
                    if 'Net Income' in str(idx):
                        earnings = quarterly.loc[idx].head(4).tolist()
                        if len(earnings) >= 2 and earnings[1] != 0:
                            earnings_growth = ((earnings[0] - earnings[1]) / abs(earnings[1]) * 100)
                        break

            # 마진율 (TTM)
            gross_margin = info.get('grossMargins', 0) * 100 if info.get('grossMargins') else None
            net_margin = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None

            # 밸류에이션
            pe_ratio = info.get('forwardPE', info.get('trailingPE', None))
            peg_ratio = info.get('pegRatio', None)
            price_to_sales = info.get('priceToSalesTrailing12Months', None)

            # ROE
            roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None

            return {
                'ticker': ticker,
                'name': name,
                'market_cap_b': round(market_cap / 1e9, 1) if market_cap else None,
                'revenue_growth_yoy': round(revenue_growth, 1) if revenue_growth else None,
                'earnings_growth_yoy': round(earnings_growth, 1) if earnings_growth else None,
                'gross_margin': round(gross_margin, 1) if gross_margin else None,
                'net_margin': round(net_margin, 1) if net_margin else None,
                'pe_ratio': round(pe_ratio, 1) if pe_ratio else None,
                'peg_ratio': round(peg_ratio, 2) if peg_ratio else None,
                'price_to_sales': round(price_to_sales, 1) if price_to_sales else None,
                'roe': round(roe, 1) if roe else None
            }

        except Exception as e:
            print(f"Error getting metrics for {ticker}: {e}")
            return None

    def _calculate_rankings(self, main_ticker: str, df: pd.DataFrame) -> Dict:
        """순위 계산"""
        # 성장률 순위 (높을수록 좋음)
        growth_rank = None
        if 'revenue_growth_yoy' in df.columns:
            df_sorted = df.sort_values('revenue_growth_yoy', ascending=False, na_position='last')
            growth_rank = df_sorted[df_sorted['ticker'] == main_ticker].index[0] + 1 if main_ticker in df_sorted['ticker'].values else None

        # 마진율 순위 (높을수록 좋음)
        margin_rank = None
        if 'gross_margin' in df.columns:
            df_sorted = df.sort_values('gross_margin', ascending=False, na_position='last')
            margin_rank = df_sorted[df_sorted['ticker'] == main_ticker].index[0] + 1 if main_ticker in df_sorted['ticker'].values else None

        # 밸류에이션 순위 (낮을수록 좋음 - PEG 기준)
        valuation_rank = None
        if 'peg_ratio' in df.columns:
            df_sorted = df.sort_values('peg_ratio', ascending=True, na_position='last')
            valuation_rank = df_sorted[df_sorted['ticker'] == main_ticker].index[0] + 1 if main_ticker in df_sorted['ticker'].values else None

        # 종합 순위 (성장률 + 마진율 조합)
        overall_rank = None
        if growth_rank and margin_rank:
            overall_rank = (growth_rank + margin_rank) / 2

        return {
            'growth_rank': growth_rank,
            'margin_rank': margin_rank,
            'valuation_rank': valuation_rank,
            'overall_rank': round(overall_rank, 1) if overall_rank else None,
            'total_peers': len(df)
        }

    def _estimate_market_share(self, main_ticker: str, df: pd.DataFrame) -> Optional[float]:
        """시장 점유율 추정 (시가총액 기준)"""
        if 'market_cap_b' not in df.columns:
            return None

        total_market_cap = df['market_cap_b'].sum()
        main_cap = df[df['ticker'] == main_ticker]['market_cap_b'].values

        if len(main_cap) > 0 and total_market_cap > 0:
            market_share = (main_cap[0] / total_market_cap) * 100
            return round(market_share, 1)

        return None

    def _assess_competitive_advantage(
        self,
        rankings: Dict,
        main_metrics: Dict,
        peer_metrics: List[Dict]
    ) -> str:
        """경쟁 우위 평가"""
        growth_rank = rankings.get('growth_rank')
        margin_rank = rankings.get('margin_rank')
        market_share = rankings.get('market_share_pct', 0)

        # Dominant: 1위 + 시장 점유율 50% 이상
        if growth_rank == 1 and margin_rank == 1 and market_share > 50:
            return 'dominant'

        # Strong: 상위 2위 + 시장 점유율 30% 이상
        elif growth_rank and growth_rank <= 2 and margin_rank and margin_rank <= 2:
            return 'strong'

        # Moderate: 상위 50%
        elif growth_rank and margin_rank:
            total = rankings.get('total_peers', 5)
            if growth_rank <= total / 2:
                return 'moderate'

        # Weak: 하위
        return 'weak'

    def _generate_comparison_summary(
        self,
        ticker: str,
        rankings: Dict,
        main_metrics: Dict,
        peer_metrics: List[Dict]
    ) -> str:
        """비교 요약 생성"""
        growth_rank = rankings.get('growth_rank')
        total = rankings.get('total_peers', 0)
        competitive_advantage = rankings.get('competitive_advantage', 'unknown')

        # 성장률 비교
        main_growth = main_metrics.get('revenue_growth_yoy', 0)
        if peer_metrics:
            avg_peer_growth = sum([p.get('revenue_growth_yoy', 0) for p in peer_metrics if p.get('revenue_growth_yoy')]) / len(peer_metrics)
            growth_multiple = main_growth / avg_peer_growth if avg_peer_growth > 0 else 0
        else:
            growth_multiple = 0

        # 요약 생성
        if competitive_advantage == 'dominant':
            summary = f"{ticker}는 섹터 내 압도적 1위 (시장 점유율 {rankings.get('market_share_pct')}%), "
            if growth_multiple > 1:
                summary += f"경쟁사 대비 {growth_multiple:.1f}배 빠른 성장"
        elif competitive_advantage == 'strong':
            summary = f"{ticker}는 섹터 내 {growth_rank}/{total}위, 강력한 경쟁력 보유"
        elif competitive_advantage == 'moderate':
            summary = f"{ticker}는 섹터 내 중위권 ({growth_rank}/{total}위), 경쟁 심화"
        else:
            summary = f"{ticker}는 섹터 내 하위권, 경쟁 열위"

        return summary

    def get_sector_peers(self, sector: str) -> List[str]:
        """특정 섹터의 대표 종목 리스트"""
        sector_leaders = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'INTC'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'LLY', 'MRK'],
            'Financials': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
            'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'NKE', 'MCD']
        }

        return sector_leaders.get(sector, [])


# ========== Standalone Functions ==========

def compare_within_sector(ticker: str) -> Dict:
    """편의 함수: 경쟁사 비교"""
    comparator = PeerComparison()
    return comparator.compare_within_sector(ticker)


def get_sector_peers(sector: str) -> List[str]:
    """편의 함수: 섹터 대표 종목"""
    comparator = PeerComparison()
    return comparator.get_sector_peers(sector)


# ========== CLI Test ==========

if __name__ == "__main__":
    print("=" * 80)
    print("🏆 Peer Comparison Test")
    print("=" * 80)

    ticker = "NVDA"
    print(f"\n🔍 Comparing {ticker} with sector peers...")
    print("-" * 80)

    comparator = PeerComparison()
    result = comparator.compare_within_sector(ticker)

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"\n✅ Comparison completed for {result['ticker']} ({result['sector']})")

        # Main stock
        main = result['main_metrics']
        print(f"\n📊 {main['ticker']} Metrics:")
        print(f"   Market Cap: ${main.get('market_cap_b', 'N/A')}B")
        print(f"   Revenue Growth: {main.get('revenue_growth_yoy', 'N/A')}%")
        print(f"   Gross Margin: {main.get('gross_margin', 'N/A')}%")
        print(f"   Net Margin: {main.get('net_margin', 'N/A')}%")
        print(f"   PE Ratio: {main.get('pe_ratio', 'N/A')}")
        print(f"   PEG Ratio: {main.get('peg_ratio', 'N/A')}")

        # Peers
        print(f"\n🏢 Peer Comparison:")
        print(f"{'Ticker':<8} {'Growth %':<12} {'G.Margin %':<12} {'PE':<8} {'PEG':<8}")
        print("-" * 60)

        for peer in result['peers']:
            print(f"{peer['ticker']:<8} "
                  f"{peer.get('revenue_growth_yoy', 'N/A'):<12} "
                  f"{peer.get('gross_margin', 'N/A'):<12} "
                  f"{peer.get('pe_ratio', 'N/A'):<8} "
                  f"{peer.get('peg_ratio', 'N/A'):<8}")

        # Summary
        summary = result['comparison_summary']
        print(f"\n📈 Ranking:")
        print(f"   Growth Rank: {summary.get('growth_rank', 'N/A')}/{summary.get('total_peers', 'N/A')}")
        print(f"   Margin Rank: {summary.get('margin_rank', 'N/A')}/{summary.get('total_peers', 'N/A')}")
        print(f"   Market Share: {summary.get('market_share_pct', 'N/A')}%")
        print(f"   Competitive Advantage: {summary.get('competitive_advantage', 'N/A')}")

        print(f"\n💡 Summary:")
        print(f"   {summary.get('summary', 'N/A')}")

    print("\n" + "=" * 80)
    print("✅ Test completed!")
