"""Recompute positions/cash/aggregates from transaction ledger."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.portfolio_math import (
    PositionSnapshot,
    TransactionInput,
    TX_BUY,
    TX_SELL,
    apply_transaction,
    calculate_unrealized_pnl,
)
from core.repositories.transaction_repo_sqlite import TransactionRepositorySQLite


class RecomputeService:
    def __init__(self, repo: Optional[TransactionRepositorySQLite] = None):
        self.repo = repo or TransactionRepositorySQLite()

    def recompute(self, price_by_symbol: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        price_by_symbol = price_by_symbol or {}
        txs = self.repo.list_all()

        positions: Dict[str, Dict[str, float]] = {}
        cash_balance = 0.0
        realized_pnl_total = 0.0
        cash_ledger: List[Dict[str, Any]] = []

        for tx in txs:
            tx_type = str(tx.get("tx_type", "")).upper().strip()
            symbol = (tx.get("symbol") or "").upper().strip()
            quantity = float(tx.get("quantity", 0.0) or 0.0)
            price = float(tx.get("price", 0.0) or 0.0)
            amount = float(tx.get("amount", 0.0) or 0.0)
            fee = float(tx.get("fee", 0.0) or 0.0)
            tax = float(tx.get("tax", 0.0) or 0.0)

            tx_input = TransactionInput(
                tx_type=tx_type,
                quantity=quantity,
                price=price,
                amount=amount,
                fee=fee,
                tax=tax,
            )

            if tx_type in {TX_BUY, TX_SELL}:
                base = positions.get(symbol, {"quantity": 0.0, "avg_cost": 0.0})
                snap = PositionSnapshot(
                    quantity=float(base["quantity"]),
                    avg_cost=float(base["avg_cost"]),
                    cash_balance=cash_balance,
                )
                updated = apply_transaction(snap, tx_input)
                cash_balance = updated.cash_balance
                realized_pnl_total += updated.realized_pnl_delta
                positions[symbol] = {
                    "quantity": updated.quantity,
                    "avg_cost": updated.avg_cost,
                }
            else:
                snap = PositionSnapshot(quantity=0.0, avg_cost=0.0, cash_balance=cash_balance)
                updated = apply_transaction(snap, tx_input)
                cash_balance = updated.cash_balance

            cash_ledger.append(
                {
                    "tx_id": tx.get("id"),
                    "tx_type": tx_type,
                    "symbol": symbol or None,
                    "balance_after": cash_balance,
                }
            )

        holdings: List[Dict[str, Any]] = []
        stock_krw = 0.0
        unrealized_pnl_total = 0.0

        for symbol, pos in positions.items():
            qty = float(pos["quantity"])
            avg = float(pos["avg_cost"])
            if qty <= 0:
                continue
            mkt = float(price_by_symbol.get(symbol, avg))
            mkt_val = qty * mkt
            u_pnl = calculate_unrealized_pnl(avg_cost=avg, market_price=mkt, quantity=qty)
            stock_krw += mkt_val
            unrealized_pnl_total += u_pnl
            holdings.append(
                {
                    "ticker": symbol,
                    "quantity": qty,
                    "average_price": avg,
                    "current_price": mkt,
                    "current_value_krw": mkt_val,
                    "unrealized_pnl_krw": u_pnl,
                    "profit_rate": (u_pnl / (avg * qty) * 100.0) if avg * qty > 0 else 0.0,
                }
            )

        total_asset = stock_krw + cash_balance
        aggregates = {
            "cash_krw": cash_balance,
            "stock_krw": stock_krw,
            "total_krw": total_asset,
            "realized_pnl_krw": realized_pnl_total,
            "unrealized_pnl_krw": unrealized_pnl_total,
        }

        return {
            "transactions": txs,
            "cash_ledger": cash_ledger,
            "holdings": holdings,
            "aggregates": aggregates,
        }
