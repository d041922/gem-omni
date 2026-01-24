import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

@st.cache_resource
def get_gspread_client():
    """Gspread 클라이언트 초기화 (Singleton)"""
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        gc = gspread.authorize(creds)
        return gc
    except Exception as e:
        st.error(f"GCP 인증 실패: {e}")
        return None

def load_data_from_gsheet(spreadsheet_name: str):
    """
    구글 시트에서 Portfolio, Watchlist, Cash 데이터를 로드합니다.
    (ref_finance_core.py의 로직 이식)
    """
    gc = get_gspread_client()
    if not gc: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        spreadsheet = gc.open(spreadsheet_name)
        
        # 1. Portfolio
        portfolio_ws = spreadsheet.worksheet("Portfolio")
        portfolio_data = portfolio_ws.get_all_values()
        if portfolio_data:
            portfolio_headers = portfolio_data.pop(0)
            portfolio_df = pd.DataFrame(portfolio_data, columns=portfolio_headers)
        else:
            portfolio_df = pd.DataFrame()

        # 2. Watchlist
        watchlist_ws = spreadsheet.worksheet("Watchlist")
        watchlist_df = pd.DataFrame(watchlist_ws.get_all_records())

        # 3. Cash
        cash_ws = spreadsheet.worksheet("Cash")
        cash_df = pd.DataFrame(cash_ws.get_all_records())

        # 숫자형 변환 (전처리)
        numeric_cols = ['수량', '평균 단가(USD)', '평균 단가(KRW)', '수동 현재가(KRW)']
        for col in numeric_cols:
            if col in portfolio_df.columns:
                portfolio_df[col] = portfolio_df[col].replace('', '0').astype(str).str.replace(',', '')
                portfolio_df[col] = pd.to_numeric(portfolio_df[col], errors='coerce').fillna(0)
        
        if '금액(KRW)' in cash_df.columns:
            cash_df['금액(KRW)'] = cash_df['금액(KRW)'].replace('', '0').astype(str).str.replace(',', '')
            cash_df['금액(KRW)'] = pd.to_numeric(cash_df['금액(KRW)'], errors='coerce').fillna(0)

        return portfolio_df, watchlist_df, cash_df

    except Exception as e:
        st.error(f"Google Sheets 로드 오류: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
