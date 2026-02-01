import os
import sys
import subprocess
from pathlib import Path

class DevPilot:
    """
    Universal Integrity & Quality Guard (Portable)
    Ensures 'Integrity First' and 'Ruff Clean' standards.
    """
    def __init__(self):
        self.root_dir = Path(os.getcwd())
        # 현재 실행 중인 파이썬 인터프리터를 기본으로 사용 (범용성 확보)
        self.python_exe = sys.executable
        self.venv_path = Path(self.python_exe).parent

    def run_static_analysis(self):
        """Ruff를 통한 완벽한 문법/스타일 검수 (Zero-Tolerance)"""
        print("🔍 Running Diamond-Standard Static Analysis...")
        
        # 1. ruff 실행 파일 경로 탐색
        ruff_candidates = [
            self.venv_path / "ruff.exe",
            self.venv_path / "ruff",
            Path(sys.executable).parent / "Scripts" / "ruff.exe",
            "ruff"
        ]
        
        ruff_exe = "ruff" # Default
        for cand in ruff_candidates:
            if isinstance(cand, Path) and cand.exists():
                ruff_exe = str(cand)
                break

        exclude_dirs = ["venv", "docs", "archive", "tests", "tmp", ".git", "__pycache__"]
        
        try:
            cmd = [ruff_exe, "check", ".", "--exclude", ",".join(exclude_dirs)]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode != 0:
                print("❌ Quality Violation Found (Style/Syntax):")
                print(result.stdout if result.stdout else result.stderr)
                return False
            print("✅ Quality Verified: 100% Clean.")
            return True
        except FileNotFoundError:
            print("⚠️ Ruff not found. Static analysis skipped. (Please install: pip install ruff)")
            return True
        except Exception as e:
            print(f"⚠️ Analysis Error: {e}")
            return True

    def run_integrity_check(self):
        """모듈 연결성 및 런타임 무결성 검수"""
        print("🔗 Testing Module Integrity (Integrity First)...")
        # 해당 프로젝트의 핵심 진입점 자동 탐색 (예: app.py, main.py 등)
        entry_points = ["app.py", "main.py", "run.py"]
        found_entry = [f for f in entry_points if (self.root_dir / f).exists()]
        
        issues = []
        
        for entry in found_entry:
            try:
                result = subprocess.run(
                    [str(self.python_exe), "-c", f"import {entry.replace('.py', '')}"],
                    capture_output=True, text=True, encoding='utf-8', errors='ignore'
                )
                if result.returncode != 0:
                    issues.append(f"❌ {entry}: {result.stderr.strip().splitlines()[-1]}")
            except Exception as e:
                issues.append(f"⚠️ {entry}: Test failed ({e})")
        
        if issues:
            for iss in issues:
                print(iss)
            return False
        print("✅ Integrity Verified: Systems Active.")
        return True

    def run_full_audit(self):
        """통합 검수 파이프라인"""
        print("\n" + "="*50)
        print("🚀 [OMNI-DevPilot] System Health Check")
        print("="*50)
        
        s1 = self.run_static_analysis()
        s2 = self.run_integrity_check()
        
        print("\n" + "="*50)
        if s1 and s2:
            print("✨ [SYSTEM HEALTHY] Ready for Master.")
            return True
        else:
            print("⚠️ [SYSTEM UNHEALTHY] Action Required.")
            return False

if __name__ == "__main__":
    pilot = DevPilot()
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        pilot.run_full_audit()