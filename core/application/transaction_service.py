"""Application service for transaction commands."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.repositories.transaction_repo_sqlite import TransactionRepositorySQLite


class TransactionService:
    def __init__(self, repo: Optional[TransactionRepositorySQLite] = None):
        self.repo = repo or TransactionRepositorySQLite()

    def add_transaction(
        self,
        tx_type: str,
        symbol: Optional[str] = None,
        quantity: float = 0.0,
        price: float = 0.0,
        amount: float = 0.0,
        fee: float = 0.0,
        tax: float = 0.0,
        occurred_at: Optional[str] = None,
        memo: str = "",
    ) -> int:
        return self.repo.create(
            tx_type=tx_type,
            symbol=symbol,
            quantity=quantity,
            price=price,
            amount=amount,
            fee=fee,
            tax=tax,
            occurred_at=occurred_at,
            memo=memo,
        )

    def list_transactions(self) -> List[Dict[str, Any]]:
        return self.repo.list_all()
