import google.generativeai as genai
import os
import streamlit as st

# secrets.toml 또는 환경 변수에서 키 로드
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    print("--- Available Gemini Models ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
            print(f"Display Name: {m.display_name}")
            print(f"Description: {m.description}")
            print("-" * 30)
except Exception as e:
    print(f"Error listing models: {e}")
