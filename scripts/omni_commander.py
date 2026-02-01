"""
[GEM: OMNI] Project Master Commander
Project Name: "행복한 나" (Happy Me)
Master Orchestrator for Finance, Health, Growth, and Harmony.
"""
import sys
import subprocess
from pathlib import Path

def run_finance_module():
    """재정(Finance) 모듈 실행"""
    print("💰 [OMNI-Finance] Launching Wealth Management System...")
    python_exe = Path("venv/Scripts/python.exe")
    if not python_exe.exists():
        python_exe = "python"
    subprocess.run([str(python_exe), "scripts/finance_commander.py"])

def run_dev_audit():
    """시스템 품질 검수 (범용 Dev-Pilot 호출)"""
    print("🛠️ [OMNI-Dev] Running System Health Check...")
    python_exe = Path("venv/Scripts/python.exe")
    if not python_exe.exists():
        python_exe = "python"
    subprocess.run([str(python_exe), "scripts/dev_pilot.py", "--audit"])

def main():
    print("🌟 [GEM: OMNI] Project 'Happy Me' - Operational Center")
    print("-" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/omni_commander.py --finance   : 재정/자산 관리 실행")
        print("  python scripts/omni_commander.py --audit     : 시스템 품질 검수")
        print("  python scripts/omni_commander.py --all       : 전체 시스템 체크")
        return

    mode = sys.argv[1]
    if mode == "--finance":
        run_finance_module()
    elif mode == "--audit":
        run_dev_audit()
    elif mode == "--all":
        run_dev_audit()
        run_finance_module()
    else:
        print(f"⚠️  Unknown OMNI module: {mode}")

if __name__ == "__main__":
    main()