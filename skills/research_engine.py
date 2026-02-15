"""
OMNI Research Engine (v3.3)
Stable Council Debate Engine with Robust Type Guarding and Micro-Narratives.
"""

import os
import json
import re
import streamlit as st
import google.generativeai as genai
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from collections import Counter
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
        UI 가시화를 위해 토론 결과(metadata)를 반환함. (PDF 제거됨)
        """
        json_cache = self._get_cache_path(ticker, "json")

        # 1. 캐시 체크 (Machine Execution)
        if not force_refresh and os.path.exists(json_cache):
            mtime = datetime.fromtimestamp(
                os.path.getmtime(json_cache), tz=timezone.utc
            )
            if datetime.now(timezone.utc) - mtime < timedelta(hours=24):
                try:
                    with open(json_cache, "r", encoding="utf-8") as f_json:
                        meta_data = json.load(f_json)
                    return {"metadata": meta_data}
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

    def get_quick_insight(self, ticker: str, summary_en: str) -> Dict[str, Any]:
        """[Cognitive] 기업 개요 영구 저장 및 해자 분석 (고정형 캐싱)"""
        profile_dir = "data/reports/profiles"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)

        cache_path = os.path.join(profile_dir, f"{ticker}.json")

        # 1. 영구 캐시 체크 (File I/O)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        default_res = {
            "summary_kr": "비즈니스 요약을 생성할 수 없습니다.",
            "moat": "데이터 부족",
            "pillars": ["정보 없음"],
        }

        if not self.gemini_available or not summary_en:
            return default_res

        # 2. 분석 실행 (해자 구체성 강화)
        prompt = f"""
        당신은 노련한 비즈니스 분석가입니다. 아래의 영문 기업 요약을 읽고 마스터를 위해 전략적 기초 정보를 추출하십시오.
        
        [Target]: {ticker}
        [Summary EN]: {summary_en[:2000]}
        
        [작성 규정]:
        - 'summary_kr'은 전체 비즈니스를 관통하는 핵심을 한글 3줄로 요약할 것.
        - 'moat'는 이 회사가 가진 독보적 기술이나 자산을 반드시 구체적으로 명시할 것. (예: 'CUDA 생태계', '액체 냉각 설계 기술', '정부 계약 독점' 등)
        - 'pillars'는 분석 시 주요 변수로 삼을 핵심 기술/전략 3가지.
        
        반드시 다음 JSON 형식으로 답변하십시오:
        {{
            "summary_kr": "...",
            "moat": "[유형]: [구체적 자산/기술]",
            "pillars": ["#태그1", "#태그2", "#태그3"]
        }}
        """
        try:
            response = self.model.generate_content(
                prompt, generation_config={"response_mime_type": "application/json"}
            )
            result = json.loads(
                re.sub(r"^```json|^```|```$", "", response.text.strip()).strip()
            )

            # 파일로 박제 (영구 저장)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            return result
        except Exception:
            return default_res

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

    def _extract_hot_keywords(self, news_items: List[Dict[str, Any]]) -> str:
        """뉴스 헤드라인에서 빈출 키워드 Top 3 추출 (Micro-Narrative)"""
        if not news_items:
            return "N/A"

        text = " ".join([n.get("headline", "") for n in news_items]).lower()
        # 특수문자 제거 및 단어 분리 (3글자 이상만)
        words = re.findall(r"\b\w{3,}\b", text)
        # 무의미한 단어 필터링
        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "stock",
            "market",
            "nasdaq",
            "shares",
            "prices",
            "index",
            "ai",
            "nvidia",
            "palantir",
            "report",
            "analysis",
            "quarter",
            "earnings",
        }
        filtered_words = [w for w in words if w not in stop_words]

        counts = Counter(filtered_words)
        top_3 = [word for word, count in counts.most_common(3)]
        kw_str = ", ".join(top_3).upper()
        print(f"[DEBUG] Extracted Hot Keywords: {kw_str}")
        return kw_str

    def _normalize_facts(
        self, ticker: str, details: Dict[str, Any], news_items: List[Dict[str, Any]]
    ) -> str:
        """[GES v4.1] 데이터를 전문가급 서사 포맷으로 정규화 (RR, SBC, PS & Keywords 포함)"""
        # 0. Sector & Theme Context
        biz_model = details.get("biz_model", "Unknown")
        hot_keywords = self._extract_hot_keywords(news_items)

        # 1. Technicals & Pivots
        rsi = details.get("rsi", "N/A")
        vol = details.get("vol_surge_ratio", 1.0)
        trend = "상승(BULL)" if details.get("is_up_trend") else "약세(BEAR/SIDE)"
        h52 = details.get("fifty_two_week_high_dist", 0.0)

        # Pivot & RR Ratio [Multi-Timeframe]
        s1 = details.get("pivot_s1", "N/A")
        r1 = details.get("pivot_r1", "N/A")
        r2 = details.get("pivot_r2", "N/A")
        rr_tac = details.get("rr_tactical", "N/A")
        rr_str = details.get("rr_strategic", "N/A")
        tgt_p = details.get("target_price", "N/A")

        p_str = (
            f"PIVOT: P:{details.get('pivot_p')} (S1:{s1} | R1:{r1} | R2:{r2})\n"
            f"ST_TARGET: {r1} | TACTICAL_RR: {rr_tac}\n"
            f"MT_TARGET: {tgt_p} | STRATEGIC_RR: {rr_str}"
        )

        tech_str = (
            f"TECH: RSI:{rsi} | Vol:{vol}x | Trend:{trend} | 52H:-{h52}% | {p_str}"
        )

        # 2. Fundamentals (Value vs Growth) [Data Guard]
        m_cap = details.get("market_cap", "N/A")
        pe = details.get("pe_ratio", "N/A")
        f_pe = details.get("forward_pe", "N/A")
        ps = details.get("ps_ratio", "N/A")
        peg = details.get("peg_ratio", "N/A")

        # Explicitly handle N/A for critical metrics to guide AI behavior
        if pe == "N/A" and f_pe == "N/A":
            pe = "정보 없음 (섹터 평균 참조 요망)"

        sbc_r = details.get("sbc_ratio", "N/A")
        div = details.get("dividend_yield", 0.0)
        div_str = f"{div * 100:.1f}%" if div else "0%"

        f_score = details.get("f_score_rating", "정보 없음")

        fund_str = f"FUND: Cap:{m_cap} | PE(TTM/Fwd):{pe}/{f_pe} | PS:{ps}x | PEG:{peg} | SBC:{sbc_r}% | Div:{div_str} | Quality:{f_score}"

        # 3. Catalyst (News)
        news_summaries = []
        for n in news_items[:3]:
            headline = n.get("headline", "")[:40]
            sentiment = n.get("sentiment", "Neut")
            news_summaries.append(f"[{sentiment}] {headline}")
        news_str = "CATALYST/NEWS: " + " | ".join(news_summaries)

        norm_out = f"[CONTEXT] Type: {biz_model} | Hot_Keywords: {hot_keywords}\n{tech_str}\n{fund_str}\n{news_str}"
        print(f"[DEBUG] Normalized Facts for LLM:\n{norm_out}")
        return norm_out

    def generate_agent_contexts(
        self, ticker: str, details: Dict[str, Any], news_items: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """[Data Allocation] 공통 팩트 + 전문가별 전용 무기(Data Packet) 배분"""

        # 0. Common Ground (모든 에이전트 공유)
        common = {
            "Ticker": ticker,
            "Price": details.get("last_price"),
            "Sector_Type": details.get("biz_model"),
            "Market_Cap": details.get("market_cap"),
        }

        # 1. Macro Strategist Data (Trend & Context)
        macro_data = {
            **common,
            **{
                "Sector_Context": details.get("biz_model"),
                "Dividend": f"{details.get('dividend_yield', 0) or 0:.2%}",
                "Hot_Keywords": self._extract_hot_keywords(news_items),
            },
        }

        # 2. Quant Analyst Data (Valuation & Statistics)
        # 유사 Z-Score 계산 (현재가 - 52주평균) / (52주고가 - 52주저가)
        h52_dist = details.get("fifty_two_week_high_dist", 0)
        z_score_sim = (50 - h52_dist) / 25  # 단순화된 위치 점수 (-2.0 ~ 2.0 시뮬레이션)

        quant_data = {
            **common,
            **{
                "Valuation": {
                    "P/E(TTM/Fwd)": f"{details.get('pe_ratio')}x / {details.get('forward_pe')}x",
                    "PEG": details.get("peg_ratio"),
                    "P/S": details.get("ps_ratio"),
                    "Z_Score_Sim": f"{z_score_sim:+.2f}σ",
                },
                "Quality": details.get("f_score_rating", "Neutral"),
            },
        }

        # 3. Devil's Advocate Data (Risks & Holes)
        risk_data = {
            **common,
            **{
                "SBC_Ratio": f"{details.get('sbc_ratio')}%",
                "RR_Ratio": details.get("rr_ratio"),
                "Overbought_RSI": "YES" if (details.get("rsi") or 50) > 70 else "NO",
                "S1_Support": details.get("pivot_s1"),
            },
        }

        # 4. Info Collector Data (Catalysts & Flows)
        info_data = {
            **common,
            **{
                "News_Keywords": self._extract_hot_keywords(news_items),
                "Vol_Surge": f"{details.get('vol_surge_ratio')}x",
                "Top_Headline": news_items[0].get("headline") if news_items else "N/A",
            },
        }

        print(f"[DEBUG] Targeted Data Packets distributed for {ticker}")
        return {
            "macro": json.dumps(macro_data, ensure_ascii=False),
            "quant": json.dumps(quant_data, ensure_ascii=False),
            "devil": json.dumps(risk_data, ensure_ascii=False),
            "info": json.dumps(info_data, ensure_ascii=False),
        }

    def _run_council_debate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini 기반 끝장 토론(The Clash) v4.1 (신뢰도 및 대립표 포함)"""
        default_res = {
            "verdict": "HOLD",
            "confidence_score": "50%",
            "headline_summary": "데이터 부족으로 분석 불가",
            "clash_table": [],
            "dashboard_clash": [],
            "ai_summary": "분석 불가",
            "master_briefing": {
                "status": "정보 없음",
                "risk": "정보 없음",
                "strategy": "관망",
            },
        }

        if not self.gemini_available:
            return default_res

        ticker = context.get("ticker")
        details = context.get("details", {})
        news_items = context.get("market_news", [])
        owned = context.get("holding_info")

        # 1. 데이터 패킷 생성
        agent_contexts = self.generate_agent_contexts(ticker, details, news_items)
        previous_history = self._load_previous_history(ticker)

        # [Data Guard] Position Context
        pos_str = "신규 진입 관점 (보유량 0) - 현재 포트폴리오에 없음"
        if owned and owned.get("quantity", 0) > 0:
            pos_str = f"{owned.get('quantity')}주 보유 (평단:{owned.get('average_price')}, 수익률:{owned.get('profit_rate', 0):.1f}%)"

        # 2. [Manager] 프롬프트 조립
        prompt = self.council_manager.build_debate_prompt(
            normalized_facts=self._normalize_facts(ticker, details, news_items),
            pos_str=pos_str,
            history_str=previous_history,
            biz_model=details.get("biz_model", "General"),
            agent_contexts=agent_contexts,
        )

        try:
            response = self.model.generate_content(
                prompt, generation_config={"response_mime_type": "application/json"}
            )
            result = json.loads(
                re.sub(r"^```json|^```|```$", "", response.text.strip()).strip()
            )

            # [Verify] 필수 필드 체크
            required = ["verdict", "confidence_score", "clash_table"]
            if all(k in result for k in required):
                # Ensure details are embedded in the result for SSOT UI access
                result["details"] = details
                print(
                    f"[DEBUG] Debate SUCCESS: Verdict={result['verdict']}, Confidence={result['confidence_score']}"
                )
                return result
            return default_res
        except Exception as e:
            print(f"Council Debate Error: {e}")
            return default_res

    def create_unified_report(
        self, ticker_data: Dict[str, Any], market_news: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        # 데이터 사본 생성 (원본 오염 방지)
        report_data = ticker_data.copy()
        report_data["market_news"] = market_news

        # 1. [Fact Room] 확정된 기술적 지표 산출
        history_data = ticker_data.get("history", {})
        details = {}
        ticker = ticker_data.get("ticker", "TEMP")

        if history_data:
            try:
                df = pd.DataFrame.from_dict(history_data)
                if not df.empty and "Close" in df.columns:
                    rsi_val = FactorEngine.calculate_rsi(df)
                    vol_res = FactorEngine.analyze_volume_energy(df)
                    vol_ratio = vol_res.get("ratio", 100.0) / 100.0

                    close_prices = df["Close"]
                    last_close = close_prices.iloc[-1]
                    ma20 = close_prices.rolling(window=20).mean().iloc[-1]
                    is_up_trend = last_close > ma20

                    pivots = FactorEngine.calculate_pivot_points(df.iloc[-1])
                    pivot_data = pivots.get("Classic", {})
                    high_52 = close_prices.max()
                    dist_52 = (
                        ((high_52 - last_close) / high_52 * 100) if high_52 > 0 else 0.0
                    )

                    extra = ticker_data.get("extra_stats", {})
                    financials = extra.get("financials", {})
                    valuation = extra.get("valuation", {})
                    growth = extra.get("growth", {})

                    # [F-Score]
                    f_score_res = FactorEngine.calculate_piotroski_f_score(
                        financials, extra.get("health", {}), growth, ticker
                    )

                    m_cap = financials.get("market_cap", 0)
                    if m_cap and m_cap > 1e12:
                        m_cap_str = f"{m_cap / 1e12:.2f}T"
                    elif m_cap and m_cap > 1e9:
                        m_cap_str = f"{m_cap / 1e9:.2f}B"
                    else:
                        m_cap_str = f"{m_cap:,}" if m_cap else "N/A"

                    sbc = financials.get("sbc", 0) or 0
                    rev = financials.get("total_rev", 1) or 1
                    sbc_ratio = (sbc / rev * 100) if rev > 0 else 0

                    # [Multi-Timeframe RR Calculation - Calculator Protocol]
                    from skills.news_analyzer import get_analyst_ratings

                    analyst_data = get_analyst_ratings(ticker)
                    target_price = analyst_data.get("target_mean") or pivot_data.get(
                        "R2", 0
                    )

                    def calc_rr_verdict(target, curr, stop):
                        if stop >= curr:
                            return None, "N/A (가각이 지지선 아래)"
                        if target <= curr:
                            return None, "N/A (가격이 목표가 위)"
                        val = (target - curr) / (curr - stop)
                        v_str = (
                            "EXCELLENT (진입 적극추천)"
                            if val >= 2.0
                            else "GOOD (적정)"
                            if val >= 1.0
                            else "BAD (손익비 불리)"
                        )
                        return val, v_str

                    rr_tac_val, rr_tac_ver = calc_rr_verdict(
                        pivot_data.get("R1", 0), last_close, pivot_data.get("S1", 0)
                    )
                    rr_str_val, rr_str_ver = calc_rr_verdict(
                        target_price, last_close, pivot_data.get("S1", 0)
                    )

                    details = {
                        "rsi": round(rsi_val, 2) if not pd.isna(rsi_val) else "N/A",
                        "vol_surge_ratio": round(vol_ratio, 2),
                        "is_up_trend": is_up_trend,
                        "fifty_two_week_high_dist": round(dist_52, 2),
                        "market_cap": m_cap_str,
                        "dividend_yield": financials.get("dividend_yield"),
                        "pe_ratio": valuation.get("trailing_pe"),
                        "forward_pe": valuation.get("forward_pe"),
                        "ps_ratio": valuation.get("ps_ratio"),
                        "peg_ratio": growth.get("peg_ratio"),
                        "sbc_ratio": round(sbc_ratio, 2) if sbc > 0 else "N/A",
                        "pivot_p": round(pivot_data.get("P", 0), 2),
                        "pivot_s1": round(pivot_data.get("S1", 0), 2),
                        "pivot_r1": round(pivot_data.get("R1", 0), 2),
                        "pivot_r2": round(pivot_data.get("R2", 0), 2),
                        "target_price": round(target_price, 2),
                        "rr_tactical": f"{rr_tac_val:.2f} [{rr_tac_ver}]"
                        if rr_tac_val
                        else rr_tac_ver,
                        "rr_strategic": f"{rr_str_val:.2f} [{rr_str_ver}]"
                        if rr_str_val
                        else rr_str_ver,
                        "rr_ratio": round(rr_tac_val, 2) if rr_tac_val else "N/A",
                        "biz_model": FactorEngine.detect_business_model(
                            extra.get("profile", {}), financials, ticker
                        ),
                        "last_price": last_close,
                        "f_score_rating": f_score_res["rating"],
                    }
            except Exception as e:
                print(f"[DEBUG] create_unified_report Error: {e}")

        report_data["details"] = details
        debate_result = self._run_council_debate(report_data)

        if isinstance(debate_result, dict):
            # SSOT Merge: Debate result might contain 'details' or other overrides
            report_data.update(debate_result)

        # PDF Generation Removed (v5.3 Patch)
        # md_content = self.reporter.generate_markdown(report_data)

        json_path = self._get_cache_path(ticker, "json")

        try:
            # Save FULL report data (including calculated details) for UI access
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            from skills.gsheet_loader import save_audit_log

            save_audit_log(
                "GEM_Finance_Portfolio",
                {
                    "summary": f"[{ticker}] {debate_result.get('verdict')} ({debate_result.get('confidence_score')})",
                    "actions": debate_result.get("master_briefing", {}).get(
                        "strategy", "N/A"
                    ),
                    "decisions": f"RR:{details.get('rr_tactical')} | Quality:{details.get('f_score_rating')}",
                },
            )
        except Exception:
            pass

        return {"metadata": report_data}
