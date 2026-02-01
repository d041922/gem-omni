"""
[GEM: OMNI] Auto-Health Checker
An agent-facing tool to verify system integrity before and after tasks.
"""
import os
import importlib

def check_environment():
    print("--- 🔍 Checking Environment ---")
    keys = ["GOOGLE_API_KEY", "TAVILY_API_KEY"]
    for key in keys:
        if os.getenv(key):
            print(f"✅ {key}: Set")
        else:
            print(f"❌ {key}: MISSING")

def check_imports():
    print("\n--- 🔍 Checking Essential Imports ---")
    modules = [
        "streamlit", "yfinance", "pandas", "crewai", "google.genai",
        "core.data_manager", "pages.style_utils", "skills.stock_analyzer"
    ]
    for mod in modules:
        try:
            importlib.import_module(mod)
            print(f"✅ {mod}: Import Successful")
        except ImportError as e:
            print(f"❌ {mod}: FAILED - {e}")

def check_files():
    print("\n--- 🔍 Checking Critical Files ---")
    files = ["GEM_SYSTEM_BLUEPRINT.md", "USER_PROFILE.md", "core/AGENT_SOP.md"]
    for f in files:
        if os.path.exists(f):
            print(f"✅ {f}: Exists")
        else:
            print(f"❌ {f}: MISSING")

if __name__ == "__main__":
    check_environment()
    check_imports()
    check_files()
    print("\n--- Health Check Completed ---")

