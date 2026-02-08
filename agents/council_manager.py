"""
OMNI Council Manager (v1.0)
Orchestrates AI personas, sector guidelines, and prompt engineering.
Separates 'Personality' logic from 'Research' execution.
"""

import os
import yaml
from typing import Dict, Any


class CouncilManager:
    def __init__(self, template_dir: str = "agents/templates"):
        self.template_dir = template_dir
        self.personas = self._load_yaml("council_personas.yaml")
        self.sectors = self._load_yaml("sector_guidelines.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration with error handling."""
        path = os.path.join(self.template_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[CouncilManager] Failed to load {filename}: {e}")
            return {}

    def get_sector_guide(self, biz_model: str) -> Dict[str, Any]:
        """Retrieve sector-specific analysis guidelines."""
        # Default to General if model not found or explicitly Unknown
        if not biz_model or biz_model not in self.sectors:
            return self.sectors.get("General", {})
        return self.sectors.get(biz_model, {})

    def build_debate_prompt(
        self, normalized_facts: str, pos_str: str, history_str: str, biz_model: str
    ) -> str:
        """Dynamically construct the Council Debate Prompt."""

        # 1. Load Persona Configuration
        meta = self.personas.get("council_meta", {})
        agents = self.personas.get("agents", {})
        rules = self.personas.get("debate_rules", [])

        # 2. Load Sector Context (The Edge)
        sector_guide = self.get_sector_guide(biz_model)
        sector_narrative = sector_guide.get("narrative", "섹터별 특이사항 없음.")
        focus_metrics = ", ".join(sector_guide.get("focus_metrics", []))

        # 3. Format Components
        agents_str = "\n".join(
            [
                f"- {a['name']}: {', '.join(a['focus'])} 관점. (규칙: {'; '.join(a['rules'])})"
                for a in agents.values()
            ]
        )

        rules_str = "\n".join([f"{i + 1}. {r}" for i, r in enumerate(rules)])

        # 4. Assembly
        prompt = f"""
        당신은 {meta.get("name", "OMNI Council")}의 {meta.get("role", "CIO")}입니다.
        목표: {meta.get("goal", "Provide actionable advice")}
        
        [Part 1: The Context]
        분석 대상 섹터 유형: {biz_model}
        ★ 섹터 가이드라인 (Sector Narrative):
        "{sector_narrative}"
        ★ 중점 검토 지표: {focus_metrics}

        [Part 2: The Data]
        -- Fact Sheet (Accuracy Lock) --
        {normalized_facts}
        
        -- Master's Position --
        {pos_str}
        
        -- Past Analysis (Post-Mortem) --
        {history_str}
        
        [Part 3: The Council (Agents)]
        {agents_str}
        
        [Part 4: Debate Rules]
        {rules_str}
        
        [Part 5: Output Format]
        반드시 다음 JSON 형식을 유지하십시오 (한글 작성):
        {{
            "verdict": "STRONG BUY | BUY | HOLD | SELL | STRONG SELL",
            "ai_summary": "위원회의 토론 요약 (에이전트간의 충돌 과정을 생생하게 묘사)",
            "reason": "최종 결론의 핵심 근거 (수치와 피벗 포인트 인용 필수)",
            "action_plan": "매수/매도 트리거 가격(피벗 기준)을 포함한 구체적 전략",
            "battle_ground": "논리 충돌의 핵심 주제",
            "portfolio_advice": "마스터 포지션 맞춤형 조언"
        }}
        """
        return prompt
