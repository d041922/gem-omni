"""
Key Loader Utility [Dev Tool] v1.0
Unified strategy to load API keys from .env, secrets.toml, or environment.
"""
import os
import toml
from pathlib import Path
from dotenv import load_dotenv

def load_google_api_key() -> str:
    """
    Attempts to find GOOGLE_API_KEY in this order:
    1. System Environment Variable
    2. .env file in Project Root
    3. .streamlit/secrets.toml
    """
    # 1. System Environment (Highest Priority)
    env_key = os.getenv("GOOGLE_API_KEY")
    if env_key:
        return env_key

    # Root Directory Resolution
    current_file = Path(__file__).resolve()
    # agents/dev_tools/key_loader.py -> agents -> root
    root_dir = current_file.parents[2]

    # 2. .env File
    env_path = root_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        env_key = os.getenv("GOOGLE_API_KEY")
        if env_key:
            return env_key

    # 3. Streamlit Secrets
    secrets_path = root_dir / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        try:
            secrets = toml.load(str(secrets_path))
            # Try various common key names
            keys_to_check = ["GOOGLE_API_KEY", "GEMINI_API_KEY", "google_api_key"]
            for k in keys_to_check:
                if k in secrets:
                    return secrets[k]
        except Exception as e:
            print(f"⚠️ Failed to read secrets.toml: {e}")

    return None

if __name__ == "__main__":
    key = load_google_api_key()
    status = "✅ Found" if key else "❌ Missing"
    print(f"Key Status: {status}")
    if key:
        print(f"Key Preview: {key[:5]}...{key[-5:]}")
