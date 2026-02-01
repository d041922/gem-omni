"""
Toss-Inspired Dark Design System [GEM: OMNI 2.0] - Robust Edition
"""
import streamlit as st
import streamlit.components.v1 as components

def load_custom_css():
    st.markdown("""
        <style>
.stApp { background-color: #0D1117
            color: #E6EDF3
            }
.toss-card { background-color: #161B22
            border-radius: 24px
            padding: 24px
            margin-bottom: 16px
            border: 1px solid #30363D
            }
.toss-title { font-size: 0.85rem
            color: #8B949E
            font-weight: 600
            }
.toss-value { font-size: 2.2rem
            color: #FFFFFF !important
            font-weight: 800
            margin: 10px 0
            }
.toss-desc { font-size: 1rem
            font-weight: 600
            }
.toss-plus { color: #F85149
            }
.toss-minus { color: #58A6FF
            }
        </style>
    """, unsafe_allow_html=True)

def format_krw(val):
    try:
        v = float(val)
        if v >= 1e8:
            return f"{v/1e8:,.2f}억"
        if v >= 1e6:
            return f"{v/1e4:,.0f}만"
        return f"{v:,.0f}"
    except Exception:
        return str(val)

def metric_card(title, value, delta=None, color=None):
    c_class = "toss-neutral"
    if delta:
        try:
            num = float(str(delta).replace('%', '').replace('+', ''))
            if num > 0:
                c_class = "toss-plus"
            elif num < 0:
                c_class = "toss-minus"
        except Exception:
            pass
    
    if color == "red":
        c_class = "toss-plus"
    elif color == "blue":
        c_class = "toss-minus"

    st.markdown(f"""
    <div class="toss-card">
        <div class="toss-title">{title}</div>
        <div class="toss-value">{value}</div>
        <div class="toss-desc {c_class}">{delta if delta else ''}</div>
    </div>
    """, unsafe_allow_html=True)

def render_tv_chart(ticker, height=500):
    try:
        # Simplified TV widget embed
        components.html(f"<div>TV Chart for {ticker}</div>", height=height)
    except Exception as e:
        st.error(f"Chart Error: {e}")

def render_tv_technicals(ticker, height=400):
    try:
        components.html(f"<div>TV Tech for {ticker}</div>", height=height)
    except Exception:
        pass

def render_tv_news(ticker, height=400):
    try:
        components.html(f"<div>TV News for {ticker}</div>", height=height)
    except Exception:
        pass
