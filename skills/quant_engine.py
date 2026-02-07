"""
GEM: OMNI Factor Engine (v7.6 - Null Safety & Precise Logic)
Fixed TypeError in inventory calculation and refined sector classification.
Google Engineering Standard compliant code.
"""

import pandas as pd
from typing import Dict, Any, List


class FactorEngine:
    """금융 기술 지표 및 펀더멘털 전략 브리핑 엔진 (v7.6)"""

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> float:
        if len(df) < period + 1:
            return 50.0
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    @staticmethod
    def calculate_bb_stats(df: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        if len(df) < period:
            return {"upper": 0, "mid": 0, "lower": 0, "pos_pct": 50, "width": 0}
        mid = df["Close"].rolling(window=period).mean()
        std = df["Close"].rolling(window=period).std()
        upper = mid + (std * 2)
        lower = mid - (std * 2)
        curr_p = float(df["Close"].iloc[-1])
        m_val = mid.iloc[-1]
        width = (upper.iloc[-1] - lower.iloc[-1]) / m_val if m_val != 0 else 0
        diff = upper.iloc[-1] - lower.iloc[-1]
        pos_pct = ((curr_p - lower.iloc[-1]) / diff * 100) if diff > 0 else 50
        return {
            "upper": float(upper.iloc[-1]),
            "mid": float(m_val),
            "lower": float(lower.iloc[-1]),
            "pos_pct": float(pos_pct),
            "width": float(width),
        }

    @staticmethod
    def analyze_volume_energy(df: pd.DataFrame) -> Dict[str, Any]:
        if len(df) < 20:
            return {"ratio": 100, "nature": "Normal"}
        avg_vol = df["Volume"].rolling(window=20).mean().iloc[-1]
        curr_vol = df["Volume"].iloc[-1]
        ratio = (curr_vol / avg_vol) * 100 if avg_vol > 0 else 0
        price_change = df["Close"].iloc[-1] - df["Close"].iloc[-2]
        nature = (
            "집중 매수 유입"
            if ratio > 150 and price_change > 0
            else "단기 차익실현"
            if ratio > 150
            else "균형 잡힌 수급"
        )
        return {"ratio": round(float(ratio), 1), "nature": nature}

    @staticmethod
    def get_ma_ribbon_status(df: pd.DataFrame) -> Dict[str, str]:
        periods = [5, 10, 20, 50, 100, 200]
        if df.empty:
            return {f"MA{p}": "N/A" for p in periods}
        curr_p = float(df["Close"].iloc[-1])
        res = {}
        for p in periods:
            if len(df) >= p:
                sma = df["Close"].rolling(window=p).mean().iloc[-1]
                res[f"MA{p}"] = "Bullish" if curr_p > sma else "Bearish"
            else:
                res[f"MA{p}"] = "N/A"
        return res

    @staticmethod
    def detect_business_model(
        profile: Dict[str, Any], fin: Dict[str, Any], ticker: str = ""
    ) -> str:
        """[Layer 1] 비즈니스 모델 정밀 분류"""
        sector = str(profile.get("sector", "")).lower()
        industry = str(profile.get("industry", "")).lower()
        gpm = fin.get("gross_margin") or 0

        t_up = ticker.upper()
        # 0. Hardcoded Overrides
        if any(t in t_up for t in ["005930", "000660", "MU", "WDC", "HBM"]):
            return "Hybrid-Memory"
        if any(
            t in t_up
            for t in [
                "NVDA",
                "AMD",
                "TSM",
                "AVGO",
                "PLTR",
                "MSFT",
                "GOOGL",
                "META",
                "AMZN",
            ]
        ):
            return "Asset-Light"

        # 1. Logic-based classification
        if "semicon" in sector and ("memory" in industry or gpm < 0.45):
            return "Hybrid-Memory"
        if (
            (gpm > 0.5)
            or ("software" in sector)
            or ("services" in sector)
            or ("technology" in sector)
        ):
            return "Asset-Light"
        return "Asset-Heavy"

    @staticmethod
    def generate_comprehensive_verdict(
        extra_stats: Dict[str, Any],
        last_p: float,
        ticker: str = "",
        holding_info: Dict[str, Any] = None,
    ) -> Dict[str, str]:
        """[Engine v7.6] 섹터별 가중치 + Wise Aggression + 강제 Bear Case"""
        val = extra_stats.get("valuation", {})
        growth = extra_stats.get("growth", {})
        fin = extra_stats.get("financials", {})

        biz_model = FactorEngine.detect_business_model(
            extra_stats.get("profile", {}), fin, ticker
        )

        pe, f_pe, pb = (
            val.get("trailing_pe"),
            val.get("forward_pe"),
            val.get("pb_ratio"),
        )
        peg = growth.get("peg_ratio")
        sbc, rev = fin.get("sbc") or 0, fin.get("total_rev") or 1
        sbc_ratio = (sbc / rev) * 100 if rev > 0 else 0

        v_verdict, g_verdict, r_verdict = (
            "데이터 부족",
            "데이터 부족",
            "정밀 검사 중...",
        )

        # --- [Layer 2] Sector-Specific Logic ---
        if biz_model == "Asset-Light":
            if pe:
                v_verdict = f"P/E {pe:.1f}배. " + (
                    "기대감 선반영 프리미엄 영역." if pe > 80 else "성장 가치 반영 중."
                )
            if peg:
                g_verdict = f"PEG {peg:.2f}. " + (
                    "저평가 고성장 시그널." if peg < 1.0 else "성장에 합당한 밸류."
                )

            if sbc_ratio > 15:
                r_verdict = f"⚠️ [SBC Risk] 매출의 {sbc_ratio:.1f}%가 주식 보상 유출. 주주 가치 희석 리스크가 결정적임."
            elif peg and peg > 2.0:
                r_verdict = "⚠️ [Over-Expectation] 성장에 비해 주가가 너무 앞서감. 실적 하회 시 변동성 주의."
            else:
                r_verdict = (
                    "매출 가속화 여부가 핵심. 경쟁사의 시장 점유율 침투가 주시 항목임."
                )

        elif biz_model == "Hybrid-Memory":
            if pb:
                v_verdict = f"P/B {pb:.2f}배. " + (
                    "역사적 바닥권(Strong Support)."
                    if pb < 1.3
                    else "사이클 고점 임박."
                    if pb > 2.2
                    else "사이클 중기 국면."
                )
            if f_pe and pe and f_pe < pe * 0.6:
                g_verdict = "강력한 업황 턴어라운드(Up-Cycle) 진입 신호."

            # [FIX] Null-safe inventory ratio calculation
            inv_val = fin.get("inventory") or 0
            if rev > 0 and inv_val > 0:
                inv_ratio = (inv_val / rev) * 100
                if inv_ratio > 30:
                    r_verdict = f"⚠️ [Inventory] 재고 비중({inv_ratio:.1f}%) 급증. 수요 둔화 시 실적 쇼크 위험."
                else:
                    r_verdict = "HBM 등 고부가 제품 수율 및 시장 점유율 유지 여부가 핵심 리스크임."
            else:
                r_verdict = "재고 데이터 부재. 제품 수율 및 시장 점유율 유지 여부가 핵심 리스크임."

        else:
            v_verdict = f"P/E {pe:.1f}배 / P/B {pb:.2f}배 기반."
            r_verdict = "부채 상환 능력 및 현금 흐름 악화 여부 주시."

        return {
            "valuation": v_verdict,
            "growth": g_verdict,
            "risk": r_verdict,
        }

    @staticmethod
    def generate_peer_comparison(extra_stats: Dict[str, Any]) -> str:
        sector = extra_stats.get("profile", {}).get("sector", "시장")
        fin = extra_stats.get("financials", {})
        growth = extra_stats.get("growth", {})
        roe = (fin.get("roe") or 0) * 100
        peg = growth.get("peg_ratio", 2.0) or 2.0
        roe_rank = "상위 1%" if roe > 50 else "우량" if roe > 20 else "평균"
        return f"[{sector} Peer Comparison] 섹터 내 ROE {roe_rank}, PEG {'저평가' if peg < 1.0 else '적정'} 수준."

    @staticmethod
    def generate_fundamental_report(
        extra_stats: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        growth, fin = extra_stats.get("growth", {}), extra_stats.get("financials", {})
        report = []
        if growth.get("peg_ratio"):
            report.append(
                {
                    "분류": "성장성",
                    "항목": "PEG Ratio",
                    "수치": f"{growth['peg_ratio']:.2f}",
                    "전략적 해석": "성장 가속화",
                }
            )
        rev = fin.get("total_rev") or 1
        rnd_val = fin.get("rnd_expense") or 0
        rnd_ratio = (rnd_val / rev) * 100
        if rnd_ratio > 0:
            report.append(
                {
                    "분류": "수익성",
                    "항목": "R&D / Rev",
                    "수치": f"{rnd_ratio:.1f}%",
                    "전략적 해석": "기술 격차 확대",
                }
            )
        return report

    @staticmethod
    def calculate_pivot_points(last_row: pd.Series) -> Dict[str, Dict[str, float]]:
        h_v, l_v, c_v = (
            float(last_row["High"]),
            float(last_row["Low"]),
            float(last_row["Close"]),
        )
        pivot = (h_v + l_v + c_v) / 3
        range_hl = h_v - l_v
        return {
            "Classic": {
                "P": pivot,
                "S1": 2 * pivot - h_v,
                "R1": 2 * pivot - l_v,
                "S2": pivot - range_hl,
                "R2": pivot + range_hl,
            }
        }

    @staticmethod
    def generate_strategic_analysis(
        ticker: str, last_p: float, df: pd.DataFrame, market_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """[Strategic Analysis v3.3] 풍부한 전문가적 서사 복원"""
        ema12 = df["Close"].ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = df["Close"].ewm(span=26, adjust=False).mean().iloc[-1]
        macd_val, rsi, bb, vol = (
            ema12 - ema26,
            FactorEngine.calculate_rsi(df),
            FactorEngine.calculate_bb_stats(df),
            FactorEngine.analyze_volume_energy(df),
        )
        p_val = (df["High"].iloc[-1] + df["Low"].iloc[-1] + df["Close"].iloc[-1]) / 3

        pos = f"현재가는 {last_p:,.2f}로, 피벗({p_val:,.2f}) 근처에서 방향성을 모색 중입니다. "
        if bb["width"] < 0.05:
            pos += "볼린저 밴드 폭이 좁아진 '스퀴즈' 국면으로 변동성 폭발 임박."
        else:
            pos += f"볼린저 밴드 {'상단' if bb['pos_pct'] > 50 else '하단'} {bb['pos_pct']:.1f}% 지점에서 지지력을 시험 중입니다."

        trend = "추세 추종: 완만한 우상향 흐름 유지."
        if macd_val < 0 and 40 < rsi < 50:
            trend = "지지 구축: MACD 음의 영역이나 RSI 견고한 '건전한 조정' 단계."
        elif macd_val > 0 and rsi > 70:
            trend = "단기 과열: 강한 매수세이나 기술적 조정 가능성에 유의."

        supply = f"거래량 {vol['ratio']}% ({vol['nature']}). {'매수 우위' if last_p > p_val else '매도 압력 우세'}."
        action = f"{p_val:,.2f}선 지지 여부를 확인하며 분할 {'매도' if rsi > 70 else '매수' if rsi < 35 else '관망'} 대응이 유리합니다."
        return {"position": pos, "trend": trend, "supply": supply, "action": action}

    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame) -> List[Dict[str, Any]]:
        if df.empty:
            return []
        cp = float(df["Close"].iloc[-1])
        res = []
        for p in [20, 50, 200]:
            if len(df) >= p:
                sma = df["Close"].rolling(window=p).mean().iloc[-1]
                res.append(
                    {
                        "period": f"MA{p}",
                        "value": round(float(sma), 2),
                        "action": "Buy" if cp > sma else "Sell",
                    }
                )
        return res
