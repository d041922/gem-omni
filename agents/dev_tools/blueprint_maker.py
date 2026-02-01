"""
Blueprint Maker [Dev Tool] v4.1: Strategic Architect
Critical Thinking Edition: Decides whether implementation is actually needed.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List

class BlueprintMaker:
    def __init__(self):
        self.root_dir = Path(os.getcwd())

    def create_conductor_files(self, digested_data: Dict, target_feature: str, track_id: str):
        """
        [Critical Evaluation]
        리서치 결과와 현재 상태를 대조하여 실제 공사 여부를 결정합니다.
        """
        targets = digested_data.get("suggested_files", [])
        best_practices = digested_data.get("best_practices", [])
        
        # 1. 개선 필요성 판단
        if not targets and not best_practices:
            briefing = f"✅ **[최적화 확인]** {target_feature}\n\n"
            briefing += "분석 결과, 시스템은 이미 최상의 표준을 준수하고 있습니다. **추가 수정이 불필요합니다.**"
            spec = f"# Spec: {target_feature}\n\n## 결과: 최적화 완료"
            plan = "N/A (No changes required)"
            return spec, plan, briefing

        # 2. 개선이 필요한 경우
        briefing = self._generate_master_briefing(digested_data, target_feature)
        spec = f"# Spec: {target_feature} (Track: {track_id})\n\n## 공사 범위\n" + "\n".join([f"- `{t}`" for t in targets])
        
        plan = f"# Plan: {target_feature}\n\n## Phase 1: 구현\n"
        for i, t in enumerate(targets):
            plan += f"- [ ] Task {i+1}: {t} 파일 수정\n"
        
        return spec, plan, briefing

    def _generate_master_briefing(self, data: Dict, feature: str) -> str:
        res = f"💎 **[미션 분석]** {feature}\n"
        res += f"🚀 **[핵심 기술]** {', '.join([bp['feature'] for bp in data.get('best_practices', [])])}\n"
        res += f"🏠 **[수정 대상]** {', '.join(data.get('suggested_files', []))}\n"
        return res

if __name__ == "__main__":
    print("✨ BlueprintMaker v4.1 Fixed.")
