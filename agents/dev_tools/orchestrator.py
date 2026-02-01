import os
import sys
import asyncio
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# --- OMNI Core v41.1 (Robust Guardian) ---
current_file = Path(__file__).resolve()
root_dir = current_file.parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.dev_tools.experts import DeepResearchExpert, ExaExpert, CodeReviewerExpert
from agents.dev_tools.blueprint_maker import BlueprintMaker
from agents.dev_tools.pilot_controller import DevPilot
from agents.dev_tools.verification_logic import OMNIVerifier

class OMNI_Reporter:
    def __init__(self, report_path: Path):
        self.report_path = report_path
        self._init_report()

    def _init_report(self):
        try:
            with open(self.report_path, "w", encoding="utf-8") as f:
                f.write(f"# 📡 OMNI 가디언 관제 리포트 (v41.1)\n**미션 개시**: {datetime.now()}\n\n---\n")
        except:
            pass

    def stream_log(self, phase: str, status: str, summary: str, thought: str = "", evidence: str = ""):
        icons = {"PASS": "🟢", "FAIL": "🔴", "WARN": "⚠️", "INFO": "ℹ️", "WORK": "🔨", "TRANSFUSE": "🚑", "SKIP": "🧘"}
        icon = icons.get(status, "⚪")
        time_str = datetime.now().strftime("%H:%M:%S")
        block = f"\n### {icon} [{time_str}] **{phase}**: {summary}\n**상태**: `{status}`\n"
        if thought: block += f"\n**🧠 사고 과정**:\n{thought}\n"
        if evidence: block += f"\n<details><summary>상세 데이터</summary>\n\n```text\n{evidence}\n```\n</details>\n"
        block += "\n---\n"
        with open(self.report_path, "a", encoding="utf-8") as f:
            f.write(block)
            f.flush()
            os.fsync(f.fileno())

class OMNI_Orchestrator:
    def __init__(self):
        self.root_dir = root_dir
        self.reporter = OMNI_Reporter(self.root_dir / "LIVE_REPORT.md")
        self.researcher = DeepResearchExpert()
        self.exa = ExaExpert()
        self.reviewer = CodeReviewerExpert()
        self.maker = BlueprintMaker()
        self.pilot = DevPilot()
        self.verifier = OMNIVerifier()

    def extract_required_files(self, plan: str) -> List[str]:
        """설계도에서 파일 리스트 추출."""
        files = re.findall(r"([a-zA-Z0-9_\-/]+\.[a-zA-Z0-9]+)", plan)
        unique_files = list(set([f for f in files if "." in f and not f.startswith("pip")]))
        return unique_files

    async def run_pipeline(self, user_input: str):
        self.reporter.stream_log("Start", "INFO", "가디언 가동 (v41.1)", evidence=user_input)
        
        # --- Phase 1 ---
        spec = self.researcher.execute(user_input)
        self.reporter.stream_log("Phase 1", "PASS", "지식 확보")

        # --- Phase 2 ---
        track_id = f"v41-{datetime.now().strftime('%H%M')}"
        track_dir = self.root_dir / "conductor" / "tracks" / track_id
        track_dir.mkdir(parents=True, exist_ok=True)
        
        _, plan, _ = self.maker.create_conductor_files({"research_summary_ko": spec}, user_input, track_id)
        (track_dir / "spec.md").write_text(spec, encoding="utf-8")
        (track_dir / "plan.md").write_text(plan, encoding="utf-8")
        
        required_files = self.extract_required_files(plan)
        # 만약 설계도에서 파일을 못 찾았다면 기본값 추가
        if not required_files:
            required_files = ["result_script.py"]
            
        self.reporter.stream_log("Phase 2", "PASS", "설계서 완성", thought=f"구성 요소: {required_files}")

        # --- Phase 2.5: Idempotency Check ---
        missing_components = []
        for f_name in required_files:
            f_path = self.root_dir / f_name if not Path(f_name).is_absolute() else Path(f_name)
            # 만약 track 폴더 내부 파일이라면 track_dir 기준
            if "track-" in f_name or "v41-" in f_name:
                f_path = track_dir / Path(f_name).name
                
            if not f_path.exists() or f_path.stat().st_size < 10:
                missing_components.append(f_name)

        if not missing_components:
            # 모든 파일이 있다면 품질 검사
            main_file = self.root_dir / required_files[0]
            if not main_file.exists(): main_file = track_dir / "result_script.py" # Fallback
            
            if main_file.exists():
                pre_res = self.reviewer.validate(main_file.read_text(encoding="utf-8"), spec)
                if pre_res['score'] >= 95:
                    self.reporter.stream_log("Audit", "SKIP", "최적화 상태", thought="완벽합니다.")
                    print("🧘 [SAGE] Skip.")
                    return

        # --- Phase 3 & 4 Loop ---
        current_feedback = f"작업 시작. 전체 구성 요소를 완비하세요: {required_files}"
        target_file = None
        
        for i in range(3):
            self.reporter.stream_log(f"Cycle {i+1}", "WORK", "구현/보완 중")
            self.pilot.execute_plan(track_id, feedback=current_feedback)
            
            py_files = list(track_dir.glob("*.py"))
            if not py_files: continue
            target_file = py_files[0]
            
            res = self.reviewer.validate(target_file.read_text(encoding="utf-8"), spec)
            if res['passed']:
                self.reporter.stream_log(f"Cycle {i+1}", "PASS", "검수 합격")
                break
            else:
                self.reporter.stream_log(f"Cycle {i+1}", "LOOP", "반려", evidence=res['critique'])
                rescue = self.exa.get_rescue_samples(res['critique'])
                current_feedback = f"반려 사유: {res['critique']}\n\n{rescue}"

        # Final Verify
        if target_file:
            v_ok, v_log = self.verifier.run_script(str(target_file))
            status = "PASS" if v_ok else "FAIL"
            self.reporter.stream_log("Phase 5", status, "최종 검증", evidence=v_log)
            print(f"✅ 결과: {status}")

if __name__ == "__main__":
    mission = sys.argv[1] if len(sys.argv) > 1 else "Self-Audit"
    asyncio.run(OMNI_Orchestrator().run_pipeline(mission))