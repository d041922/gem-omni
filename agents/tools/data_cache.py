"""
Data Cache Tool [GEM: OMNI]
Handles local caching of market data and agent results.
"""
import os
import json
from typing import Any, Optional

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