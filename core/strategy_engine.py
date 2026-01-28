"""
Strategy Engine - 통합 전략 분석 코어
데이터(Portfolio/Market)와 규칙(IPS)을 결합하여 일관된 전략적 판단을 내리는 두뇌 모듈.
"""
import pandas as pd
import json
from typing import Dict, List, Any
from skills.policy_manager import PolicyManager
from skills.portfolio_utils import get_portfolio_summary, load_portfolio_from_session
from core.models import get_gemini_llm

class StrategyEngine:
    def __init__(self):
        self.policy_manager = PolicyManager()
        self.llm = get_gemini_llm(model_name="gemini/gemini-2.0-flash", temperature=0.2)

    def analyze_portfolio_health(self, portfolio_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        포트폴리오 건전성 진단 (Rule-based & AI Hybrid)
        IPS의 제약조건 위반 여부와 목표 비중 괴리율을 계산함.
        """
        if portfolio_df is None:
            portfolio_df = load_portfolio_from_session()
            
        if portfolio_df is None or portfolio_df.empty:
            return {"status": "error", "message": "포트폴리오 데이터가 없습니다."}

        policy = self.policy_manager.load_policy()
        constraints = policy.get('constraints', {})
        targets = policy.get('targets', {})
        
        # 1. 제약조건 검증 (Hard Rules)
        violations = []
        
        # 1-1. 단일 종목 집중도 체크
        total_value = portfolio_df['평가금액(KRW)'].sum()
        max_weight_limit = constraints.get('max_single_stock_weight', 0.20)
        
        for _, row in portfolio_df.iterrows():
            weight = row['평가금액(KRW)'] / total_value
            if weight > max_weight_limit:
                violations.append(f"⚠️ [집중도 경고] {row.get('종목명', 'Unknown')} 비중 {weight*100:.1f}% (한도 {max_weight_limit*100:.0f}%)")

        # 1-2. 현금 비중 체크 (Cash DF 필요 - 여기서는 생략 가능하거나 세션에서 가져옴)
        # TODO: 현금 데이터 연동 강화 필요

        # 2. 목표 비중 괴리율 (Gap Analysis)
        sector_gaps = {}
        target_sectors = targets.get('sectors', {})
        
        if '카테고리' in portfolio_df.columns:
            current_sectors = portfolio_df.groupby('카테고리')['평가금액(KRW)'].sum() / total_value
            
            for sector, target_pct in target_sectors.items():
                current_pct = current_sectors.get(sector, 0)
                gap = current_pct - target_pct
                # 괴리가 5%p 이상일 때만 유의미하게 봄
                if abs(gap) > 0.05:
                    status = "과비중" if gap > 0 else "저비중"
                    sector_gaps[sector] = {
                        "current": round(current_pct, 2),
                        "target": target_pct,
                        "gap": round(gap, 2),
                        "status": status
                    }

        return {
            "status": "success",
            "total_value": total_value,
            "violations": violations,
            "sector_gaps": sector_gaps,
            "policy_version": policy['meta']['last_updated']
        }

    def generate_strategic_advice(self, market_summary: str = "") -> str:
        """
        AI 기반 전략 조언 생성 (Context-Aware)
        단순 현황판독이 아닌, IPS와 의사결정 로그를 반영한 '행동 지침'을 생성.
        """
        # 1. 데이터 수집
        health_check = self.analyze_portfolio_health()
        if health_check['status'] == 'error':
            return "데이터 부족으로 전략을 수립할 수 없습니다."
            
        policy_context = self.policy_manager.get_strategy_context()
        
        # 2. 프롬프트 구성
        prompt = f"""
당신은 마스터의 전담 투자 전략가 [GEM: OMNI]입니다.
아래의 [투자 정책서(IPS)]와 [포트폴리오 진단] 결과를 바탕으로, 지금 즉시 실행해야 할 전략적 조언을 작성하세요.

{policy_context}

## 📊 현재 포트폴리오 진단 결과
- 총 자산 평가액: {health_check['total_value']:,} KRW
- 주요 위반 사항(Violations): {json.dumps(health_check['violations'], ensure_ascii=False)}
- 섹터 괴리(Gaps): {json.dumps(health_check['sector_gaps'], ensure_ascii=False)}

## 🌍 시장 상황 요약
{market_summary}

## 📝 작성 지침
1. **일관성 유지**: 과거 의사결정 로그(Context)를 참고하여, 이전에 내린 결정과 모순되지 않게 조언하세요.
2. **규칙 준수**: '위반 사항'이 있다면 최우선으로 해소하는 방안을 제시하세요.
3. **구체적 행동**: 단순히 "비중을 줄이세요"가 아니라 "XX 섹터를 약 5% 매도하여 현금을 확보하세요" 처럼 구체적으로 말하세요.
4. **어조**: 냉철하고 전략적인 참모의 톤을 유지하세요.

결과는 마크다운 형식으로 **3가지 핵심 Action Item** 위주로 요약하세요.
"""
        # 3. LLM 호출
        try:
            response = self.llm.call(messages=[{"role": "user", "content": prompt}])
            return response
        except Exception as e:
            return f"전략 생성 중 오류 발생: {str(e)}"

# 싱글톤 헬퍼
def run_strategy_engine(market_summary=""):
    engine = StrategyEngine()
    return engine.generate_strategic_advice(market_summary)
