import sys
import os
from pathlib import Path

# 프로젝트 루트를 경로에 추가 (최상단 배치로 E402 예방)
sys.path.append(os.getcwd())

from agents.dev_tools.intelligence_ingester import IntelligenceIngester

def run_proof():
    ing = IntelligenceIngester()
    # 진짜 마스터 리포트를 소화
    data = ing.digest_report('memory/research_repo/mcp_master_report.md')

    print("\n" + "💎" * 20)
    print("🌟 [OMNI-DevPilot v5.0] Intelligence Proof")
    print("💎" * 20)
    print(f"\n1. 스스로 식별한 핵심 수정 대상:\n   {data.get('suggested_files')}")
    print(f"\n2. 리포트에서 포착한 핵심 기술 (Tech Stack):\n   {data.get('key_tech')}")
    print(f"\n3. 분석된 코드 패턴 수:\n   {data.get('patterns_found')} patterns")
    print(f"\n4. 요약된 아키텍처:\n   {data.get('raw_summary')[:300]}...")
    print("\n" + "💎" * 20)

if __name__ == "__main__":
    run_proof()
