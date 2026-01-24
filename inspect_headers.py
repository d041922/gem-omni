import pandas as pd
import os

files = ["assets/GEM_Finance_Portfolio.xlsx", "assets/MyAsset_AllAcc_Excel.xls"]

print("--- Excel Header Inspection ---")
for f in files:
    if not os.path.exists(f):
        print(f"[X] Not Found: {f}")
        continue
        
    try:
        if f.endswith('.xls'):
            df = pd.read_excel(f, engine='xlrd', nrows=1)
        else:
            df = pd.read_excel(f, nrows=1)
        print(f"\n[File: {os.path.basename(f)}]")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"[Error] {f}: {e}")
