import subprocess
import sys
import os

def run_auto_fix(file_path: str):
    """
    ruff를 사용하여 파이썬 파일의 들여쓰기 및 스타일 오류를 자동으로 교정함.
    """
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    
    print(f"--- 🛠️ Auto-fixing {file_path} ---")
    try:
        # 1. 포맷팅 (들여쓰기 등 교정)
        subprocess.run([venv_python, "-m", "ruff", "format", file_path], check=True)
        # 2. 린트 및 자동 수정 (불필요한 임포트 제거 등)
        subprocess.run([venv_python, "-m", "ruff", "check", "--fix", file_path], check=True)
        print(f"✅ {file_path} has been auto-fixed and formatted.")
        return True
    except Exception as e:
        print(f"❌ Auto-fix failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/auto_fix.py <file_path>")
        sys.exit(1)
    
    if run_auto_fix(sys.argv[1]):
        sys.exit(0)
    else:
        sys.exit(1)
