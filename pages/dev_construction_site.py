import streamlit as st
import json
from pathlib import Path

def render_construction_site():
    st.markdown("# 🚧 Dev-Construction Site")
    st.warning("이 페이지는 시스템 고도화를 위한 '임시 공사 현장'입니다.")
    
    # --- 1. Load Real State Data ---
    state_path = Path("memory/task_states/current_mission.json")
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {"phase": "OFFLINE", "status": "No active mission.", "progress": 0}

    # --- 2. Live Status Board ---
    st.subheader(f"📍 Current Mission: {state.get('mission', 'None')}")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("Phase", state["phase"])
    with c2:
        st.metric("Progress", f"{state['progress']}%")
    with c3:
        st.caption(f"Last Update: {state.get('last_updated', 'N/A')}")

    st.progress(state["progress"] / 100)
    st.info(f"**Status:** {state['status']}")

    st.divider()

    # --- 3. Active Tracks & History ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📝 Project Blueprints (Conductor)")
        tracks_path = Path("conductor/tracks.md")
        if tracks_path.exists():
            with open(tracks_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.caption("활성화된 설계 트랙이 없습니다.")

    with col_right:
        st.subheader("🔌 Extensions")
        for ext in ["Deep Research", "Stitch", "Exa", "Security", "Review"]:
            st.write(f"✅ {ext}")

if __name__ == "__main__":
    render_construction_site()