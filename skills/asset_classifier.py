"""
Asset Classifier [GEM: OMNI] - Dual-Layer Logic
Layer 1: Master's Static Mapping (For Portfolio Display)
Layer 2: Flexible AI Logic (For General Analysis & Suggestions)
"""
from typing import Dict, Any

class AssetClassifier:
    def __init__(self, strategy: str = 'balanced'):
        self.strategy = strategy

    def classify(self, ticker: str, category: str, name: str, account: str = "Unknown") -> str:
        """
        Classifies assets with priority to Master's mapping.
        """
        ticker = str(ticker).upper().strip()
        account = str(account).strip()
        name = str(name)

        # --- LAYER 1: Master's Static Mapping (Highest Priority) ---
        
        # 1. Pension/IRP/DC Rules -> ALWAYS Core
        if any(acc in account for acc in ["연금", "IRP", "DC", "퇴직"]):
            return "Core"

        # 2. Specific Ticker Mapping (Overseas & Domestic)
        # Core
        if ticker in ["NVDA", "GOOGL", "MSFT", "AAPL"]:
            return "Core"
        # Scaling
        if ticker in ["AMZN", "META", "005930.KS", "000660.KS", "423180.KS", "487230.KS", "005930", "000660", "423180", "487230"]:
            return "Scaling"
        if any(k in name for k in ["필반나", "전력핵심인프라", "삼성전자", "SK하이닉스"]):
            return "Scaling"
        # Optional
        if ticker in ["TSLA", "PLTR"]:
            return "Optional"

        # --- LAYER 2: Flexible AI/Strategy Logic (For everything else) ---
        
        # Core: Global Indices & Safe Assets
        if any(k in name for k in ["S&P500", "나스닥100", "채권", "TDF", "현금"]):
            return "Core"
        
        # Scaling: Sector Leaders & Growth ETFs
        if "ETF" in category or "반도체" in name or "AI" in name:
            return "Scaling"
        
        # Optional: Individual high-volatility stocks or themed assets
        if self.strategy == 'aggressive':
            return "Scaling"
        
        return "Optional" # Conservative default for unknown individuals

    def get_rebalancing_target(self, current_core_pct: float) -> Dict[str, Any]:
        """
        Calculates rebalancing needs based on the strategy.
        Strategies:
        - aggressive: Core 40-50%
        - balanced: Core 50-60% (Default)
        - defensive: Core 60-70%
        """
        targets = {
            'aggressive': (40, 50),
            'balanced': (50, 60),
            'defensive': (60, 70)
        }
        
        target_min, target_max = targets.get(self.strategy, (50, 60))

        if current_core_pct < target_min:
            return {
                'action': 'increase_core',
                'target_pct': target_min,
                'adjustment_needed': target_min - current_core_pct,
                'message': f'Increase Core allocation to {target_min:.0f}%'
            }
        elif current_core_pct > target_max:
            return {
                'action': 'decrease_core',
                'target_pct': target_max,
                'adjustment_needed': current_core_pct - target_max,
                'message': f'Decrease Core allocation to {target_max:.0f}%'
            }
        else:
            return {
                'action': 'maintain',
                'status': 'balanced',
                'target_pct': target_min,
                'adjustment_needed': 0,
                'message': 'Core allocation is within target range'
            }

    def calculate_allocation(self, holdings: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Legacy compatibility API for allocation summary."""
        classified = []
        total_value = 0.0
        core_value = 0.0

        for h in holdings:
            value = float(h.get("value", 0) or 0)
            asset_type = self.classify(
                str(h.get("ticker", "")),
                str(h.get("category", "")),
                str(h.get("name", "")),
                str(h.get("account", "Unknown")),
            )
            if asset_type in {"Scaling", "Optional"}:
                asset_type = "Satellite"

            item = dict(h)
            item["asset_type"] = asset_type
            classified.append(item)

            total_value += value
            if asset_type == "Core":
                core_value += value

        satellite_value = max(0.0, total_value - core_value)
        core_pct = (core_value / total_value * 100.0) if total_value else 0.0
        satellite_pct = 100.0 - core_pct if total_value else 0.0

        return {
            "total_value": total_value,
            "core_value": core_value,
            "core_pct": core_pct,
            "satellite_value": satellite_value,
            "satellite_pct": satellite_pct,
            "holdings_classified": classified,
            "rebalancing": self.get_rebalancing_target(core_pct),
        }
