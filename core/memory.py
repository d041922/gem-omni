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
    """
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        self.history_file = os.path.join(memory_dir, "conversation_history.json")
        self.profile_file = os.path.join(memory_dir, "user_profile.json")

        self.conversation_history: List[Dict[str, Any]] = []
        self.user_profile: Dict[str, Any] = {}

        self._ensure_memory_dir()
        self.load_all_memory()

    def _ensure_memory_dir(self):
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)

    def load_all_memory(self):
        """모든 종류의 기억을 파일에서 로드"""
        self.conversation_history = self._load_json(self.history_file, default=[])
        default_profile = {
            "risk_tolerance": "중간",  # 보수적/중간/공격적
            "investment_goal": "장기 자산 증식",
            "investment_horizon": "10년",  # 단기(<3년)/중기(3-10년)/장기(>10년)
            "preferred_strategy": "가치 투자",  # 가치/성장/배당/퀀트/혼합
            "max_single_position": 15,  # %
            "max_sector_concentration": 30,  # %
            "rebalancing_threshold": 5,  # %
            "portfolio": []
        }
        self.user_profile = self._load_json(self.profile_file, default=default_profile)

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
