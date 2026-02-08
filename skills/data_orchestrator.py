"""
GEM: OMNI Data Orchestrator (v4.1 - Clean & Precise)
Google Engineering Standard compliant code for portfolio integration.
Removed unused imports and fixed style guide violations.
"""

import json
import os
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
        """[GES v4.1] 정밀 포트폴리오 동기화 및 요약 정보 계산"""
        if not load_data_from_gsheet:
            return False
        try:
            p_df, _, _ = load_data_from_gsheet("GEM_Finance_Portfolio")
            if p_df is None or p_df.empty:
                return False

            holdings = []
            COL_TICKER = "종목코드"
            COL_QTY = "수량"
            COL_AVG_USD = "평균 단가(USD)"
            COL_AVG_KRW = "평균 단가(KRW)"
            COL_PROFIT = "수동 수익률(%)"

            def clean_num(val):
                try:
                    s = (
                        str(val)
                        .replace("$", "")
                        .replace(",", "")
                        .replace("%", "")
                        .replace("₩", "")
                        .strip()
                    )
                    return float(s) if s else 0.0
                except (ValueError, TypeError):
                    return 0.0

            for _, row in p_df.iterrows():
                ticker = str(row.get(COL_TICKER, "")).strip().upper()
                if not ticker or ticker == "CASH":
                    continue

                qty = clean_num(row.get(COL_QTY, 0))
                if qty <= 0:
                    continue

                avg_usd = clean_num(row.get(COL_AVG_USD, 0))
                avg_krw = clean_num(row.get(COL_AVG_KRW, 0))

                is_kr = (
                    ".KS" in ticker
                    or ".KQ" in ticker
                    or (ticker.isdigit() and len(ticker) == 6)
                )
                avg_price = avg_krw if is_kr else avg_usd
                cur_sym = "₩" if is_kr else "$"

                holdings.append(
                    {
                        "ticker": ticker,
                        "quantity": qty,
                        "average_price": avg_price,
                        "current_price": 0.0,
                        "profit_rate": clean_num(row.get(COL_PROFIT, 0)),
                        "currency_symbol": cur_sym,
                    }
                )

            # 요약 정보 계산 (평단가 합계 기준 - 현재가는 0이므로)
            stock_cost_krw = 0.0
            for h in holdings:
                cost = h["quantity"] * h["average_price"]
                if h["currency_symbol"] == "$":
                    cost *= 1450
                stock_cost_krw += cost

            portfolio_data = {
                "holdings": holdings,
                "summary": {
                    "total_cost_krw": stock_cost_krw,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                },
            }
            return self.update_state("portfolio", portfolio_data)
        except Exception:
            return False

    def get_full_ticker_data(self, ticker: str) -> Dict[str, Any]:
        """통합 데이터 수집 및 포트폴리오 병합"""
        state = self.read_state()
        holdings = state.get("data", {}).get("portfolio", {}).get("holdings", [])

        def normalize(t):
            return str(t).split(".")[0].upper().strip()

        search_norm = normalize(ticker)
        holding_info = next(
            (h for h in holdings if normalize(h.get("ticker", "")) == search_norm),
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

        if holding_info:
            holding_info["current_price"] = last_price
            if holding_info["average_price"] > 0 and last_price > 0:
                holding_info["profit_rate"] = (
                    (last_price - holding_info["average_price"])
                    / holding_info["average_price"]
                    * 100
                )

        extra_stats = {}
        try:
            info = t_obj.info
            pe_val = info.get("trailingPE")
            if pe_val is None:
                try:
                    income_stmt = t_obj.quarterly_income_stmt
                    if (
                        income_stmt is not None
                        and not income_stmt.empty
                        and "Diluted EPS" in income_stmt.index
                    ):
                        recent_eps = income_stmt.loc["Diluted EPS"].iloc[:4].sum()
                        if recent_eps > 0:
                            pe_val = last_price / recent_eps
                except Exception:
                    pass

            eps_g = info.get("earningsQuarterlyGrowth")
            peg_val = info.get("pegRatio")
            if peg_val is None and pe_val and eps_g and eps_g > 0:
                peg_val = pe_val / (eps_g * 100)

            fcf_val = info.get("freeCashflow")
            current_ratio = info.get("currentRatio")
            sbc_val, capex_val = 0, 0
            try:
                cf = t_obj.quarterly_cashflow
                if cf is not None and not cf.empty:
                    if "Stock Based Compensation" in cf.index:
                        sbc_val = cf.loc["Stock Based Compensation"].iloc[0]
                    if "Capital Expenditure" in cf.index:
                        capex_val = cf.loc["Capital Expenditure"].iloc[0]
                    if fcf_val is None and "Free Cash Flow" in cf.index:
                        fcf_val = cf.loc["Free Cash Flow"].iloc[0]
            except Exception:
                pass

            # [GES v4.1] Data Extraction for Research Engine & Fundamental Tab
            info = t_obj.info

            # 1. Market Cap & Dividend (New Additions)
            mkt_cap = info.get("marketCap")
            div_yield = info.get("dividendYield")

            # 2. Valuation Logic (Restored)
            pe_val = info.get("trailingPE")
            if pe_val is None:
                try:
                    income_stmt = t_obj.quarterly_income_stmt
                    if (
                        income_stmt is not None
                        and not income_stmt.empty
                        and "Diluted EPS" in income_stmt.index
                    ):
                        recent_eps = income_stmt.loc["Diluted EPS"].iloc[:4].sum()
                        if recent_eps > 0:
                            pe_val = last_price / recent_eps
                except Exception:
                    pass

            eps_g = info.get("earningsQuarterlyGrowth")
            peg_val = info.get("pegRatio")
            if peg_val is None and pe_val and eps_g and eps_g > 0:
                peg_val = pe_val / (eps_g * 100)

            # 3. Financials & Health (Restored)
            fcf_val = info.get("freeCashflow")
            current_ratio = info.get("currentRatio")
            sbc_val, capex_val = 0, 0
            try:
                cf = t_obj.quarterly_cashflow
                if cf is not None and not cf.empty:
                    if "Stock Based Compensation" in cf.index:
                        sbc_val = cf.loc["Stock Based Compensation"].iloc[0]
                    if "Capital Expenditure" in cf.index:
                        capex_val = cf.loc["Capital Expenditure"].iloc[0]
                    if fcf_val is None and "Free Cash Flow" in cf.index:
                        fcf_val = cf.loc["Free Cash Flow"].iloc[0]
            except Exception:
                pass

            extra_stats = {
                "profile": {
                    "sector": info.get("sector", "N/A"),
                    "industry": info.get("industry", "N/A"),
                    "business_model": info.get("longBusinessSummary", "N/A")[:200]
                    + "...",
                },
                "financials": {
                    "market_cap": mkt_cap,  # Added
                    "dividend_yield": div_yield,  # Added
                    "roe": info.get("returnOnEquity"),
                    "gross_margin": info.get("grossMargins"),
                    "fcf": fcf_val,  # Restored
                    "sbc": sbc_val,  # Restored
                    "capex": capex_val,  # Restored
                    "net_income": info.get("netIncomeToCommon"),
                    "inventory": info.get("inventory"),  # Restored
                    "total_rev": info.get("totalRevenue"),
                },
                "growth": {
                    "rev_growth": info.get("revenueGrowth"),
                    "peg_ratio": peg_val,  # Restored
                },
                "valuation": {
                    "trailing_pe": pe_val,
                    "forward_pe": info.get("forwardPE"),
                    "pb_ratio": info.get("priceToBook"),
                },
                "health": {
                    "debt_to_equity": info.get("debtToEquity"),  # Restored
                    "current_ratio": current_ratio,  # Restored
                },
                "events": {
                    "next_earnings": info.get("nextEarningsDate"),
                    "dividend_yield": div_yield,  # Backward compatibility
                },
            }
        except Exception as e:
            print(f"DataOrchestrator Error for {ticker}: {e}")
            pass

        return {
            "ticker": ticker,
            "name": info.get("longName", ticker) if "info" in locals() else ticker,
            "last_price": last_price,
            "history": history_data,
            "holding_info": holding_info,
            "is_owned": holding_info is not None,
            "is_ready": len(history_data) > 0,
            "extra_stats": extra_stats,
            "market_context": {"change_pct": 0.0},
        }
