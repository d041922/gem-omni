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
        self,
        normalized_facts: str,
        pos_str: str,
        history_str: str,
        biz_model: str,
        agent_contexts: Dict[str, str],
    ) -> str:
        """Dynamically construct the Council Debate Prompt v4.1."""

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
        
        [Part 1: The Context & Sector DNA]
        분석 대상 섹터 유형: {biz_model}
        ★ 섹터 가이드라인: "{sector_narrative}"
        ★ 중점 검토 지표: {focus_metrics}

        [Part 2: Specialized Data Packets (Expert Weapons)]
        각 전문가는 본인에게 배정된 데이터 패킷을 주력 무기로 삼아 논리를 전개하십시오.
        - 매크로 전략가 전용 데이터: {agent_contexts.get("macro")}
        - 퀀트 분석가 전용 데이터: {agent_contexts.get("quant")}
        - 데블스 애드버킷 전용 데이터: {agent_contexts.get("devil")}
        - 정보 수집가 전용 데이터: {agent_contexts.get("info")}
        
        [Part 3: Master's Context]
        -- 현 포지션: {pos_str}
        -- 과거 분석: {history_str}
        
        [Part 4: The Council & Debate Rules]
        {agents_str}
        
        규정:
        {rules_str}
        10. **Calculator Protocol**: 데이터 패킷에 포함된 `RR_Ratio`나 `Z_Score` 뒤에 붙은 `[EXCELLENT]`, `[BAD]` 등의 판정 태그는 시스템이 정밀 계산한 결과입니다. 이를 무시하고 스스로 재해석하여 반대 결론을 내리지 마십시오. 판정 태그를 절대적 진리로 수용하십시오.
        11. **Multi-Timeframe RR**: 손익비는 단기(Tactical, R1 기준)와 중장기(Strategic, 목표가 기준)로 제공됩니다. 단기 손익비가 [BAD]여도 중장기 손익비가 [EXCELLENT]라면, "지금은 비싸지만 내려오면(눌림목) 사라"는 입체적 조언을 제공하십시오.

        [Part 5: Expression Rules - DEEP DIVE & DASHBOARD]
        본 토론은 OMNI 시스템의 핵심입니다. 다음 2단계 프로세스를 준수하십시오:
        
        1. **Deep Debate (본질)**: 'clash_table'에서는 글자 수 제한 없이 치열하게 논쟁하십시오. 상대방 논리의 허점을 데이터 패킷에 기반하여 집요하게 공격해야 합니다.
        2. **Dashboard Mapping (요약)**: 마스터를 위해 위 토론 내용을 'dashboard_clash' 섹션에 **20단어 이내의 단문**과 **신호등 아이콘(🟢🔴🟡)**으로 요약하십시오.

        [Part 6: Output Format]
        반드시 다음 JSON 형식을 유지하십시오 (한글 작성):
        {{
            "verdict": "STRONG BUY | BUY | HOLD | SELL | STRONG SELL",
            "confidence_score": "0~100% (투표 기반 확신도)",
            "headline_summary": "1초 만에 이해되는 강렬한 헤드라인 (예: 성장이 고평가를 씹어먹는 구간)",
            "clash_table": [
                {{
                    "agent": "전문가명",
                    "position": "BULL | BEAR | NEUTRAL",
                    "logic": "상세 논리 (데이터와 인과관계를 포함한 충분한 서술)",
                    "counter": "상세 반박 (상대방 주장을 무력화하는 논증)"
                }}
            ],
            "dashboard_clash": [
                {{
                    "agent": "전문가명",
                    "position": "BULL | BEAR | NEUTRAL",
                    "icon": "🟢 | 🔴 | 🟡",
                    "summary_logic": "핵심 논리 (20자 내외 요약)",
                    "summary_counter": "결정적 반박 (20자 내외 요약)"
                }}
            ],
            "master_briefing": {{
                "status": "평단가 대비 상황 (예: +3.8% 수익 중. 심리적 요새 확보)",
                "risk": "손익비 관점 리스크 (예: 먹을 폭 2% vs 물릴 폭 4%)",
                "strategy": "최종 행동 지침 (예: 177불 눌림목 대기)"
            }},
            "action_plan": {{
                "wait_price": "관망/대기 가격대",
                "entry_price": "분할 매수 진입가",
                "profit_price": "1차 익절 목표가",
                "stop_price": "손절 라인"
            }},
            "ai_summary": "위원회 토론 전체 요약 (Deep Dive용, 3문장)"
        }}
        """
        return prompt
