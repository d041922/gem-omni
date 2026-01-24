import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("GEM_OMNI")

class MemorySystem:
    """
    [GEM: OMNI] Integrated Memory System
    1. Short-Term: 대화 맥락 (Context)
    2. Long-Term: 사용자 프로필 (Profile)
    3. Episodic: 과거 분석 기록 (History Logs)
    """
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        self.history_file = os.path.join(memory_dir, "conversation_history.json")
        self.profile_file = os.path.join(memory_dir, "user_profile.json")
        self.analysis_log_file = os.path.join(memory_dir, "analysis_log.json")
        
        self.conversation_history: List[Dict[str, Any]] = []
        self.user_profile: Dict[str, Any] = {}
        self.analysis_logs: List[Dict[str, Any]] = []
        
        self._ensure_memory_dir()
        self.load_all_memory()

    def _ensure_memory_dir(self):
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)

    def load_all_memory(self):
        """모든 종류의 기억을 파일에서 로드"""
        self.conversation_history = self._load_json(self.history_file, default=[])
        self.user_profile = self._load_json(self.profile_file, default={"risk_tolerance": "neutral", "portfolio": []})
        self.analysis_logs = self._load_json(self.analysis_log_file, default=[])

    def _load_json(self, filepath: str, default: Any) -> Any:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load {filepath}: {e}")
        return default

    def save_all_memory(self):
        """모든 기억을 파일에 저장"""
        self._save_json(self.history_file, self.conversation_history)
        self._save_json(self.profile_file, self.user_profile)
        self._save_json(self.analysis_log_file, self.analysis_logs)

    def _save_json(self, filepath: str, data: Any):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save {filepath}: {e}")

    # --- Interface for Short-Term Memory ---
    def add_dialogue(self, role: str, content: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        }
        self.conversation_history.append(entry)
        self._save_json(self.history_file, self.conversation_history) # Auto-save

    # --- Interface for Episodic Memory (Comparison) ---
    def record_analysis(self, ticker: str, price: float, metric_data: Dict):
        """특정 종목 분석 결과를 기록 (추후 비교용)"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker.upper(),
            "price": price,
            "data": metric_data
        }
        self.analysis_logs.append(entry)
        self._save_json(self.analysis_log_file, self.analysis_logs)

    def get_last_analysis(self, ticker: str) -> Optional[Dict]:
        """해당 종목의 가장 최근(직전) 분석 기록 조회"""
        ticker = ticker.upper()
        # 역순으로 탐색하여 가장 최근 기록 찾기
        for entry in reversed(self.analysis_logs):
            if entry['ticker'] == ticker:
                return entry
        return None
