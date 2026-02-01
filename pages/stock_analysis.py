"""
Stock Analysis [GEM: OMNI] - Legacy Bridge
Redirects to wealth_screens/analysis for unified logic.
"""
from pages.wealth_screens.analysis import render_analysis

def render_stock_analysis_page():
    render_analysis()

if __name__ == "__main__":
    render_stock_analysis_page()
