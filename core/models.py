from crewai import LLM
import os

def get_gemini_llm(model_name="gemini/gemini-2.0-flash-exp", temperature=0.3):
    """
    GEM: OMNI 시스템 표준 LLM 생성 함수.
    접두어 'gemini/'를 사용하여 litellm 호환성을 보장함.
    """
    return LLM(
        model=model_name,
        temperature=temperature,
        api_key=os.getenv("GOOGLE_API_KEY")
    )

# 시스템 표준 모델 인스턴스
default_llm = get_gemini_llm()
pro_llm = get_gemini_llm(model_name="gemini/gemini-3-pro-preview", temperature=0.1)
flash_llm = get_gemini_llm(model_name="gemini/gemini-3-flash-preview", temperature=0.2)
