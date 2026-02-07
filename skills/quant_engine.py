"""
GEM: OMNI Factor Engine (v6.1 - Fundamental Expert)
Advanced financial insight generation and structured fundamental reporting.
Strictly verified with Triple-Lock Pipeline.
"""

import pandas as pd
from typing import Dict, Any, List


class FactorEngine:
    """금융 기술 지표 및 펀더멘털 전략 브리핑 엔진 (v6.1)"""

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
        width = (upper.iloc[-1] - lower.iloc[-1]) / mid.iloc[-1]
        pos_pct = (
            ((curr_p - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) * 100)
            if (upper.iloc[-1] - lower.iloc[-1]) > 0
            else 50
        )
        return {
            "upper": float(upper.iloc[-1]),
            "mid": float(mid.iloc[-1]),
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
        ratio = (curr_vol / avg_vol) * 100
        price_change = df["Close"].iloc[-1] - df["Close"].iloc[-2]
        if ratio > 150:
            nature = (
                "집중 매수세 유입"
                if price_change > 0
                else "단기 차익 실현 및 매도 압력"
            )
        elif ratio < 70:
            nature = "거래량 감소 및 관망세"
        else:
            nature = "균형 잡힌 수급 흐름"
        return {"ratio": round(float(ratio), 1), "nature": nature}

    @staticmethod
    def generate_strategic_analysis(
        ticker: str, last_p: float, df: pd.DataFrame, market_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """[Strategic Analysis v3.0] 전문가용 시장 분석 보고서 생성 (완벽 복구)"""
        from skills.quant_engine import FactorEngine as FE

        ema12 = df["Close"].ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = df["Close"].ewm(span=26, adjust=False).mean().iloc[-1]
        macd_val = ema12 - ema26
        rsi = FE.calculate_rsi(df)
        bb = FE.calculate_bb_stats(df)
        vol = FE.analyze_volume_energy(df)
        p_val = (df["High"].iloc[-1] + df["Low"].iloc[-1] + df["Close"].iloc[-1]) / 3

        # 1. 시장 위치
        pos = f"현재가는 {last_p:,.2f}로, 주요 피벗선({p_val:,.2f}) 근처에서 방향성을 탐색 중입니다. "
        if bb["width"] < 0.05:
            pos += "볼린저 밴드 폭이 극도로 좁아지는 '스퀴즈' 국면으로, 강력한 변동성 확대가 예상됩니다."
        else:
            pos += f"현재 밴드 내 위치는 {bb['pos_pct']:.1f}% 수준으로 심리적 균형점에 머물고 있습니다."

        # 2. 추세 및 패턴 분석
        trend = (
            "추세 추종 국면: 지표 간 충돌 없이 가격 흐름을 완만하게 추종하고 있습니다."
        )
        if macd_val < 0 and rsi > 40 and rsi < 50:
            trend = "지표 상충 관찰: MACD는 단기 매도 신호를 보냈으나 RSI는 견고한 지지력을 유지하며 '건강한 조정' 패턴을 보입니다."
        elif macd_val > 0 and rsi > 70:
            trend = "단기 과열 국면: 시세 분출로 주요 지표가 임계치에 도달했습니다. 기술적 조정 가능성에 대비하십시오."

        # 3. 수급 및 변동성 분석
        supply = f"거래량은 평소 대비 {vol['ratio']}% 수준이며 {vol['nature']} 양상을 보입니다. "
        if last_p > p_val:
            supply += "지지선 상단에서 형성된 거래량은 반등 시 강력한 동력으로 작용할 전망입니다."
        else:
            supply += "현재 가격대 아래로 매물이 출회될 경우 변동성이 확대될 위험이 존재합니다."

        # 4. 대응 전략 제언
        action = (
            f"단기적으로 {p_val:,.2f}선의 지지 여부를 확인하며 대응하시기 바랍니다. "
        )
        if rsi > 70:
            action += "추격 매수보다는 분할 익절을 통해 수익을 확정하고 보수적으로 접근할 시점입니다."
        elif rsi < 35:
            action += "역발상 관점의 매수 진입이 유리한 구간입니다. 하방 경직성 확인 후 진입을 권장합니다."
        else:
            action += "현재의 비중을 유지하며, 주요 저항선 돌파 여부를 모니터링하는 전략이 유효해 보입니다."

        return {
            "position": pos,
            "trend": trend,
            "supply": supply,
            "action": action,
        }

    @staticmethod
    def generate_fundamental_insight(extra_stats: Dict[str, Any]) -> Dict[str, str]:
        """기존 펀더멘털 요약 로직 유지"""
        fin = extra_stats.get("financials", {})
        val = extra_stats.get("valuation", {})
        roe = fin.get("roe")
        pe = val.get("trailing_pe")
        profit_insight = (
            f"수익성 분석: ROE {(roe * 100):.1f}%로 자본 효율성이 유지되고 있습니다."
            if roe
            else "수익성 데이터 부족"
        )
        val_insight = (
            f"가치 평가: P/E {pe:.1f}배로 현재 주가는 시장 평균 대비 합리적인 수준입니다."
            if pe
            else "밸류에이션 데이터 부족 (수동 계산 권장)"
        )
        return {
            "profitability": profit_insight,
            "valuation": val_insight,
            "consensus": "시장 의견 수렴 중",
        }

    @staticmethod
    def generate_fundamental_report(
        extra_stats: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """[New] 마스터를 위한 보완된 펀더멘털 리포트 테이블 데이터 생성"""
        growth = extra_stats.get("growth", {})
        fin = extra_stats.get("financials", {})
        health = extra_stats.get("health", {})
        events = extra_stats.get("events", {})

        report = []

        # 1. 성장성 (PEG & Rev Growth)
        peg = growth.get("peg_ratio")
        if peg:
            insight = (
                "성장 가속도가 주가 상승보다 빨라 매력적"
                if peg < 1.0
                else "이익 성장세 대비 주가가 다소 고평가"
            )
            report.append(
                {
                    "분류": "성장성",
                    "항목": "PEG Ratio",
                    "수치": f"{peg:.2f}",
                    "전략적 해석": insight,
                }
            )

        rev_g = growth.get("rev_growth")
        if rev_g:
            insight = (
                "폭발적 매출 성장을 통한 시장 지배력 확대"
                if rev_g > 0.5
                else "안정적인 매출 성장 곡선 유지"
            )
            report.append(
                {
                    "분류": "성장성",
                    "항목": "Rev Growth (YoY)",
                    "수치": f"{rev_g * 100:.1f}%",
                    "전략적 해석": insight,
                }
            )

        # 2. 현금흐름 (FCF Margin)
        fcf = fin.get("fcf")
        rev = fin.get(
            "net_income"
        )  # Fallback to net income for margin calc if rev not in financials
        if fcf and rev and rev > 0:
            fcf_margin = (fcf / rev) * 100
            insight = (
                "벌어들인 이익의 상당 부분이 실제 현금으로 전환되는 구조"
                if fcf_margin > 80
                else "이익의 현금 회수 속도 모니터링 필요"
            )
            report.append(
                {
                    "분류": "현금흐름",
                    "항목": "FCF / NetIncome",
                    "수치": f"{fcf_margin:.1f}%",
                    "전략적 해석": insight,
                }
            )

        # 3. 안전성 (Debt to Equity)
        de = health.get("debt_to_equity")
        if de:
            insight = (
                "자본 대비 부채 비중이 낮아 금리 인상기에도 건전성 탁월"
                if de < 50
                else "레버리지를 활용한 공격적 경영, 부채 관리 필요"
            )
            report.append(
                {
                    "분류": "안전성",
                    "항목": "Debt-to-Equity",
                    "수치": f"{de:.1f}%",
                    "전략적 해석": insight,
                }
            )

        # 4. 이벤트 (Earnings Date)
        ed = events.get("next_earnings")
        if ed:
            from datetime import datetime

            date_str = (
                datetime.fromtimestamp(ed).strftime("%Y-%m-%d")
                if isinstance(ed, int)
                else str(ed)
            )
            report.append(
                {
                    "분류": "이벤트",
                    "항목": "Earnings Date",
                    "수치": date_str,
                    "전략적 해석": "실적 발표 전후 변동성 확대 대비 필수",
                }
            )

        return report

    @staticmethod
    def calculate_pivot_points(last_row: pd.Series) -> Dict[str, Dict[str, float]]:
        high_val, low_val, close_val = (
            float(last_row["High"]),
            float(last_row["Low"]),
            float(last_row["Close"]),
        )
        pivot = (high_val + low_val + close_val) / 3
        range_hl = high_val - low_val
        return {
            "Classic": {
                "P": pivot,
                "S1": (2 * pivot) - high_val,
                "R1": (2 * pivot) - low_val,
                "S2": pivot - range_hl,
                "R2": pivot + range_hl,
            },
            "Fibonacci": {
                "P": pivot,
                "S1": pivot - 0.382 * range_hl,
                "R1": pivot + 0.382 * range_hl,
                "S2": pivot - 0.618 * range_hl,
                "R2": pivot + 0.618 * range_hl,
            },
        }

    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame) -> List[Dict[str, Any]]:
        periods = [5, 10, 20, 50, 100, 200]
        results = []
        if df.empty:
            return []
        curr_price = float(df["Close"].iloc[-1])
        for p in periods:
            if len(df) >= p:
                sma = df["Close"].rolling(window=p).mean().iloc[-1]
                results.append(
                    {
                        "period": f"MA{p}",
                        "value": round(float(sma), 2),
                        "action": "Buy" if curr_price > sma else "Sell",
                    }
                )
        return results
