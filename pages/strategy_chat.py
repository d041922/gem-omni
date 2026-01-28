"""
Strategy Sync Chat - 마스터의 전략 참모 [GEM: OMNI]
사용자와 대화하며 시스템 도구를 호출하고 투자 정책(IPS)을 동기화함.
"""
import streamlit as st
import os
import json
import google.genai as genai
from google.genai.types import Content, Part

def render_strategy_chat_page():
    try:
        st.markdown("<p class='panel-header'>🧠 전략 회의실 (Strategy Sync)</p>", unsafe_allow_html=True)
        st.caption("실시간 데이터 조회 및 정책(IPS) 수정이 가능합니다.")

        # Lazy import tools
        from agents.tools.ai_strategy_tools import (
            get_ai_portfolio_status,
            get_ai_stock_analysis,
            update_system_policy,
            get_current_policy,
            record_strategic_decision
        )

        tools = [
            get_ai_portfolio_status,
            get_ai_stock_analysis,
            update_system_policy,
            get_current_policy,
            record_strategic_decision
        ]

        # --- 1. Session State ---
        if "strategy_history" not in st.session_state:
            st.session_state.strategy_history = [] # For Gemini SDK (Content objects)
        if "ui_messages" not in st.session_state:
            st.session_state.ui_messages = [] # For UI rendering

        # --- 2. Display Chat UI ---
        for msg in st.session_state.ui_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # --- 3. Chat Input ---
        if prompt := st.chat_input("전략 지시 또는 질문 (예: 계좌 현황 브리핑해)"):
            # UI: User Message
            st.session_state.ui_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # AI Response
            with st.chat_message("assistant"):
                response_container = st.empty()
                
                try:
                    # 1) Show status
                    with st.spinner("데이터 조회 및 전략 수립 중..."):
                        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
                        
                        system_instruction = """
                        당신은 마스터의 자산을 관리하는 최고 전략 책임자(CSO) [GEM: OMNI]입니다.
                        
                        [원칙]
                        1. **즉시 도구 사용**: "포트폴리오", "계좌", "종목" 관련 질문에는 무조건 `get_ai_portfolio_status` 등의 도구를 먼저 실행하십시오.
                        2. **맥락 유지**: 이전 대화의 결정 사항을 기억하십시오.
                        3. **단답형 지양**: 데이터를 근거로 논리적이고 구체적인 조언을 하십시오.
                        """

                        # 2) Create Chat Session with History
                        chat = client.chats.create(
                            model="gemini-2.0-flash",
                            config=genai.types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                tools=tools,
                                temperature=0.3 # 낮을수록 사실 기반
                            ),
                            history=st.session_state.strategy_history
                        )

                        # 3) Send Message
                        response = chat.send_message(prompt)
                        
                        # 4) Parse Response text
                        # Tool use response might be split, usually response.text contains the final answer.
                        if response.text:
                            full_response = response.text
                        else:
                            # Fallback if text is empty (rare in simple turn)
                            full_response = "데이터를 확인했으나 답변을 생성하지 못했습니다. 다시 시도해주세요."

                    # UI: AI Message
                    response_container.markdown(full_response)
                    
                    # Update States
                    st.session_state.ui_messages.append({"role": "assistant", "content": full_response})
                    
                    # Update History for Gemini (preserving turns)
                    # Note: The SDK automatically updates chat.history inside the session object,
                    # but since we recreate 'chat' object each run (stateless web), we must capture history manually.
                    # However, manually constructing 'Content' objects from UI messages is safer for stateless.
                    
                    # For simplicity/speed in this prototype, we rely on the fact that
                    # we passed 'st.session_state.strategy_history' to create().
                    # Now we must Append the NEW turns to it for next time.
                    
                    # User turn
                    st.session_state.strategy_history.append(Content(role="user", parts=[Part(text=prompt)]))
                    # Model turn (including function calls handles internally? No, need to be careful)
                    # To be 100% safe in stateless Streamlit + GenAI SDK 0.1, 
                    # we just assume single-turn optimization or simple history.
                    # BETTER: Just save the text history.
                    
                    st.session_state.strategy_history.append(Content(role="model", parts=[Part(text=full_response)]))

                except Exception as e:
                    error_msg = f"통신 오류: {str(e)}"
                    response_container.error(error_msg)

        # --- Sidebar ---
        with st.sidebar:
            st.divider()
            if st.button("🧹 대화 기억 초기화"):
                st.session_state.strategy_history = []
                st.session_state.ui_messages = []
                st.rerun()
            st.markdown("### 📜 적용 중인 IPS")
            st.caption(get_current_policy())

    except Exception as e:
        st.error(f"시스템 오류: {e}")
