"""
Home Page [GEM: OMNI] - Legacy Bridge
Redirects or provides a summary consistent with app.py.
"""
import streamlit as st

def render_home_page():
    st.markdown("### Welcome to GEM: OMNI")
    st.info("Use the Mandalart Grid on the main page to navigate.")

if __name__ == "__main__":
    render_home_page()
