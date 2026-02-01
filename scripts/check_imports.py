print("Checking imports...")
try:
    print("google.genai imported successfully")
except ImportError as e:
    print(f"Failed to import google.genai: {e}")

try:
    print("agents.tools.ai_strategy_tools imported successfully")
except ImportError as e:
    print(f"Failed to import agents.tools.ai_strategy_tools: {e}")
    import traceback
    traceback.print_exc()

print("Done.")
