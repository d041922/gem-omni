"""
[GEM: OMNI] Deep Integrity Checker
Verifies not just modules, but essential functions within them.
"""
import sys
import os
import importlib

def verify():
    checks = [
        ("core.data_manager", ["DataManager", "get_data_manager"]),
        ("skills.stock_analyzer", ["analyze_stock", "search_stock_candidates"]),
        ("skills.sentiment_analyzer", ["get_news_sentiment", "translate_headlines"]),
        ("pages.style_utils", ["load_custom_css", "metric_card", "indicator_badge"]),
        ("app", [])
    ]
    
    print("--- 🛡️ DEEP INTEGRITY CHECK ---")
    all_pass = True
    for mod_name, functions in checks:
        try:
            mod = importlib.import_module(mod_name)
            print(f"✅ Module {mod_name}: Found")
            for func in functions:
                if hasattr(mod, func):
                    print(f"  └ ✅ {func}: OK")
                else:
                    print(f"  └ ❌ {func}: MISSING")
                    all_pass = False
        except Exception as e:
            print(f"❌ Module {mod_name}: FAILED - {e}")
            all_pass = False
            
    return all_pass

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    if verify():
        print("\n🏆 SYSTEM STABLE: Mission Ready.")
        sys.exit(0)
    else:
        print("\n🚨 CRITICAL FAILURE: System inconsistent.")
        sys.exit(1)