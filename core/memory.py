"""
OMNI Memory System (v5.0) - Grand Integration Edition
Inspired by Prism Insight's Recursive Learning Architecture.
Provides deep journaling, intuition mapping, and principle extraction.
"""
import sqlite3
import json
import logging
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class UserMemoryManager:
    """
    마스터의 경험(Journal)을 학습하여 지혜(Principle)로 승화시키는 영구 기억 장치.
    """

    def __init__(self, db_path: str = "data/omni.db"):
        self.db_path = db_path
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._ensure_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _ensure_tables(self):
        """Prism Insight 기반의 고도화된 스키마 초기화"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 1. 일반 기억 (대화 로그 등)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    ticker TEXT,
                    importance REAL DEFAULT 0.5,
                    created_at TEXT NOT NULL,
                    tags TEXT
                )
            """)
            
            # 2. 투자 일지 (Trading Journal) - Prism Insight 정수 이식
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trading_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    trigger_type TEXT, -- 진입 근거 (e.g., RSI_Oversold)
                    confidence_score INTEGER, -- 확신도 (0-100)
                    situation_analysis TEXT, -- 당시 시장 상황 분석
                    buy_price REAL,
                    sell_price REAL,
                    profit_rate REAL, -- 사후 업데이트 대상
                    tracking_status TEXT DEFAULT 'active', -- active, completed
                    created_at TEXT NOT NULL
                )
            """)
            
            # 3. 투자 직관 및 통계 (Trading Intuitions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trading_intuitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT UNIQUE,
                    occurrence_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    avg_profit REAL DEFAULT 0.0,
                    last_updated TEXT
                )
            """)
            
            # 4. 투자 원칙 (Investment Principles)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_principles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    principle_text TEXT NOT NULL,
                    source_ids TEXT, -- 근거가 된 journal ID들
                    created_at TEXT NOT NULL
                )
            """)
            
            # 5. 사용자 선호도
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()
        finally:
            conn.close()

    # --- Core Memory Methods ---
    def add_memory(self, memory_type: str, content: str, ticker: Optional[str] = None, importance: float = 0.5, tags: List[str] = None) -> int:
        now = datetime.now(timezone.utc).isoformat()
        tags_json = json.dumps(tags) if tags else None
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_memories (memory_type, content, ticker, importance, created_at, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (memory_type, content, ticker, importance, now, tags_json))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    # --- Journal & Principle Methods (New in v5.0) ---
    def add_journal(self, ticker: str, trigger_type: str = None, confidence_score: int = 50, situation_analysis: str = "") -> int:
        """전문 트레이딩 일지 기록"""
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trading_journal (ticker, trigger_type, confidence_score, situation_analysis, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (ticker, trigger_type, confidence_score, situation_analysis, now))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_principle(self, text: str, source_ids: str = "") -> int:
        """학습된 투자 원칙 저장"""
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO investment_principles (principle_text, source_ids, created_at)
                VALUES (?, ?, ?)
            """, (text, source_ids, now))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def recall(self, ticker: Optional[str] = None, keyword: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        query = "SELECT id, memory_type, content, ticker, importance, created_at FROM user_memories WHERE 1=1"
        params = []
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        if keyword:
            query += " AND content LIKE ?"
            params.append(f"%{keyword}%")
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_preferences(self, **kwargs):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            for k, v in kwargs.items():
                cursor.execute("INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)", (k, str(v)))
            conn.commit()
        finally:
            conn.close()

    def get_preferences(self) -> Dict[str, str]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_preferences")
            return {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            conn.close()


class MemorySystem(UserMemoryManager):
    """Backward-compatible alias used by legacy tests/tools."""

    pass
