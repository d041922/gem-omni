"""
OMNI Analysis Manager (v1.1)
The Strategy Brain connecting Market Screener, News, and User Memory.
"""
from typing import Dict, Any

class AnalysisManager:
    """
    개별 종목 후보를 다각도로 검증하고 최종 투자 전략을 수립함.
    """

    def __init__(self, orchestrator, memory_manager):
        self.orchestrator = orchestrator
        self.memory_manager = memory_manager

    def analyze_candidate(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        종목 후보를 분석하여 최종 스코어 및 상태(Status) 반환.
        """
        ticker = candidate.get("ticker", "UNKNOWN")
        sector = candidate.get("sector", "Unknown")
        quant_score = candidate.get("score", 50.0)
        
        # 1. 투자 원칙 필터링 (Principle Guard)
        prefs = self.memory_manager.get_preferences()
        banned_sectors_str = prefs.get("banned_sectors", "")
        banned_sectors = [s.strip().lower() for s in banned_sectors_str.split(",") if s.strip()]
        
        if sector.lower() in banned_sectors:
            return {
                "ticker": ticker,
                "status": "filtered",
                "reason": f"투자 원칙 위반: 금지된 섹터({sector}) 종목입니다.",
                "final_score": 0.0
            }

        # 2. 기억 점수 산출 (Memory Score)
        memory_score = self._calculate_memory_score(ticker)
        
        # 3. 뉴스 점수 산출 (기본값)
        news_score = 50.0 
        
        # 4. 최종 가중치 합산 (Quant 50%, Memory 30%, News 20%)
        final_score = (quant_score * 0.5) + (memory_score * 0.3) + (news_score * 0.2)
        
        # 5. 투자 의견 결정
        verdict = "WATCH"
        if final_score >= 80:
            verdict = "STRONG BUY"
        elif final_score >= 70:
            verdict = "BUY"
        elif final_score <= 30:
            verdict = "AVOID"
        
        return {
            "ticker": ticker,
            "status": "active",
            "final_score": round(final_score, 2),
            "verdict": verdict,
            "quant_score": quant_score,
            "memory_score": memory_score,
            "news_score": news_score,
            "reason": f"퀀트({quant_score}점) 및 과거 승률({memory_score}점) 기반 결정"
        }

    def _calculate_memory_score(self, ticker: str) -> float:
        """과거 기록을 바탕으로 해당 종목에 대한 기억 점수 산출"""
        past_memories = self.memory_manager.recall(ticker=ticker, limit=5)
        
        if not past_memories:
            return 50.0
            
        total_weight = 0.0
        weighted_sum = 0.0
        
        positive_keywords = ["성공", "수익", "우상향", "success", "profit"]
        negative_keywords = ["실패", "손실", "하락", "fail", "loss"]
        
        for m in past_memories:
            importance = m.get("importance", 0.5)
            content = m.get("content", "").lower()
            
            score = 50.0
            if any(kw in content for kw in positive_keywords):
                score = 100.0
            elif any(kw in content for kw in negative_keywords):
                score = 0.0
            
            weighted_sum += score * importance
            total_weight += importance
            
        return round(weighted_sum / total_weight, 2) if total_weight > 0 else 50.0