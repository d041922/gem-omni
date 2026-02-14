"""
Data Cache Tool [GEM: OMNI]
Handles local caching of market data and agent results.
"""
import os
import json
from typing import Any, Optional
import pandas as pd

class DataCache:
    def __init__(self, cache_file: str = "tmp/cache/data_cache.json"):
        self.path = cache_file
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get(key)
        except Exception:
            pass
        return None

    def set(self, key: str, value: Any):
        try:
            data = {}
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except Exception:
                        data = {}
            
            data[key] = value
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception:
            pass


def _cache_dir() -> str:
    path = os.path.join("tmp", "cache")
    os.makedirs(path, exist_ok=True)
    return path


def save_portfolio_data(df: pd.DataFrame, filename: str = "portfolio_raw.json", metadata: Optional[dict] = None) -> dict:
    """Persist dataframe to cache and return compact summary."""
    cache_dir = _cache_dir()
    file_path = os.path.join(cache_dir, filename)
    records = df.to_dict(orient="records") if df is not None else []
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, default=str)

    summary = {
        "total_positions": len(records),
        "columns": list(df.columns) if df is not None else [],
    }
    if metadata:
        summary.update({"metadata": metadata})

    return {"file_path": file_path, "summary": summary}


def load_portfolio_data(file_path: str) -> pd.DataFrame:
    """Load cached dataframe from a json file path."""
    if not file_path or not os.path.exists(file_path):
        return pd.DataFrame()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)


def get_cache_summary() -> dict:
    """Return cache file inventory."""
    cache_dir = _cache_dir()
    files = []
    for name in sorted(os.listdir(cache_dir)):
        fp = os.path.join(cache_dir, name)
        if os.path.isfile(fp):
            files.append(
                {
                    "name": name,
                    "size_kb": round(os.path.getsize(fp) / 1024, 2),
                    "path": fp,
                }
            )
    return {"cache_dir": cache_dir, "total_files": len(files), "files": files}
