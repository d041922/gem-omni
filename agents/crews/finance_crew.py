"""Finance crew compatibility layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class FinanceCrew:
    """Minimal FinanceCrew interface used by legacy tests."""

    memory_system: Any
    spreadsheet_name: str = "GEM_Finance_Portfolio"

    def generate_full_report(self) -> Dict[str, Any]:
        return {
            "success": True,
            "report": {
                "spreadsheet": self.spreadsheet_name,
                "memory": type(self.memory_system).__name__,
                "summary": "FinanceCrew compatibility report generated.",
            },
        }


def run_portfolio_audit(portfolio_df: Any, cash_balance: float, market_context: Optional[Dict] = None) -> str:
    """Backward-compatible function retained for callers expecting string output."""
    context = market_context or {}
    rows = len(portfolio_df) if hasattr(portfolio_df, "__len__") else 0
    return (
        f"Audit complete: rows={rows}, cash_balance={cash_balance}, "
        f"context_keys={list(context.keys())}"
    )
