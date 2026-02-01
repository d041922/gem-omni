import re
import json
from pathlib import Path
from typing import Dict, List

class IntelligenceIngester:
    """
    [OMNI-Ingester v3.0]
    리포트에서 단순 키워드가 아닌 '전략적 차이(Gap)'와 '구현 규격'을 추출합니다.
    """
    def __init__(self):
        self.output_dir = Path("memory/research_repo")

    def digest_report(self, report_path: str) -> Dict:
        if not Path(report_path).exists():
            return {"error": "Report not found"}

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. 수정 파일 추출
        file_patterns = re.findall(r'[`\[]([a-zA-Z0-9_\-/]+\.py)[`\]]', content)
        
        # 2. 핵심 기술 및 권장 사항 (Best Practices) 추출
        # 리포트 내의 'Key Findings' 또는 'Insights' 섹션 탐색
        best_practices = []
        bp_match = re.findall(r'[*\-]\s*\*\*([^*]+)\*\*:\s*([^\n]+)', content)
        for title, desc in bp_match:
            best_practices.append({"feature": title.strip(), "description": desc.strip()})

        # 3. 코드 패턴 추출
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)

        return {
            "suggested_files": list(set(file_patterns)),
            "best_practices": best_practices[:5], # 주요 5개만
            "patterns_found": len(code_blocks),
            "raw_summary": content[:1000] # 분석용 원본 요약
        }

    def save_action_plan(self, digested_data: Dict):
        plan_path = self.output_dir / "action_plan.json"
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(digested_data, f, indent=4, ensure_ascii=False)
        return plan_path

if __name__ == "__main__":
    print("✨ Intelligence Ingester v3.0: Deep Analysis Mode Active.")
