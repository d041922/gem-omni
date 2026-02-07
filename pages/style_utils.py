"""
GEM: OMNI Design System (v4.0)
Glassmorphism & Bento Grid Utilities
"""
import streamlit as st

def load_custom_css():
    st.markdown("""
    <style>
        /* Base Theme */
        .stApp {
            background-color: #0E1117;
        }
        
        /* Glassmorphism Card */
        .glass-card {
            background: rgba(30, 37, 48, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            margin-bottom: 20px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            border-color: rgba(49, 130, 246, 0.5);
        }

        /* Typography */
        .card-title {
            color: #8B949E;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .card-value {
            color: #FFFFFF;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .card-delta-pos {
            color: #FF4B4B;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .card-delta-neg {
            color: #1C7ED6;
            font-size: 0.9rem;
            font-weight: 600;
        }

        /* Bento Grid Layout Helpers */
        .bento-row {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .bento-col {
            flex: 1;
            min-width: 300px;
        }
        
        /* Momentum Badge */
        .momentum-badge {
            background: rgba(49, 130, 246, 0.15);
            color: #3182F6;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
            margin-right: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

def metric_card(title: str, value: str, delta: str = None, color: str = None):
    """
    Bento Grid용 Metric Card 컴포넌트
    """
    delta_html = ""
    if delta:
        delta_class = "card-delta-pos" if "red" in str(color) or "+" in delta else "card-delta-neg"
        # OMNI에서는 Red가 Positive (수익), Blue가 Negative (손실) 또는 Neutral
        if color == "blue" and "-" in delta: delta_class = "card-delta-neg"
        delta_html = f"<div class='{delta_class}'>{delta}</div>"
        
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def bento_box(content_func):

    """

    컨텐츠를 감싸는 Glass Container 데코레이터 패턴 (활용 예시)

    """

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    content_func()

    st.markdown('</div>', unsafe_allow_html=True)



def localize_signal(signal: str) -> str:

    """영문 퀀트 시그널을 한글 및 배지로 변환"""

    mapping = {

        "Oversold": "🔵 과매도(저점)",

        "Overbought": "🔴 과매수(과열)",

        "Volume Surge": "🔥 수급폭발",

        "Golden Cross Trend": "📈 상승추세",

        "Neutral": "⚪ 중립"

    }

    return mapping.get(signal, signal)
