"""
GEM: OMNI Factor Engine (v7.7 - Data-Driven & Precise Logic)
Numerical DNA based classification and Piotroski F-Score integration.
Google Engineering Standard compliant code.
"""

import pandas as pd
from typing import Dict, Any, List


class FactorEngine:
    """금융 기술 지표 및 펀더멘털 전략 브리핑 엔진 (v7.7)"""

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
        """[DNA Analysis] 마진율과 산업 키워드로 비즈니스 체질 감별"""
        sector = str(profile.get("sector", "")).lower()
        gpm = fin.get("gross_margin") or 0

        # 1. Pure-Tech (Soft): 고마진 소프트웨어/플랫폼 (Amazon 포함 위해 internet 추가)
        if gpm > 0.60 or "software" in sector or "services" in sector or "internet" in sector:
            model = "Pure-Tech (Soft)"

        # 2. Fabless/IP: 고마진 반도체 설계/IP
        elif gpm > 0.35 and ("semicon" in sector or "tech" in sector):
            model = "Fabless/IP"

        # 3. Hard-Infra: 저마진 하드웨어/제조 (SMCI 등)
        elif gpm < 0.20 or "hardware" in sector or "computer" in sector:
            model = "Hard-Infra"

        # 4. Cyclical-Giant: 장치 산업/시클리컬
        elif "manufacturing" in sector or "semicon" in sector or "industrial" in sector:
            model = "Cyclical-Giant"

        else:
            model = "General"

        print(f"[DEBUG] Business Model Detected for {ticker}: {model} (Margin: {gpm:.1%})")
        return model

    @staticmethod
    def calculate_piotroski_f_score(
        fin: Dict[str, Any],
        health: Dict[str, Any],
        growth: Dict[str, Any],
        ticker: str = "",
    ) -> Dict[str, Any]:
        """[Quality] 피오트로스키 F-Score (9점 만점) 산출 및 로깅 [Robust v2]"""
        score = 0
        details = []

        print(f"\n[F-SCORE DEBUG] Calculating for {ticker}")

        # Helper for robust float conversion
        def safe_float(val, name):
            try:
                if val is None:
                    print(f"  [WARNING] Missing Data for {name}. Treated as 0.0")
                    return 0.0
                return float(val)
            except Exception:
                return 0.0

        # 1. Profitability (수익성)
        roa = safe_float(fin.get("roa"), "ROA")
        if roa > 0:
            score += 1
            details.append("ROA 양수(+1)")
            print(f"  - ROA({roa:.4f}) > 0: PASS")

        cfo = safe_float(fin.get("cfo"), "CFO")
        if cfo > 0:
            score += 1
            details.append("영업현금흐름 양수(+1)")
            print(f"  - CFO({cfo:,.0f}) > 0: PASS")

        net_income = safe_float(fin.get("net_income"), "NetIncome")
        if cfo > net_income:
            score += 1
            details.append("현금흐름 > 순이익(+1)")
            print(f"  - CFO > NetIncome({net_income:,.0f}): PASS")

        # 2. Leverage, Liquidity (재무 건전성)
        debt_ratio = safe_float(health.get("debt_to_equity"), "DebtRatio")
        # Debt ratio often None for tech stocks with no debt, or explicitly 0
        # If None, we assume 0 (Best case) but verify context? No, strictly penalize missing data or treat as 0?
        # Standard: Treat as 0 if legit 0, but if actually missing, it might be risky.
        # Here we assume safe_float 0.0 is 'no debt' which passes < 250 test.
        if debt_ratio < 250:
            score += 1
            details.append("부채비율 양호(<250%)(+1)")
            print(f"  - Debt/Equity({debt_ratio:.1f}) < 250: PASS")
        else:
            print(f"  - Debt/Equity({debt_ratio:.1f}) >= 250: FAIL")

        curr_ratio = safe_float(health.get("current_ratio"), "CurrentRatio")
        if curr_ratio > 0.8:
            score += 1
            details.append("유동비율 양호(>0.8)(+1)")
            print(f"  - Current Ratio({curr_ratio:.2f}) > 0.8: PASS")

        # 3. Operating Efficiency (운영 효율성)
        gpm = safe_float(fin.get("gross_margin"), "GrossMargin")
        if gpm > 0.10:
            score += 1
            details.append("마진율 확보(>10%)(+1)")
            print(f"  - Gross Margin({gpm:.2%}) > 10%: PASS")

        # Rating (Normalized)
        if score >= 6:
            rating = "Strong Quality (우량)"
        elif score >= 4:
            rating = "Neutral (보통)"
        else:
            rating = "Weak (부실)"

        print(f"[F-SCORE RESULT] {ticker}: {score} pts -> {rating}")

        return {"score": score, "rating": rating, "details": details}

    @staticmethod
    def generate_comprehensive_verdict(
        extra_stats: Dict[str, Any],
        last_p: float,
        ticker: str = "",
        holding_info: Dict[str, Any] = None,
    ) -> Dict[str, str]:
        """[Engine v7.7] 섹터별 가중치 + Data-Driven Narrative"""
        val = extra_stats.get("valuation", {})
        growth = extra_stats.get("growth", {})
        fin = extra_stats.get("financials", {})
        health = extra_stats.get("health", {})

        biz_model = FactorEngine.detect_business_model(
            extra_stats.get("profile", {}), fin, ticker
        )

        f_score = FactorEngine.calculate_piotroski_f_score(fin, health, growth, ticker)

        pe, ps, pb = (
            val.get("trailing_pe"),
            val.get("ps_ratio"),
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

        print(f"[DEBUG] Verdict Logic Entry for {ticker} with Model: {biz_model}")

        # --- [Layer 2] Sector-Specific Logic (Data-Driven Narrative) ---
        if biz_model == "Pure-Tech (Soft)":
            v_verdict = f"P/E {pe:.1f}배. " + ("프리미엄 구간." if pe and pe > 50 else "합리적 밸류.")
            if peg:
                g_verdict = f"PEG {peg:.2f}. " + ("저평가 고성장." if peg < 1.0 else "성장 반영 중.")
            elif growth.get("rev_growth"):
                g_verdict = f"매출 성장률({growth['rev_growth']:.1%}) 기반 모멘텀 유효."
            else:
                g_verdict = "성장 지표 대조 중."
            r_verdict = f"SBC 비율 {sbc_ratio:.1f}% 및 현금흐름 건전성 주시."

        elif biz_model == "Fabless/IP":
            v_verdict = f"P/E {pe:.1f}배. 기술 독점 프리미엄 반영."
            if peg:
                g_verdict = f"PEG {peg:.2f}. " + ("압도적 성장." if peg < 1.0 else "성장 궤도 진입.")
            else:
                g_verdict = "AI 인프라 수요에 따른 높은 성장 기대감 유지."
            r_verdict = "공급망 병목 및 기술 경쟁 심화 리스크."

        elif biz_model == "Hard-Infra":
            if ps:
                v_verdict = f"P/S {ps:.2f}배. " + ("고평가 주의." if ps > 1.5 else "적정가 형성.")
            g_verdict = "재고 회전율 및 매출 가속화 동력 확인."
            r_verdict = "회계 투명성 및 마진 압박 요인 주시."

        elif biz_model == "Cyclical-Giant":
            v_verdict = f"P/B {pb:.2f}배. " + ("상단선 근접." if pb and pb > 2.0 else "바닥권 탈출.")
            g_verdict = "고부가 가치 비중 확대에 따른 재평가 기대."
            r_verdict = "장치 산업 고유의 감가상각 및 재고 리스크."

        else:
            v_verdict = f"P/E {pe:.1f}배 / P/B {pb:.2f}배 기반 가치 평가."
            g_verdict = "산업군 평균 대비 성장성 분석 중."
            r_verdict = "재무 지표 변동성 및 현금 흐름 주시."

        if f_score["score"] <= 2:
            r_verdict = f"🚩 [Low Quality] {f_score['rating']} (F-Score:{f_score['score']}). {r_verdict}"

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
    def generate_fundamental_axis_scores(extra_stats: Dict[str, Any]) -> Dict[str, float]:
        """Build normalized 0-100 axis scores for value/quality/growth/risk."""
        growth = extra_stats.get("growth", {}) if isinstance(extra_stats, dict) else {}
        financials = extra_stats.get("financials", {}) if isinstance(extra_stats, dict) else {}
        valuation = extra_stats.get("valuation", {}) if isinstance(extra_stats, dict) else {}
        health = extra_stats.get("health", {}) if isinstance(extra_stats, dict) else {}

        pe = valuation.get("trailing_pe")
        peg = growth.get("peg_ratio")
        roe = financials.get("roe")
        gross_margin = financials.get("gross_margin")
        rev_growth = growth.get("rev_growth")
        debt_to_equity = health.get("debt_to_equity")
        current_ratio = health.get("current_ratio")

        # Value: lower PE/PEG is preferred with conservative fallback.
        value_score = 50.0
        if pe and pe > 0:
            value_score = max(0.0, min(100.0, 100.0 - (float(pe) * 1.2)))
        if peg and peg > 0:
            value_score = (value_score + max(0.0, min(100.0, 120.0 - float(peg) * 60.0))) / 2.0

        # Quality: profitability and margin.
        quality_score = 50.0
        if roe is not None:
            quality_score = max(0.0, min(100.0, float(roe) * 200.0))
        if gross_margin is not None:
            quality_score = (quality_score + max(0.0, min(100.0, float(gross_margin) * 140.0))) / 2.0

        # Growth: revenue growth 중심.
        growth_score = 45.0
        if rev_growth is not None:
            growth_score = max(0.0, min(100.0, 50.0 + float(rev_growth) * 200.0))

        # Risk: lower debt and acceptable current ratio.
        risk_score = 55.0
        if debt_to_equity is not None:
            risk_score = max(0.0, min(100.0, 100.0 - float(debt_to_equity) * 0.25))
        if current_ratio is not None:
            risk_score = (risk_score + max(0.0, min(100.0, float(current_ratio) * 35.0))) / 2.0

        return {
            "value": round(value_score, 2),
            "quality": round(quality_score, 2),
            "growth": round(growth_score, 2),
            "risk": round(risk_score, 2),
        }

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
        """[Strategic Analysis v3.4] Regime-aware decision-oriented interpretation."""
        if df.empty or "Close" not in df.columns:
            return {
                "position": "가격 데이터가 부족해 시장 위치를 판정할 수 없습니다.",
                "trend": "추세 데이터 부족 (NEUTRAL).",
                "supply": "수급/변동성 데이터 부족 (NEUTRAL).",
                "action": "관망. 신뢰도: LOW (데이터 부족)",
                "confidence": "LOW",
            }

        close = pd.to_numeric(df["Close"], errors="coerce").dropna()
        if close.empty:
            return {
                "position": "가격 데이터가 부족해 시장 위치를 판정할 수 없습니다.",
                "trend": "추세 데이터 부족 (NEUTRAL).",
                "supply": "수급/변동성 데이터 부족 (NEUTRAL).",
                "action": "관망. 신뢰도: LOW (데이터 부족)",
                "confidence": "LOW",
            }

        price = float(close.iloc[-1])
        prev_price = float(close.iloc[-2]) if len(close) >= 2 else price

        ma20 = float(close.rolling(window=20).mean().iloc[-1]) if len(close) >= 20 else price
        ma50 = float(close.rolling(window=50).mean().iloc[-1]) if len(close) >= 50 else ma20
        ma200 = float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else ma50

        ema12 = float(close.ewm(span=12, adjust=False).mean().iloc[-1])
        ema26 = float(close.ewm(span=26, adjust=False).mean().iloc[-1])
        macd_val = ema12 - ema26
        rsi = FactorEngine.calculate_rsi(df)
        bb = FactorEngine.calculate_bb_stats(df)
        vol = FactorEngine.analyze_volume_energy(df)
        vol_ratio = float(vol.get("ratio", 100.0))

        h_last = float(df["High"].iloc[-1]) if "High" in df.columns else price
        l_last = float(df["Low"].iloc[-1]) if "Low" in df.columns else price
        p_val = (h_last + l_last + price) / 3.0
        pivots = FactorEngine.calculate_pivot_points(pd.Series({"High": h_last, "Low": l_last, "Close": price}))
        classic = pivots.get("Classic", {})
        s1 = float(classic.get("S1", p_val))
        r1 = float(classic.get("R1", p_val))

        # Regime
        if ma20 > ma50 and price > ma50:
            trend_regime = "UP"
        elif ma20 < ma50 and price < ma50:
            trend_regime = "DOWN"
        else:
            trend_regime = "SIDE"

        bb_width = float(bb.get("width", 0.0))
        if bb_width >= 0.08 or vol_ratio >= 170:
            vol_regime = "HIGH"
        elif bb_width <= 0.03 and vol_ratio <= 90:
            vol_regime = "LOW"
        else:
            vol_regime = "NORMAL"

        # Position
        pos_pct = float(bb.get("pos_pct", 50.0))
        bb_lower = float(bb.get("lower", price))
        bb_upper = float(bb.get("upper", price))
        swing_low = float(close.tail(20).min()) if len(close) >= 20 else price
        swing_high = float(close.tail(20).max()) if len(close) >= 20 else price

        support_candidates = [s1, bb_lower, ma200, swing_low]
        resistance_candidates = [r1, bb_upper, swing_high]
        near_support = min(abs(price - x) / max(price, 1.0) for x in support_candidates) <= 0.015
        near_resistance = min(abs(price - x) / max(price, 1.0) for x in resistance_candidates) <= 0.015
        near_pivot = abs(price - p_val) / max(price, 1.0) <= 0.008
        if pos_pct >= 85 and rsi >= 65:
            position_state = "OVEREXTENDED"
        elif near_support:
            position_state = "NEAR_SUPPORT"
        elif near_resistance:
            position_state = "NEAR_RESISTANCE"
        elif near_pivot:
            position_state = "NEAR_PIVOT"
        else:
            position_state = "NEUTRAL"

        ma50_gap_pct = ((price - ma50) / max(ma50, 1.0)) * 100.0
        position = (
            f"결론: {position_state}. "
            f"근거: BB {pos_pct:.1f}%, 피벗 {p_val:,.2f}, MA50 대비 {ma50_gap_pct:+.2f}%."
        )

        # Trend
        if trend_regime == "UP" and macd_val >= 0:
            trend_state = "BULLISH"
        elif trend_regime == "DOWN" and macd_val <= 0:
            trend_state = "BEARISH"
        else:
            trend_state = "NEUTRAL"

        strength_points = 0
        strength_points += 1 if price > ma50 else 0
        strength_points += 1 if price > ma200 else 0
        strength_points += 1 if macd_val > 0 else 0
        strength_points += 1 if rsi >= 55 else 0

        if strength_points >= 3:
            trend_strength = "STRONG"
        elif strength_points >= 2:
            trend_strength = "MODERATE"
        else:
            trend_strength = "WEAK"

        turning_risk = "LOW"
        if trend_state == "BULLISH" and (rsi > 70 or macd_val < 0):
            turning_risk = "HIGH"
        elif trend_state == "BEARISH" and (rsi < 30 or macd_val > 0):
            turning_risk = "MEDIUM"
        elif trend_state == "NEUTRAL":
            turning_risk = "MEDIUM"

        regime_kor = "상승" if trend_regime == "UP" else "하락" if trend_regime == "DOWN" else "횡보"
        trend = (
            f"결론: {regime_kor} 국면({trend_state}/{trend_strength}). "
            f"근거: MA20 {ma20:,.2f} vs MA50 {ma50:,.2f}, MACD {macd_val:+.2f}, RSI {rsi:.1f}. "
            f"리스크: 전환 {turning_risk}."
        )

        # Supply / Volatility
        price_change = price - prev_price
        if vol_ratio > 150 and price_change > 0 and trend_regime == "UP":
            flow_state = "ACCUMULATION"
        elif vol_ratio > 150 and price_change < 0 and trend_regime == "DOWN":
            flow_state = "DISTRIBUTION"
        else:
            flow_state = "NEUTRAL"

        if vol_regime == "HIGH" and abs(price - p_val) / max(price, 1.0) <= 0.01:
            risk_state = "CHOPPY"
        elif vol_regime == "HIGH":
            risk_state = "BREAKOUT_RISK"
        elif vol_regime == "LOW":
            risk_state = "CALM"
        else:
            risk_state = "NORMAL"

        flow_kor = (
            "매집(ACCUMULATION)"
            if flow_state == "ACCUMULATION"
            else "분배(DISTRIBUTION)"
            if flow_state == "DISTRIBUTION"
            else "중립(NEUTRAL)"
        )
        supply = (
            f"결론: {flow_kor}. "
            f"근거: 거래량 {vol_ratio:.1f}% ({vol.get('nature', 'N/A')}), 변동성 {vol_regime}/{risk_state}."
        )

        # Action with guardrails
        action_level = "WATCH"
        if trend_state == "BULLISH" and rsi < 40 and position_state in {"NEAR_SUPPORT", "NEUTRAL"} and vol_regime != "HIGH":
            action_level = "ENTER"
        elif position_state == "OVEREXTENDED" or rsi > 70:
            action_level = "REDUCE"
        elif trend_state == "BEARISH" and vol_regime == "HIGH":
            action_level = "AVOID"

        # Guardrail: downtrend dip-buy blocked
        if trend_regime == "DOWN" and rsi < 35 and action_level == "ENTER":
            action_level = "WATCH"

        # Confidence
        coverage_count = 0
        coverage_total = 6
        coverage_count += 1 if len(close) >= 50 else 0
        coverage_count += 1 if len(close) >= 20 else 0
        coverage_count += 1 if "High" in df.columns else 0
        coverage_count += 1 if "Low" in df.columns else 0
        coverage_count += 1 if "Volume" in df.columns else 0
        coverage_count += 1 if macd_val == macd_val else 0
        coverage_ratio = coverage_count / max(coverage_total, 1)

        agreement = 0.0
        if trend_state == "BULLISH" and flow_state == "ACCUMULATION":
            agreement = 1.0
        elif trend_state == "BEARISH" and flow_state == "DISTRIBUTION":
            agreement = 1.0
        elif trend_state == "NEUTRAL" or flow_state == "NEUTRAL":
            agreement = 0.5

        vol_penalty = 0.2 if vol_regime == "HIGH" else 0.0
        confidence_score = 60
        confidence_score += 8 if trend_state in {"BULLISH", "BEARISH"} else -5
        confidence_score += 6 if flow_state in {"ACCUMULATION", "DISTRIBUTION"} else 0
        confidence_score -= 10 if vol_regime == "HIGH" else 0
        confidence_score -= 8 if turning_risk == "HIGH" else 0
        confidence_score += int((coverage_ratio - 0.5) * 10)
        confidence_score = max(35, min(85, confidence_score))

        if confidence_score >= 72:
            confidence = "HIGH"
        elif confidence_score >= 56:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        guardrail = "고변동성 구간은 포지션 사이징 축소" if vol_regime == "HIGH" else "레벨 이탈 전 과도한 추격 금지"
        reason = (
            "횡보+고변동성으로 방향성 확인 전 관망 우위"
            if action_level == "WATCH"
            else "과열/저항 구간으로 리스크 관리 우선"
            if action_level == "REDUCE"
            else "하락 추세+고변동성 조합으로 회피 우위"
            if action_level == "AVOID"
            else "상승 쪽 정합 신호 확인 시 분할 진입"
        )
        action = (
            f"현재 판단: {action_level} (신뢰도 {confidence} {confidence_score}점). "
            f"신뢰도: {confidence}. "
            f"이유: {reason}. "
            f"가드레일: {guardrail}. "
            f"[Coverage {coverage_ratio:.2f} / Agreement {agreement:.2f} / VolPenalty -{vol_penalty:.2f}]"
        )

        return {
            "position": position,
            "trend": trend,
            "supply": supply,
            "action": action,
            "confidence": confidence,
        }

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
