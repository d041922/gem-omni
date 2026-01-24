from typing import Dict, Any

class BaseAgent:
    """
    모든 서브 에이전트의 부모 클래스.
    공통된 인터페이스와 로깅, 에러 처리 기능을 제공합니다.
    """
    def __init__(self, name: str, memory: Any = None):
        self.name = name
        self.memory = memory

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        요청을 처리하고 표준 응답 포맷을 반환합니다.
        자식 클래스에서 구체적인 로직을 오버라이딩해야 합니다.
        """
        raise NotImplementedError(f"[{self.name}] process method not implemented.")
