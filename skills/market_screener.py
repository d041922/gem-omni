"""
Market Screener [GEM: OMNI] - Sector Hunter Edition
Scans for growth opportunities in specific high-potential sectors.
"""
import yfinance as yf
from typing import List, Dict, Any

class SectorHunter:
    def __init__(self):
        self.sectors = {
            "Energy Infra": ["VRT", "ETN", "GE", "PWR"],
            "Robotics": ["ISRG", "TER", "ZBRA", "BOTZ"],
            "Biotech": ["IBB", "XBI", "AMGN", "VRTX"],
            "AI Core": ["NVDA", "AVGO", "ARM", "TSM"]
        }

    def hunt_opportunities(self) -> List[Dict[str, Any]]:
        """섹터별 유망 종목 스크리닝 (심플 버전)"""
        recommendations = []
        for sector, tickers in self.sectors.items():
            for t in tickers:
                try:
                    s = yf.Ticker(t)
                    hist = s.history(period="5d")
                    if not hist.empty:
                        change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
                        if change > 0:
                            # 최근 상승세 종목 선정
                            recommendations.append({
                                "ticker": t,
                                "sector": sector,
                                "weekly_change": round(change, 2),
                                "price": round(hist['Close'].iloc[-1], 2)
                            })
                except Exception:
                    continue
        return sorted(recommendations, key=lambda x: x['weekly_change'], reverse=True)[:5]

def get_sector_hunter(): return SectorHunter()