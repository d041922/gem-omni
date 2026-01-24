import os

# .env 파일을 직접 한 줄씩 읽어서 파싱
env_data = {}
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                env_data[key.strip()] = val.strip()

print("--- ENV FILE DIRECT CHECK ---")
print(f"KIS_PAPER_TRADING: [{env_data.get('KIS_PAPER_TRADING')}]")
print(f"APP_KEY START: {env_data.get('KIS_APP_KEY', 'None')[:4]}...")

paper_mode = str(env_data.get('KIS_PAPER_TRADING', 'true')).lower() == 'true'
print(f"FINAL RESOLVED MODE: {'PAPER' if paper_mode else 'REAL'}")
