"""Optimality Check v1 for PDOS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class UserPolicyDefaults:
    cash_target_min: float = 0.05
    cash_target_max: float = 0.15
    top1_weight_max: float = 0.25
    top3_weight_max: float = 0.50
    bucket_weight_max: float = 0.60
    rebalance_cooldown_days: int = 14


class OptimalityCheckService:
    def __init__(self, query_service: Any):
        self.query_service = query_service
        self.defaults = UserPolicyDefaults()

    def evaluate(self, user_policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        view = self.query_service.get_portfolio_view()
        return self.evaluate_from_view(view=view, user_policy=user_policy)

    def evaluate_from_view(
        self,
        view: Dict[str, Any],
        user_policy: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        policy = self._merge_policy(user_policy or {})
        holdings = list(view.get("holdings", []))
        aggregates = dict(view.get("aggregates", {}))

        total = self._f(aggregates.get("total_krw", 0.0))
        cash = self._f(aggregates.get("cash_krw", 0.0))

        holding_weights = self._compute_holding_weights(holdings=holdings, total=total)
        concentration = self._compute_concentration(holding_weights)
        bucket_weights = self._compute_bucket_weights(holdings=holdings, cash=cash, total=total)
        cash_ratio = (cash / total) if total > 0 else 0.0

        metrics = {
            "return": {
                "absolute_return_pct": 0.0,
                "excess_return_pct": 0.0,
            },
            "volatility": {
                "realized_volatility_pct": 0.0,
            },
            "concentration": concentration,
            "cash_ratio": cash_ratio,
            "bucket_weights": bucket_weights,
            "weights": holding_weights,
        }
        warnings = self._build_warnings(metrics=metrics, policy=policy)

        return {
            "metrics": metrics,
            "warnings": warnings,
            "policy_used": policy,
        }

    @staticmethod
    def _f(value: Any) -> float:
        try:
            if value is None:
                return 0.0
            return float(value)
        except Exception:
            return 0.0

    def _merge_policy(self, user_policy: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "cash_target_min": self._f(user_policy.get("cash_target_min", self.defaults.cash_target_min)),
            "cash_target_max": self._f(user_policy.get("cash_target_max", self.defaults.cash_target_max)),
            "top1_weight_max": self._f(user_policy.get("top1_weight_max", self.defaults.top1_weight_max)),
            "top3_weight_max": self._f(user_policy.get("top3_weight_max", self.defaults.top3_weight_max)),
            "bucket_weight_max": self._f(user_policy.get("bucket_weight_max", self.defaults.bucket_weight_max)),
            "rebalance_cooldown_days": int(user_policy.get("rebalance_cooldown_days", self.defaults.rebalance_cooldown_days)),
        }

    def _compute_holding_weights(self, holdings: list[Dict[str, Any]], total: float) -> Dict[str, float]:
        if total <= 0:
            return {}
        weight_rows: list[tuple[str, float]] = []
        for row in holdings:
            ticker = str(row.get("ticker", "")).upper().strip()
            if not ticker:
                continue
            value = self._f(row.get("current_value_krw", 0.0))
            if value <= 0:
                qty = self._f(row.get("quantity", 0.0))
                px = self._f(row.get("current_price", 0.0))
                value = qty * px
            weight_rows.append((ticker, value / total))
        # Deterministic output order by ticker.
        return {k: float(v) for k, v in sorted(weight_rows, key=lambda x: x[0])}

    def _compute_concentration(self, holding_weights: Dict[str, float]) -> Dict[str, float]:
        sorted_weights = sorted(holding_weights.values(), reverse=True)
        top1 = float(sorted_weights[0]) if sorted_weights else 0.0
        top3 = float(sum(sorted_weights[:3])) if sorted_weights else 0.0
        return {
            "top1_weight": top1,
            "top3_weight": top3,
        }

    def _bucket_for_ticker(self, ticker: str) -> str:
        t = ticker.upper().strip()
        if t in {"SPY", "VOO", "IVV", "VTI", "QQQ", "TDF"}:
            return "Stable Core"
        if t in {"MSFT", "NVDA", "GOOGL", "AAPL"}:
            return "Growth Core"
        if t in {"TSLA", "PLTR"}:
            return "Option"
        if "SOXX" in t or "SMH" in t or "XLK" in t:
            return "Scale"
        return "Scale"

    def _compute_bucket_weights(self, holdings: list[Dict[str, Any]], cash: float, total: float) -> Dict[str, float]:
        if total <= 0:
            return {"Cash": 0.0}
        bucket_sums: Dict[str, float] = {}
        for row in holdings:
            ticker = str(row.get("ticker", "")).upper().strip()
            if not ticker:
                continue
            value = self._f(row.get("current_value_krw", 0.0))
            if value <= 0:
                value = self._f(row.get("quantity", 0.0)) * self._f(row.get("current_price", 0.0))
            bucket = self._bucket_for_ticker(ticker)
            bucket_sums[bucket] = bucket_sums.get(bucket, 0.0) + value
        bucket_sums["Cash"] = cash
        return {k: float(v / total) for k, v in sorted(bucket_sums.items(), key=lambda x: x[0])}

    def _build_warnings(self, metrics: Dict[str, Any], policy: Dict[str, Any]) -> list[Dict[str, Any]]:
        warnings: list[Dict[str, Any]] = []
        cash_ratio = self._f(metrics.get("cash_ratio", 0.0))
        top1 = self._f(metrics.get("concentration", {}).get("top1_weight", 0.0))
        top3 = self._f(metrics.get("concentration", {}).get("top3_weight", 0.0))
        bucket_weights = dict(metrics.get("bucket_weights", {}))

        if cash_ratio < policy["cash_target_min"]:
            warnings.append(
                self._warning(
                    code="CASH_RATIO_LOW",
                    level="WARN",
                    message="Cash ratio is below target band.",
                    evidence_fields={"cash_ratio": cash_ratio, "cash_target_min": policy["cash_target_min"]},
                )
            )
        elif cash_ratio > policy["cash_target_max"]:
            warnings.append(
                self._warning(
                    code="CASH_RATIO_HIGH",
                    level="WARN",
                    message="Cash ratio is above target band.",
                    evidence_fields={"cash_ratio": cash_ratio, "cash_target_max": policy["cash_target_max"]},
                )
            )

        if top1 > policy["top1_weight_max"]:
            warnings.append(
                self._warning(
                    code="TOP1_CONCENTRATION",
                    level="ALERT",
                    message="Top-1 concentration exceeds policy.",
                    evidence_fields={"top1_weight": top1, "top1_weight_max": policy["top1_weight_max"]},
                )
            )

        if top3 > policy["top3_weight_max"]:
            warnings.append(
                self._warning(
                    code="TOP3_CONCENTRATION",
                    level="ALERT",
                    message="Top-3 concentration exceeds policy.",
                    evidence_fields={"top3_weight": top3, "top3_weight_max": policy["top3_weight_max"]},
                )
            )

        max_bucket_name = ""
        max_bucket_value = 0.0
        for bucket, weight in bucket_weights.items():
            if bucket == "Cash":
                continue
            if self._f(weight) > max_bucket_value:
                max_bucket_name = bucket
                max_bucket_value = self._f(weight)
        if max_bucket_value > policy["bucket_weight_max"]:
            warnings.append(
                self._warning(
                    code="BUCKET_CONCENTRATION",
                    level="ALERT",
                    message="Single non-cash bucket concentration exceeds policy.",
                    evidence_fields={
                        "bucket": max_bucket_name,
                        "bucket_weight": max_bucket_value,
                        "bucket_weight_max": policy["bucket_weight_max"],
                    },
                )
            )

        return warnings

    @staticmethod
    def _warning(code: str, level: str, message: str, evidence_fields: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "code": code,
            "level": level,
            "message": message,
            "evidence_fields": evidence_fields,
        }

