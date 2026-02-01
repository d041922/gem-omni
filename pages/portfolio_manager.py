"""
Portfolio Manager [GEM: OMNI] - Legacy Bridge
Redirects to wealth_screens/dashboard for unified logic.
"""
from pages.wealth_screens.dashboard import render_dashboard

def render_portfolio_page():
    render_dashboard()

if __name__ == "__main__":
    render_portfolio_page()
