"""
GEM: OMNI Data Orchestrator (v3.4 - Universal Fundamental)
Fixed Korean stock PE N/A issues via manual calculation fallback.
Comprehensive collection of Growth, Health, and Cash Flow metrics.
Strictly verified with Triple-Lock Pipeline.
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any
import yfinance as yf

try:
    from skills.gsheet_loader import load_data_from_gsheet
except ImportError:
    load_data_from_gsheet = None


class DataOrchestrator:
    def __init__(self, state_path: str = "data/world_state.json"):
        self.state_path = state_path
        data_dir = os.path.dirname(self.state_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _atomic_write(self, data: Dict[str, Any]) -> bool:
        tmp_path = f"{self.state_path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.state_path)
            return True
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False

    def read_state(self) -> Dict[str, Any]:
        if not os.path.exists(self.state_path):
            return {"data": {}}
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"data": {}}

    def update_state(self, section: str, new_data: Any) -> bool:
        full_state = self.read_state()
        if "data" not in full_state:
            full_state["data"] = {}
        if (
            section in full_state["data"]
            and isinstance(full_state["data"][section], dict)
            and isinstance(new_data, dict)
        ):
            full_state["data"][section].update(new_data)
        else:
            full_state["data"][section] = new_data
        full_state["metadata"] = {
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        return self._atomic_write(full_state)

    def sync_portfolio(self) -> bool:
        if not load_data_from_gsheet:
            return False
        try:
            df, _, _ = load_data_from_gsheet("GEM_Finance_Portfolio")
            if df is None or df.empty:
                return False
            holdings = []
            for _, row in df.iterrows():
                ticker = None
                for cell in row.values:
                    val = str(cell).strip().upper()
                    if (
                        re.match("^[A-Z0-9.]{1,10}$", val)
                        and val != "CASH"
                        and not val.replace(".", "").isdigit()
                    ):
                        ticker = val
                        break
                if not ticker:
                    continue
                nums = []
                for cell in row.values:
                    try:
                        clean_str = (
                            str(cell)
                            .replace("$", "")
                            .replace(",", "")
                            .replace("%", "")
                            .replace("₩", "")
                            .strip()
                        )
                        clean_val = float(clean_str)
                        if clean_val > 0:
                            nums.append(clean_val)
                    except (ValueError, TypeError):
                        pass
                holdings.append(
                    {
                        "ticker": ticker,
                        "quantity": nums[0] if len(nums) > 0 else 0.0,
                        "current_price": nums[2] if len(nums) > 2 else 0.0,
                        "average_price": nums[1] if len(nums) > 1 else 0.0,
                        "profit_rate": ((nums[2] - nums[1]) / nums[1] * 100)
                        if len(nums) > 2 and nums[1] > 0
                        else 0.0,
                        "currency_symbol": "₩"
                        if ".KS" in ticker or ".KQ" in ticker
                        else "$",
                    }
                )
            return self.update_state("portfolio", {"holdings": holdings})
        except Exception as e:
            print(f"[ERROR] Sync failed: {e}")
            return False

    def get_full_ticker_data(self, ticker: str) -> Dict[str, Any]:
        """[Machine Domain] 통합 데이터 수집 (Fundamentals 고도화 버전)"""
        state = self.read_state()
        holdings = state.get("data", {}).get("portfolio", {}).get("holdings", [])
        search_clean = ticker.split(".")[0].upper()
        holding_info = next(
            (
                h
                for h in holdings
                if h.get("ticker").split(".")[0].upper() == search_clean
            ),
            None,
        )

        history_data = {}
        last_price = 0.0
        try:
            t_obj = yf.Ticker(ticker)
            hist = t_obj.history(period="1y")
            if not hist.empty:
                history_data = hist.to_dict()
                last_price = round(float(hist["Close"].iloc[-1]), 2)
        except Exception:
            pass

        # 벤치마크 (QQQ)
        market_benchmark = {"change_pct": 0.0}
        try:
            qqq = yf.Ticker("QQQ").history(period="2d")
            if len(qqq) > 1:
                change = (
                    (qqq["Close"].iloc[-1] - qqq["Close"].iloc[-2])
                    / qqq["Close"].iloc[-2]
                ) * 100
                market_benchmark["change_pct"] = round(float(change), 2)
        except Exception:
            pass

        # [ENHANCED] 전문가급 펀더멘털 지표 전수 수집
        extra_stats = {}
        try:
            info = t_obj.info

            # [FIX] 한국 주식 PE 복구 로직 (Manual Fallback)
            pe_val = info.get("trailingPE")
            eps = info.get("trailingEps")
            if pe_val is None and eps and eps > 0:
                pe_val = last_price / eps

            extra_stats = {
                "financials": {
                    "roe": info.get("returnOnEquity"),
                    "roa": info.get("returnOnAssets"),
                    "gross_margin": info.get("grossMargins"),
                    "op_margin": info.get("operatingMargins"),
                    "fcf": info.get("freeCashflow"),
                    "net_income": info.get("netIncomeToCommon"),
                },
                "growth": {
                    "rev_growth": info.get("revenueGrowth"),
                    "eps_growth": info.get("earningsQuarterlyGrowth"),
                    "peg_ratio": info.get("pegRatio"),
                },
                "valuation": {
                    "trailing_pe": pe_val,
                    "forward_pe": info.get("forwardPE"),
                    "ps_ratio": info.get("priceToSalesTrailing12Months"),
                    "pb_ratio": info.get("priceToBook"),
                },
                "health": {
                    "debt_to_equity": info.get("debtToEquity"),
                    "current_ratio": info.get("currentRatio"),
                },
                "analyst_opinions": {
                    "target_mean": info.get("targetMeanPrice"),
                    "recommendation": info.get("recommendationKey"),
                    "opinions_count": info.get("numberOfAnalystOpinions"),
                },
                "events": {"next_earnings": info.get("nextEarningsDate")},
            }
        except Exception:
            pass

        if last_price == 0 and holding_info:
            last_price = holding_info.get("current_price", 0)

        return {
            "ticker": ticker,
            "last_price": last_price,
            "history": history_data,
            "holding_info": holding_info,
            "is_owned": holding_info is not None,
            "is_ready": len(history_data) > 0,
            "extra_stats": extra_stats,
            "market_context": market_benchmark,
        }
