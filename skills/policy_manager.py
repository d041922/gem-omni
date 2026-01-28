"""
Policy Manager - 투자 정책서(IPS) 관리 모듈
사용자의 투자 철학, 제약 조건, 목표 비중 등을 JSON 형태로 관리하고
AI 에이전트에게 컨텍스트를 제공함.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class PolicyManager:
    def __init__(self, policy_file: str = "memory/investment_policy.json"):
        # 프로젝트 루트 기준 경로 설정
        self.root_dir = Path(os.getcwd())
        self.policy_path = self.root_dir / policy_file
        self.default_policy = {
            "meta": {
                "version": "1.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "owner": "Master"
            },
            "philosophy": {
                "core_satellite_ratio": "60:40",
                "risk_tolerance": "Moderate Growth (중위험 중수익)",
                "investment_horizon": "Long-term (3년 이상)",
                "principles": [
                    "하락장에서는 분할 매수로 대응",
                    "모멘텀보다는 펀더멘털과 밸류에이션 중시",
                    "단일 종목 최대 손실 10% 제한"
                ]
            },
            "constraints": {
                "min_cash_buffer_krw": 5000000,
                "max_single_stock_weight": 0.20,
                "max_sector_weight": 0.40,
                "excluded_sectors": []
            },
            "targets": {
                "sectors": {
                    "Technology": 0.35,
                    "Healthcare": 0.15,
                    "Finance": 0.10
                },
                "asset_class": {
                    "Equity": 0.70,
                    "Cash": 0.20,
                    "Crypto": 0.10
                }
            },
            "recent_decisions": []  # 의사결정 로그 (최근 5건)
        }
        
        # 파일이 없으면 초기화
        if not self.policy_path.exists():
            self._save_policy(self.default_policy)

    def load_policy(self) -> Dict[str, Any]:
        """정책 파일 로드"""
        try:
            with open(self.policy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"정책 파일 로드 실패: {e}")
            return self.default_policy

    def _save_policy(self, policy_data: Dict[str, Any]):
        """정책 파일 저장 (내부용)"""
        try:
            # 디렉토리 확인
            self.policy_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 메타데이터 업데이트
            if 'meta' not in policy_data: policy_data['meta'] = {}
            policy_data['meta']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.policy_path, 'w', encoding='utf-8') as f:
                json.dump(policy_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"정책 파일 저장 실패: {e}")

    def update_policy(self, section: str, key: str, value: Any) -> bool:
        """
        특정 정책 항목 업데이트
        예: update_policy('constraints', 'min_cash_buffer_krw', 10000000)
        """
        policy = self.load_policy()
        
        if section not in policy:
            policy[section] = {}
            
        policy[section][key] = value
        self._save_policy(policy)
        return True

    def add_decision_log(self, action: str, reason: str, related_assets: list = None):
        """
        의사결정 로그 추가 (컨텍스트 유지를 위해)
        """
        policy = self.load_policy()
        if 'recent_decisions' not in policy:
            policy['recent_decisions'] = []
            
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "reason": reason,
            "assets": related_assets or []
        }
        
        # 최신 순으로 추가하고 10개만 유지
        policy['recent_decisions'].insert(0, log_entry)
        policy['recent_decisions'] = policy['recent_decisions'][:10]
        
        self._save_policy(policy)

    def get_strategy_context(self) -> str:
        """
        AI 프롬프트 주입용 컨텍스트 문자열 생성 (토큰 최적화)
        """
        p = self.load_policy()
        
        # 리스트 문자열 변환
        principles = "\n".join([f"- {item}" for item in p['philosophy'].get('principles', [])])
        
        # 제약조건 요약
        const = p.get('constraints', {})
        constraints_str = f"""
- 최소 현금 보유: ₩{const.get('min_cash_buffer_krw', 0):,}
- 단일 종목 최대 비중: {const.get('max_single_stock_weight', 0)*100:.0f}%
- 섹터 최대 비중: {const.get('max_sector_weight', 0)*100:.0f}%
"""

        # 의사결정 로그 (최근 3건만)
        logs = p.get('recent_decisions', [])[:3]
        logs_str = ""
        if logs:
            logs_str = "\n### 📜 최근 전략적 의사결정 (Context)\n"
            for log in logs:
                logs_str += f"- [{log['timestamp']}] {log['action']}: {log['reason']}\n"

        context = f"""
## 🧠 투자 정책서 (IPS) - {p['meta']['last_updated']} 기준

### 1. 투자 철학 ({p['philosophy'].get('risk_tolerance')})
- Core/Satellite 비율: {p['philosophy'].get('core_satellite_ratio')}
{principles}

### 2. 리스크 관리 원칙 (Hard Rules)
{constraints_str}

### 3. 목표 포트폴리오
- 섹터 비중: {json.dumps(p['targets'].get('sectors', {}), ensure_ascii=False)}
- 자산군 비중: {json.dumps(p['targets'].get('asset_class', {}), ensure_ascii=False)}
{logs_str}
"""
        return context

# 싱글톤 인스턴스처럼 사용하기 위한 헬퍼 함수
def get_policy_context():
    return PolicyManager().get_strategy_context()

def add_strategy_log(action, reason, assets=None):
    PolicyManager().add_decision_log(action, reason, assets)
