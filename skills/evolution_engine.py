"""
OMNI Evolution Engine (v1.0)
Analyzes trading journals to extract investment principles and update intuitions.
Inspired by Prism Insight's recursive learning logic.
"""
import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

class EvolutionEngine:
    """
    마스터의 투자 일지를 먹고 자라는 자가 진화 엔진.
    """

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def _cluster_journals(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        완료된 일지 데이터를 성공(Profit > 0)과 실패(Profit <= 0) 그룹으로 분류함.
        """
        conn = self.memory_manager._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM trading_journal 
                WHERE tracking_status = 'completed' 
                AND profit_rate IS NOT NULL
            """)
            all_journals = [dict(row) for row in cursor.fetchall()]
            
            success_group = [j for j in all_journals if j['profit_rate'] > 0]
            failure_group = [j for j in all_journals if j['profit_rate'] <= 0]
            
            return success_group, failure_group
        finally:
            conn.close()

    def extract_principles(self) -> str:
        """
        일지 패턴 분석을 통해 새로운 투자 원칙을 도출함.
        (현재는 요약 로직, 향후 LLM 심층 분석 연동)
        """
        success, failure = self._cluster_journals()
        
        if not success and not failure:
            return "분석할 데이터가 부족합니다."

        # 1. 성공 패턴 요약
        success_triggers = [j.get('trigger_type') for j in success if j.get('trigger_type')]

        # TODO: LLM을 호출하여 정교한 문장으로 요약하는 로직 추가
        new_principle = ""
        if success_triggers:
            most_common = max(set(success_triggers), key=success_triggers.count)
            new_principle = f"과거 데이터 분석 결과, '{most_common}' 패턴에서 높은 수익률이 확인되었습니다. 이 시그널을 신뢰하십시오."
            
            # 원칙 테이블에 저장
            source_ids = ",".join([str(j['id']) for j in success])
            self._save_extracted_principle(new_principle, source_ids)
            
        return new_principle if new_principle else "새로운 원칙을 도출하는 중입니다."

    def _save_extracted_principle(self, text: str, source_ids: str) -> int:
        """도출된 원칙을 DB에 저장"""
        return self.memory_manager.add_principle(text, source_ids)

    def update_intuitions_from_history(self) -> bool:
        """
        과거 전체 이력을 바탕으로 패턴별 승률(Trading Intuitions)을 갱신함.
        """
        conn = self.memory_manager._get_connection()
        try:
            cursor = conn.cursor()
            # 패턴별 통계 계산
            cursor.execute("""
                SELECT trigger_type, 
                       COUNT(*) as total, 
                       SUM(CASE WHEN profit_rate > 0 THEN 1 ELSE 0 END) as success,
                       AVG(profit_rate) as avg_p
                FROM trading_journal 
                WHERE tracking_status = 'completed'
                GROUP BY trigger_type
            """)
            stats = cursor.fetchall()
            
            now = datetime.now(timezone.utc).isoformat()
            for row in stats:
                trigger, total, success, avg_p = row
                cursor.execute("""
                    INSERT OR REPLACE INTO trading_intuitions 
                    (pattern_name, occurrence_count, success_count, avg_profit, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """, (trigger, total, success, round(avg_p, 2), now))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Failed to update intuitions: {e}")
            return False
        finally:
            conn.close()
