"""
Peer Comparison Engine [Safe Edition]
Comparing stocks within the same sector robustly.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional

class PeerComparison:
    SECTOR_PEERS = {
        'Technology': {'NVDA': ['AMD', 'INTC', 'AVGO'], 'AAPL': ['MSFT', 'GOOGL', 'AMZN']},
        'Healthcare': {'JNJ': ['PFE', 'MRK', 'ABBV']},
        'Financials': {'JPM': ['BAC', 'WFC', 'C']}
    }

    def compare_within_sector(self, ticker: str) -> Dict:
        try:
            main_stock = yf.Ticker(ticker)
            info = main_stock.info
            if not info:
                return {'error': 'No info'}
            
            sector = info.get('sector', 'Unknown')
            peers = self._get_peers(ticker, sector)
            if not peers:
                return {'error': 'No peers found'}

            main_metrics = self._get_stock_metrics(ticker, main_stock)
            if not main_metrics:
                return {'error': 'Main metrics fail'}

            peer_metrics = []
            for p_ticker in peers:
                try:
                    p_stock = yf.Ticker(p_ticker)
                    m = self._get_stock_metrics(p_ticker, p_stock)
                    if m:
                        peer_metrics.append(m)
                except Exception:
                     continue

            if not peer_metrics:
                return {'error': 'No peer data'}

            all_stocks = [main_metrics] + peer_metrics
            df = pd.DataFrame(all_stocks)
            summary = self._calculate_rankings(ticker, df)
            summary['market_share_pct'] = self._estimate_market_share(ticker, df)
            summary['summary'] = self._generate_summary(ticker, summary, main_metrics, peer_metrics)

            return {
                'ticker': ticker, 'sector': sector, 'peers_metrics': peer_metrics,
                'comparison_summary': summary, 'peer_table': df
            }
        except Exception as e:
            return {'error': str(e)}

    def _get_peers(self, ticker: str, sector: str) -> List[str]:
        for group in self.SECTOR_PEERS.values():
            if ticker in group:
                return group[ticker]
        
        s_low = sector.lower()
        if 'tech' in s_low:
            return ['AAPL', 'MSFT', 'NVDA', 'AMD']
        if 'health' in s_low:
            return ['JNJ', 'PFE', 'LLY']
        return []

    def _get_stock_metrics(self, ticker: str, stock) -> Optional[Dict]:
        try:
            info = stock.info
            if not info:
                return None
            mcap = info.get('marketCap', 0)
            return {
                'ticker': ticker,
                'name': info.get('shortName', ticker),
                'market_cap_b': round(float(mcap)/1e9, 1) if mcap else 0.0,
                'pe': info.get('forwardPE', info.get('trailingPE', 0.0)),
                'profit_margins': info.get('profitMargins', 0.0) * 100,
                'revenue_growth': info.get('revenueGrowth', 0.0) * 100
            }
        except Exception:
             return None

    def _calculate_rankings(self, ticker: str, df: pd.DataFrame) -> Dict:
        res = {'total_peers': len(df)}
        for col in ['revenue_growth', 'profit_margins']:
            if col in df.columns:
                df_s = df.sort_values(col, ascending=False).reset_index()
                match = df_s[df_s['ticker'] == ticker]
                if not match.empty:
                    res[f'{col}_rank'] = int(match.index[0] + 1)
        return res

    def _estimate_market_share(self, ticker: str, df: pd.DataFrame) -> float:
        if 'market_cap_b' not in df.columns:
            return 0.0
        total = df['market_cap_b'].sum()
        val = df[df['ticker'] == ticker]['market_cap_b'].values
        return round(float(val[0]/total*100), 1) if total > 0 and len(val)>0 else 0.0

    def _generate_summary(self, ticker, rankings, main, peers) -> str:
        share = rankings.get('market_share_pct', 0)
        return f"{ticker}는 섹터 내 주요 종목이며, 시장 점유율 약 {share}% 추정됩니다."

def compare_within_sector(ticker: str) -> Dict:
    return PeerComparison().compare_within_sector(ticker)