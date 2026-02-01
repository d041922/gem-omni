import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# --- OMNI Core v37.0 (The Cynic) ---
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
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(f"# 🛰️ OMNI 자율 개선 관제소 (v37.0: The Cynic)\n**미션 개시**: {datetime.now()}\n\n---\n")

    def stream_log(self, phase: str, status: str, summary: str, thought: str = "", evidence: str = ""):
        icons = {"PASS": "🟢", "FAIL": "🔴", "WARN": "⚠️", "INFO": "ℹ️", "WORK": "🔨", "TRANSFUSE": "🚑"}
        icon = icons.get(status, "⚪")
        block = f"\n### {icon} [{datetime.now().strftime('%H:%M:%S')}] **{phase}**: {summary}\n"
        if thought: block += f"\n**🧠 에이전트 사고**: {thought}\n"
        if evidence: block += f"\n<details><summary>상세 데이터</summary>\n\n```text\n{evidence}\n```\n</details>\n"
        block += "\n---\n"
        with open(self.report_path, "a", encoding="utf-8") as f:
            f.write(block)
            f.flush()

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

    async def run_pipeline(self, user_input: str):
        self.reporter.stream_log("Phase 1", "WORK", "지식 확보 및 명세 수립")
        spec = self.researcher.execute(user_input)
        
        # Anti-TBD check
        if any(w in spec.lower() for w in ["tbd", "미정", "unable to"]):
            spec = self.researcher.execute(f"RE-RESEARCH: Previous attempt was too vague. Details needed for: {user_input}")

        track_id = f"v37-{datetime.now().strftime('%H%M')}"
        track_dir = self.root_dir / "conductor" / "tracks" / track_id
        track_dir.mkdir(parents=True, exist_ok=True)
        (track_dir / "spec.md").write_text(spec, encoding="utf-8")
        
        self.reporter.stream_log("Phase 2", "PASS", "설계서 확정", evidence=spec)
        _, plan, _ = self.maker.create_conductor_files({"research_summary_ko": spec}, user_input, track_id)
        (track_dir / "plan.md").write_text(plan, encoding="utf-8")

        current_feedback = "신규 구현 시작."
        MAX_RETRIES = 3
        target_file = None
        
        for i in range(MAX_RETRIES):
            self.reporter.stream_log(f"Cycle {i+1}", "WORK", "코드 구현", thought="Pilot이 코딩 중...")
            reasoning = self.pilot.execute_plan(track_id, feedback=current_feedback)
            self.reporter.stream_log(f"Cycle {i+1}", "INFO", "논리 설계", thought=reasoning)
            
            py_files = list(track_dir.glob("*.py"))
            if not py_files: continue
            target_file = py_files[0]
            code_txt = target_file.read_text(encoding="utf-8")
            
            # 🧐 Strict Audit
            res = self.reviewer.validate(code_txt, spec)
            if res['passed']:
                self.reporter.stream_log(f"Cycle {i+1}", "PASS", "리뷰 합격", evidence=res['critique'])
                break
            
            # 지식 수혈
            rescue = self.exa.get_rescue_samples(res['critique'])
            current_feedback = f"검수 반려 사유: {res['critique']}\n\n[코드 가이드]\n{rescue}"
            self.reporter.stream_log(f"Cycle {i+1}", "TRANSFUSE", "지식 수혈", evidence=current_feedback)

        # [CRITICAL] Final Truth Check
        if target_file:
            print("🔍 [Final Check] Performing cynical verification...")
            v_ok, v_log = self.verifier.run_script(str(target_file))
            
            if v_ok:
                self.reporter.stream_log("Phase 5", "PASS", "최종 성공", thought="물리적 실행 및 키워드 검사를 통과했습니다.", evidence=v_log)
                print(f"✅ Mission Success: {track_id}")
            else:
                self.reporter.stream_log("Phase 5", "FAIL", "최종 실패 (거짓 성공 차단)", thought="실행 로그에서 오류나 중단 흔적이 발견되었습니다.", evidence=v_log)
                print(f"❌ Mission Failed: Hidden errors detected in logs.")
        else:
            print("❌ No artifact to verify.")

if __name__ == "__main__":
    mission = sys.argv[1] if len(sys.argv) > 1 else "Self-Audit"
    asyncio.run(OMNI_Orchestrator().run_pipeline(mission))
