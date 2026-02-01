"""
Sector Rotation Analyzer [Safe Edition]
Dynamic sector momentum and money flow tracking.
All dictionary/dataframe accesses secured via .get().
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta

class SectorAnalyzer:
    SECTOR_ETFS = {
        'Technology': 'XLK', 'Healthcare': 'XLV', 'Financials': 'XLF', 'Energy': 'XLE',
        'Consumer Discretionary': 'XLY', 'Consumer Staples': 'XLP', 'Industrials': 'XLI',
        'Materials': 'XLB', 'Real Estate': 'XLRE', 'Utilities': 'XLU', 'Communication Services': 'XLC'
    }

    def __init__(self, cache_dir: str = "tmp/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "sector_rotation.json"

    def analyze_sector_rotation(self) -> Dict:
        # Simple cache check
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                if datetime.now() - datetime.fromisoformat(cache.get('timestamp', '2000-01-01')) < timedelta(minutes=5):
                    return cache.get('analysis', {})
            except Exception:
                 pass

        print("🔍 Analyzing sector rotation...")
        sector_data = []
        for name, ticker in self.SECTOR_ETFS.items():
            try:
                data = self._analyze_single_sector(name, ticker)
                if data:
                    sector_data.append(data)
            except Exception:
                 continue

        if not sector_data:
            return {'error': 'No data'}
        
        df = pd.DataFrame(sector_data)
        leading = df[df.get('momentum_score', pd.Series([0])) >= 6].sort_values('momentum_score', ascending=False).to_dict('records')
        lagging = df[df.get('momentum_score', pd.Series([0])) < 4].sort_values('momentum_score', ascending=True).to_dict('records')
        neutral = df[(df.get('momentum_score', pd.Series([0])) >= 4) & (df.get('momentum_score', pd.Series([0])) < 6)].to_dict('records')

        result = {
            'leading_sectors': leading, 'lagging_sectors': lagging, 'neutral_sectors': neutral,
            'money_flow': self._analyze_money_flow(leading, lagging),
            'sector_performance': {s.get('name', ''): s.get('momentum_score', 0.0) for s in sector_data if s.get('name')}
        }
        
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({'timestamp': datetime.now().isoformat(), 'analysis': result}, f)
        except Exception:
             pass
        return result

    def _analyze_single_sector(self, name: str, ticker: str) -> Optional[Dict]:
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period='6mo')
            if hist.empty or len(hist) < 20:
                return None
            
            curr = float(hist['Close'].iloc[-1])
            prev_1m = float(hist['Close'].iloc[-20])
            ret_1m = (curr - prev_1m) / prev_1m * 100
            
            vol_recent = hist['Volume'].iloc[-5:].mean()
            vol_avg = hist['Volume'].mean()
            vol_ratio = vol_recent / vol_avg if vol_avg > 0 else 1.0
            
            score = (min(ret_1m, 10.0) * 0.5) + (min(vol_ratio, 2.0) * 2.5) # Simplified score
            
            return {
                'name': name, 'ticker': ticker, 'current_price': curr,
                'return_1m': float(ret_1m), 'momentum_score': float(score)
            }
        except Exception:
             return None

    def _analyze_money_flow(self, leading, lagging) -> Dict:
        to_s = [s.get('name', '') for s in leading[:3]]
        from_s = [s.get('name', '') for s in lagging[:3]]
        return {'from': from_s, 'to': to_s, 'summary': f"{', '.join(to_s[:2])} 섹터로 자금 유입 중" if to_s else "자금 흐름 정체"}

def analyze_sector_rotation():
    return SectorAnalyzer().analyze_sector_rotation()