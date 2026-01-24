import sys
import logging
import re
from typing import Dict, Any, Optional
from core.base import BaseAgent
from core.memory import MemorySystem
from agents.crews.finance_crew import FinanceCrew

# 윈도우 환경 인코딩 호환성 패치 (제거됨: 시스템 기본값 사용)
# if sys.platform == 'win32':
#     sys.stdin.reconfigure(encoding='utf-8')
#     sys.stdout.reconfigure(encoding='utf-8')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("gem_omni.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GEM_OMNI")

class GeminiOmniSystem:
    """
    [GEM: OMNI] 메인 시스템 컨트롤러
    - 에이전트 생명주기 관리
    - 사용자 입력 라우팅
    - 메모리 관리
    """
    def __init__(self):
        self.memory = MemorySystem()  # 메모리 시스템 초기화
        self.agents: Dict[str, BaseAgent] = {}
        self.active = True
        self._initialize_system()

    def _initialize_system(self):
        logger.info("Initializing [GEM: OMNI] System...")
        self._load_core_rules()
        self._register_agents()
        logger.info("System Initialized. Awaiting commands.")

    def _load_core_rules(self):
        # core/RULES.md 또는 설정 파일을 읽어오는 로직 (추후 구현)
        logger.info("Core rules loaded.")

    def _register_agents(self):
        """서브 에이전트 등록 및 초기화"""
        # [SLOT 01] Finance Crew 등록 (CrewAI 기반, Memory 주입)
        self.agents['finance'] = FinanceCrew(memory_system=self.memory, spreadsheet_name="GEM_Finance_Portfolio")
        logger.info("Agent registered: FinanceCrew (CrewAI-powered)")

        # 추후 다른 에이전트들도 여기서 등록 (건강, 관계, 교육 등)

    def route_request(self, user_input: str):
        """사용자 입력을 분석하여 적절한 에이전트에게 라우팅"""
        
        # 사용자 입력 기억
        self.memory.add_dialogue("user", user_input)

        # 티커 패턴 (영문 대문자 2~5글자) 감지
        has_ticker = bool(re.search(r'\b[A-Z]{2,5}\b', user_input))

        # 단순 키워드 기반 라우팅 (임시 로직)
        if "재정" in user_input or "주식" in user_input or "돈" in user_input or "분석" in user_input or has_ticker:
            finance_crew = self.agents.get('finance')
            if finance_crew:
                print("\n[GEM: OMNI] FinanceCrew 실행 중... (4단계 워크플로우)")
                print("  1. 데이터 동기화 (Google Sheets + KIS API)")
                print("  2. 포트폴리오 분석 (메트릭 계산)")
                print("  3. 리스크 평가 (베타, 상관계수)")
                print("  4. AI 전략 생성 (Gemini)")
                print()

                result = finance_crew.generate_full_report()

                if result['success']:
                    response_msg = f"✅ 재정 분석 완료!\n\n{result['strategy_report']}"
                else:
                    response_msg = f"❌ 오류 발생: {result.get('message', 'Unknown error')}"

                print(f"\n[GEM: OMNI] {response_msg}\n")

                # 에이전트 응답 기억
                self.memory.add_dialogue("agent", response_msg)
            else:
                msg = "재정 Crew를 찾을 수 없습니다."
                print(f"\n[GEM: OMNI] {msg}\n")
                self.memory.add_dialogue("agent", msg)
        
        elif user_input.lower() in ['exit', 'quit', '종료']:
            self.shutdown()
        
        else:
            msg = f"명령을 이해했습니다: '{user_input}' (아직 처리할 에이전트가 없습니다.)"
            print(f"\n[GEM: OMNI] {msg}\n")
            self.memory.add_dialogue("agent", msg)

    def start(self):
        print("="*50)
        print(" [GEM: OMNI] Personal Agent System Online")
        print(" Model: Gemini 3 Pro | Architecture: Core-Agents-Skills")
        print("="*50)
        
        while self.active:
            try:
                user_input = input("\n[마스터] >>> ").strip()
                if not user_input:
                    continue
                self.route_request(user_input)
            except (KeyboardInterrupt, EOFError):
                self.shutdown()
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

    def shutdown(self):
        print("\n[GEM: OMNI] Shutting down system...")
        self.memory.save_all_memory() # 종료 전 최종 저장
        self.active = False
        sys.exit(0)

if __name__ == "__main__":
    app = GeminiOmniSystem()
    app.start()
