"""
[Universal Dev-Pilot]
Any Project, Any Domain - Same Master Quality.
이 파일은 어떤 프로젝트 폴더에 복사해도 즉시 개발 환경을 검수하고 설계할 수 있는 범용 도구입니다.
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 PATH에 추가 (모듈 호출용)
sys.path.append(os.getcwd())

from agents.dev_tools.pilot_controller import DevPilot
from agents.dev_tools.blueprint_maker import BlueprintMaker

def run_audit():
    """시스템 헬스 체크 및 품질 검수 (Ruff, Integrity)"""
    pilot = DevPilot()
    pilot.run_full_audit()

def run_plan(feature_name):
    """신규 기능 설계 및 Conductor 트랙 생성"""
    print(f"🛠️  Architecting feature: {feature_name}...")
    maker = BlueprintMaker()
    track_id = feature_name.lower().replace(" ", "-")[:10] + "-track"
    
    # 설계 파일 생성
    spec, plan = maker.create_conductor_files("Universal Context", feature_name, track_id)
    
    track_dir = Path(f"conductor/tracks/{track_id}")
    track_dir.mkdir(parents=True, exist_ok=True)
    
    with open(track_dir / "spec.md", "w", encoding="utf-8") as f:
        f.write(spec)
    with open(track_dir / "plan.md", "w", encoding="utf-8") as f:
        f.write(plan)
    
    print(f"✅ Blueprint created at: {track_dir}")

def main():
    if len(sys.argv) < 2:
        print("🚀 Universal Dev-Pilot Active.")
        print("Usage:")
        print("  .\\venv\\Scripts\\python scripts/dev_pilot.py --audit          : 품질 및 무결성 검수")
        print("  .\\venv\\Scripts\\python scripts/dev_pilot.py --plan [Name]    : 신규 기능 설계")
        return

    cmd = sys.argv[1]
    if cmd == "--audit":
        run_audit()
    elif cmd == "--plan":
        name = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "New Task"
        run_plan(name)

if __name__ == "__main__":
    main()
