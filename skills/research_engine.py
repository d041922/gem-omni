"""
OMNI Research Engine (v2.3)
Stable Council Debate Engine with Robust Type Guarding.
"""

import os
import json
import re
import streamlit as st
import google.generativeai as genai
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from skills.reporting_engine import ReportingEngine
from skills.quant_engine import FactorEngine
from agents.council_manager import CouncilManager
import pandas as pd


class ResearchEngine:
    def __init__(self, cache_dir: str = "data/reports/cache"):
        self.reporter = ReportingEngine()
        self.council_manager = CouncilManager()
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.gemini_available = False
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                # 검증된 최신 모델 사용
                self.model = genai.GenerativeModel("gemini-flash-latest")
                self.gemini_available = True
        except Exception:
            self.gemini_available = False

    def _get_cache_path(self, ticker: str, ext: str = "pdf") -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        return os.path.join(self.cache_dir, f"{ticker}_{date_str}.{ext}")

    def get_report_with_cache(
        self, ticker: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        [Cognitive Domain] 전문가 토론 리포트 생성 및 캐싱.
        UI 가시화를 위해 PDF 바이너리와 토론 결과(metadata)를 함께 반환함.
        """
        pdf_cache = self._get_cache_path(ticker, "pdf")
        json_cache = self._get_cache_path(ticker, "json")

        # 1. 캐시 체크 (Machine Execution)
        if (
            not force_refresh
            and os.path.exists(pdf_cache)
            and os.path.exists(json_cache)
        ):
            mtime = datetime.fromtimestamp(os.path.getmtime(pdf_cache), tz=timezone.utc)
            if datetime.now(timezone.utc) - mtime < timedelta(hours=24):
                try:
                    with open(pdf_cache, "rb") as f_pdf:
                        pdf_data = f_pdf.read()
                    with open(json_cache, "r", encoding="utf-8") as f_json:
                        meta_data = json.load(f_json)
                    return {"pdf": pdf_data, "metadata": meta_data}
                except Exception:
                    pass

        # 2. 분석용 데이터 확보 (Machine Action)
        from skills.data_orchestrator import DataOrchestrator
        from skills.news_manager import NewsManager

        orchestrator = DataOrchestrator()
        ticker_info = orchestrator.get_full_ticker_data(ticker)
        news_manager = NewsManager(orchestrator)
        market_news = news_manager.fetch_ticker_news(ticker)

        # 3. 리포트 생성
        result = self.create_unified_report(ticker_info, market_news or [])
        return result

    def _load_previous_history(self, ticker: str) -> str:
        """[Post-Mortem] 최근 30일 이내의 가장 최신 분석 기록 로드"""
        try:
            files = [
                f
                for f in os.listdir(self.cache_dir)
                if f.startswith(f"{ticker}_") and f.endswith(".json")
            ]
            if not files:
                return "HISTORY: No previous records."

            # 파일명 정렬 (날짜 기준 최신순)
            files.sort(reverse=True)

            # 가장 최신 파일 하나 읽기 (오늘 파일 제외)
            today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            latest_file = None
            for f in files:
                if today_str not in f:
                    latest_file = f
                    break

            if not latest_file:
                return "HISTORY: No previous history beyond today."

            with open(
                os.path.join(self.cache_dir, latest_file), "r", encoding="utf-8"
            ) as f:
                hist = json.load(f)
                date = latest_file.split("_")[1].split(".")[0]
                return f"HISTORY: [{date}] Verdict:{hist.get('verdict')} | Summary:{hist.get('ai_summary')[:100]}..."
        except Exception:
            return "HISTORY: Error loading records."

    def _normalize_facts(
        self, ticker: str, details: Dict[str, Any], news_items: List[Dict[str, Any]]
    ) -> str:
        """[GES v4.1] 데이터를 전문가급 서사 포맷으로 정규화 (RR Ratio & SBC 포함)"""
        # 0. Sector Context
        biz_model = details.get("biz_model", "Unknown")

        # 1. Technicals & Pivots
        rsi = details.get("rsi", "N/A")
        vol = details.get("vol_surge_ratio", 1.0)
        trend = "상승(BULL)" if details.get("is_up_trend") else "약세(BEAR/SIDE)"
        h52 = details.get("fifty_two_week_high_dist", 0.0)

        # Pivot & RR Ratio
        lp = details.get("last_price", 0)
        s1 = details.get("pivot_s1", 0)
        r1 = details.get("pivot_r1", 0)

        rr_ratio = "N/A"
        if lp > 0 and s1 > 0 and r1 > 0:
            upside = (r1 - lp) / lp
            downside = (lp - s1) / lp
            if downside > 0:
                rr_ratio = f"{upside / downside:.2f}"

        p_str = f"PIVOT: P:{details.get('pivot_p')} (S1:{s1} | R1:{r1}) | RR_Ratio:{rr_ratio}"

        tech_str = (
            f"TECH: RSI:{rsi} | Vol:{vol}x | Trend:{trend} | 52H:-{h52}% | {p_str}"
        )

        # 2. Fundamentals (Value vs Growth)
        m_cap = details.get("market_cap", "N/A")
        pe = details.get("pe_ratio", "N/A")
        f_pe = details.get("forward_pe", "N/A")
        peg = details.get("peg_ratio", "N/A")
        sbc_r = details.get("sbc_ratio", "N/A")
        div = details.get("dividend_yield", 0.0)
        div_str = f"{div * 100:.1f}%" if div else "0%"

        fund_str = f"FUND: Cap:{m_cap} | TTM_PE:{pe}x | Fwd_PE:{f_pe}x | PEG:{peg} | SBC_Ratio:{sbc_r}% | Div:{div_str}"

        # 3. News
        news_summaries = []
        for n in news_items[:3]:
            headline = n.get("headline", "")[:40]
            sentiment = n.get("sentiment", "Neut")
            news_summaries.append(f"[{sentiment}] {headline}")
        news_str = "NEWS: " + " | ".join(news_summaries)

        return f"[CONTEXT] Sector_Type: {biz_model}\n{tech_str}\n{fund_str}\n{news_str}"

    def _run_council_debate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini 기반 끝장 토론(The Clash) 및 개인화 조언 생성 (CouncilManager 위임)"""
        default_res = {
            "verdict": "HOLD",
            "ai_summary": "데이터 부족으로 분석 불가",
            "reason": "N/A",
            "action_plan": "보수적 관망",
            "battle_ground": "N/A",
            "portfolio_advice": "정보 없음",
        }

        if not self.gemini_available:
            return default_res

        ticker = context.get("ticker")
        details = context.get("details", {})
        news_items = context.get("market_news", [])
        owned = context.get("holding_info")

        # Sector Context 추출
        biz_model = details.get("biz_model", "General")

        # 1. 데이터 정규화 및 히스토리
        normalized_facts = self._normalize_facts(ticker, details, news_items)
        previous_history = self._load_previous_history(ticker)

        pos_str = "미보유"
        if owned:
            pos_str = f"{owned.get('quantity')}주 보유 (평단:{owned.get('average_price')}, 수익률:{owned.get('profit_rate', 0):.1f}%)"

        # 2. [Manager] 프롬프트 조립 위임
        prompt = self.council_manager.build_debate_prompt(
            normalized_facts=normalized_facts,
            pos_str=pos_str,
            history_str=previous_history,
            biz_model=biz_model,
        )

        try:
            response = self.model.generate_content(
                prompt, generation_config={"response_mime_type": "application/json"}
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```json|^```|```$", "", text).strip()

            result = json.loads(text)
            return (
                result
                if isinstance(result, dict) and "verdict" in result
                else default_res
            )
        except Exception as e:
            print(f"Council Debate Error: {e}")
            return default_res

    def create_unified_report(
        self, ticker_data: Dict[str, Any], market_news: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        # 데이터 사본 생성 (원본 오염 방지)
        report_data = ticker_data.copy()
        report_data["market_news"] = market_news

        # 1. [Fact Room] 확정된 기술적 지표 산출 (Accuracy Lock)
        history_data = ticker_data.get("history", {})
        details = {}

        ticker = ticker_data.get("ticker", "TEMP")
        print(f"\n[DEBUG] === Research Engine: Processing {ticker} ===")

        if history_data:
            try:
                df = pd.DataFrame.from_dict(history_data)
                print(f"[DEBUG] DF Row Count: {len(df)}")

                if not df.empty and "Close" in df.columns:
                    # Technicals
                    rsi_val = FactorEngine.calculate_rsi(df)
                    vol_res = FactorEngine.analyze_volume_energy(df)
                    vol_ratio = vol_res.get("ratio", 100.0) / 100.0

                    close_prices = df["Close"]
                    last_close = close_prices.iloc[-1]
                    ma20 = close_prices.rolling(window=20).mean().iloc[-1]
                    is_up_trend = last_close > ma20

                    # [GES] Pivot Points Calculation
                    pivots = FactorEngine.calculate_pivot_points(df.iloc[-1])
                    pivot_data = pivots.get("Classic", {})

                    high_52 = close_prices.max()
                    dist_52 = (
                        ((high_52 - last_close) / high_52 * 100) if high_52 > 0 else 0.0
                    )

                    # Fundamental Data Binding (from extra_stats)
                    extra = ticker_data.get("extra_stats", {})
                    financials = extra.get("financials", {})
                    valuation = extra.get("valuation", {})
                    growth = extra.get("growth", {})
                    profile = extra.get("profile", {})

                    # [GES] Business Model Detection
                    biz_model = FactorEngine.detect_business_model(
                        profile, financials, ticker
                    )

                    m_cap = financials.get("market_cap", 0)
                    if m_cap and m_cap > 1e12:
                        m_cap_str = f"{m_cap / 1e12:.2f}T"
                    elif m_cap and m_cap > 1e9:
                        m_cap_str = f"{m_cap / 1e9:.2f}B"
                    else:
                        m_cap_str = f"{m_cap:,}" if m_cap else "N/A"

                    # SBC Ratio calculation
                    sbc = financials.get("sbc", 0) or 0
                    rev = financials.get("total_rev", 1) or 1
                    sbc_ratio = (sbc / rev * 100) if rev > 0 else 0

                    # RR Ratio calculation for template
                    lp = ticker_data.get("last_price", 0)
                    s1 = pivot_data.get("S1", 0)
                    r1 = pivot_data.get("R1", 0)
                    rr_val = 0.0
                    if lp > 0 and s1 > 0 and r1 > 0:
                        upside = (r1 - lp) / lp
                        downside = (lp - s1) / lp
                        if downside > 0:
                            rr_val = upside / downside

                    # details 객체 완성 (템플릿 및 토론용)
                    details = {
                        "rsi": round(rsi_val, 2) if not pd.isna(rsi_val) else "N/A",
                        "vol_surge_ratio": round(vol_ratio, 2),
                        "is_up_trend": is_up_trend,
                        "fifty_two_week_high_dist": round(dist_52, 2),
                        "market_cap": m_cap_str,
                        "dividend_yield": financials.get("dividend_yield"),
                        "pe_ratio": valuation.get("trailing_pe"),
                        "forward_pe": valuation.get("forward_pe"),
                        "peg_ratio": growth.get("peg_ratio"),
                        "sbc_ratio": round(sbc_ratio, 2) if sbc > 0 else "N/A",
                        "pivot_p": round(pivot_data.get("P", 0), 2),
                        "pivot_s1": round(pivot_data.get("S1", 0), 2),
                        "pivot_r1": round(pivot_data.get("R1", 0), 2),
                        "rr_ratio": round(rr_val, 2) if rr_val > 0 else "N/A",
                        "biz_model": biz_model,  # Sector Context
                        "last_price": lp,
                    }
                    print(f"[DEBUG] Final Details Map: {details}")
                else:
                    print(
                        f"[DEBUG] DF columns missing or empty. Columns: {list(df.columns)}"
                    )
            except Exception as e:
                print(
                    f"[DEBUG] CRITICAL ERROR in create_unified_report details calc: {e}"
                )

        report_data["details"] = details

        # 2. [Council Chamber] 전문가 토론 실행 (Context에 details 포함)
        debate_result = self._run_council_debate(report_data)

        # 3. 결과 병합 (Type-safe Update)
        if isinstance(debate_result, dict):
            report_data.update(debate_result)

        # 4. PDF 및 캐시 생성 (PDF는 마스터의 요청에 따라 점진적으로 제거 고려 가능하나 일단 유지)
        md_content = self.reporter.generate_markdown(report_data)
        pdf_bytes = self.reporter.render_pdf(md_content)

        # 캐시 저장
        pdf_path = self._get_cache_path(ticker, "pdf")
        json_path = self._get_cache_path(ticker, "json")

        try:
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(debate_result, f, ensure_ascii=False, indent=2)

            # [Post-Process] 구글 시트에 분석 로그 기록
            try:
                from skills.gsheet_loader import save_audit_log

                log_payload = {
                    "summary": f"[{ticker}] {debate_result.get('verdict')} | {debate_result.get('ai_summary')[:150]}",
                    "actions": debate_result.get("action_plan", "N/A"),
                    "decisions": f"Battle: {debate_result.get('battle_ground')} | RSI: {details.get('rsi')}",
                }
                save_audit_log("GEM_Finance_Portfolio", log_payload)
                print(f"[DEBUG] Analysis log saved to GSheet for {ticker}")
            except Exception as ge:
                print(f"[DEBUG] GSheet log error: {ge}")

        except Exception:
            pass

        return {"pdf": pdf_bytes, "metadata": debate_result}
