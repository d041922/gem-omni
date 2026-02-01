import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# --- OMNI Intelligence Core ---
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

os.environ["NO_COLOR"] = "1"

from agents.dev_tools.intelligence_ingester import IntelligenceIngester  # noqa: E402
from agents.dev_tools.blueprint_maker import BlueprintMaker  # noqa: E402

class OMNIDevPilot:
    """
    [OMNI-DevPilot v6.2: Critical Briefing Core]
    불필요한 작업은 거부하고, 마스터에게 간결하고 명확한 현황만 보고합니다.
    """
    def __init__(self):
        self.root_dir = Path(os.getcwd())
        self.python_exe = sys.executable
        self.report_file = self.root_dir / "LIVE_REPORT.md"
        self.state_file = self.root_dir / "memory" / "task_states" / "current_mission.json"
        self.ingester = IntelligenceIngester()
        self.maker = BlueprintMaker()
        self._init_files()

    def _init_files(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(f"# 💎 OMNI Live Report\n\n**보고 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n")

    def log_to_master(self, title: str, content: str, level: str = "INFO"):
        icon = "🔵" if level == "INFO" else "🟢" if level == "SUCCESS" else "🟠"
        with open(self.report_file, "a", encoding="utf-8") as f:
            f.write(f"\n## {icon} {title}\n\n{content}\n\n---\n")
        print(f"[{level}] {title} ... (Log Updated)")

    def update_state(self, phase: str, status: str, progress: int = 0):
        state = {"mission": getattr(self, 'current_mission', "Evolution"), "phase": phase, "status": status, "progress": progress}
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)

    async def run_autonomous_flow(self, intent: str):
        self.current_mission = intent
        self.log_to_master("미션 개시", f"**과업**: {intent}", "INFO")

        # 1. 지능 소화
        report_path = self.root_dir / "memory" / "research_repo" / "mcp_master_report.md"
        digested = self.ingester.digest_report(str(report_path))
        
        # 2. 설계 및 비판적 판단
        self.update_state("DESIGN", "Evaluating implementation necessity", 60)
        track_id = f"mission-{datetime.now().strftime('%m%d-%H%M')}"
        spec, plan, briefing = self.maker.create_conductor_files(digested, intent, track_id)
        
        if plan == "N/A (No changes required)":
            self.log_to_master("최적화 확인", briefing, "SUCCESS")
            self.update_state("COMPLETED", "System is already optimized", 100)
            print("\n✨ [STATUS: OPTIMIZED] No changes needed. Check LIVE_REPORT.md")
        else:
            self.log_to_master("시스템 설계도", briefing + "\n\n### 상세 공정 계획\n" + plan, "INFO")
            self.update_state("WAITING", "Awaiting confirmation", 80)
            print(f"\n🚀 [STATUS: READY] Plan generated: {track_id}. Review LIVE_REPORT.md")

if __name__ == "__main__":
    pilot = OMNIDevPilot()
    intent = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "데브툴 고도화"
    asyncio.run(pilot.run_autonomous_flow(intent))