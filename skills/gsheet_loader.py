"""
Google Sheets Loader [GEM: OMNI]
Handles synchronization with Mandalart goals and portfolio data.
"""

import os
import gspread
import pandas as pd
import toml
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import Dict, Tuple, Any


@st.cache_resource
def get_gspread_client():
    """GCP 서비스 계정 인증 및 클라이언트 반환"""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    service_account_info = None

    # 1. Streamlit Secrets 확인
    try:
        service_account_info = st.secrets.get("gcp_service_account")
    except Exception:
        pass

    # 2. 로컬 TOML 파일 확인 (개발 환경용)
    if not service_account_info:
        try:
            p = os.path.join(".streamlit", "secrets.toml")
            if os.path.exists(p):
                service_account_info = toml.load(p).get("gcp_service_account")
        except Exception:
            pass

    if not service_account_info:
        return None

    try:
        creds = Credentials.from_service_account_info(
            service_account_info, scopes=scopes
        )
        return gspread.authorize(creds)
    except Exception:
        return None


def load_mandalart_goals(spreadsheet_name: str) -> Dict[str, Any]:
    """만다라트 시트에서 목표 자산 및 영역별 예산 로드"""
    try:
        client = get_gspread_client()
        if not client:
            return {"success": False, "error": "No client", "total_goal": 1000000000}

        sh = client.open(spreadsheet_name)
        try:
            worksheet = sh.worksheet("Mandalart")
        except Exception:
            worksheet = sh.get_worksheet(0)

        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        target_goal = 1000000000
        if not df.empty and "goal_amount" in df.columns:
            # Finance 카테고리의 목표 합산
            target_goal = df[df["category"] == "Finance"]["goal_amount"].sum()

        return {"success": True, "total_goal": float(target_goal), "categories": data}
    except Exception as e:
        return {"success": False, "error": str(e), "total_goal": 1000000000}


@st.cache_data(ttl=3600)
def load_data_from_gsheet(
    spreadsheet_name: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """[SSOT] 포트폴리오, 관심종목, 현금 데이터 로드 (1시간 메모리 캐싱)"""
    gc = get_gspread_client()
    if not gc:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        ss = gc.open(spreadsheet_name)
        p_df = pd.DataFrame(ss.worksheet("Portfolio").get_all_records())
        w_df = pd.DataFrame(ss.worksheet("Watchlist").get_all_records())
        c_df = pd.DataFrame(ss.worksheet("Cash").get_all_records())

        return p_df, w_df, c_df
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def save_audit_log(spreadsheet_name: str, log_data: Dict):
    """[GES v4.1] 분석 로그 영구 저장 (GSheet Audit Trail)"""
    gc = get_gspread_client()
    if not gc:
        print("[DEBUG] GSheet Client not available for logging.")
        return
    try:
        ss = gc.open(spreadsheet_name)
        # AnalysisLogs 워크시트 우선 사용, 없으면 생성
        try:
            ws = ss.worksheet("AnalysisLogs")
        except Exception:
            try:
                ws = ss.add_worksheet(title="AnalysisLogs", rows="2000", cols="10")
                # 헤더 추가
                ws.append_row(
                    ["Timestamp", "Summary", "Action Plan", "Details/Metadata"]
                )
            except Exception:
                # 권한 이슈 등으로 생성 실패 시 기본 AuditLogs 시도
                ws = ss.worksheet("AuditLogs")

        ws.append_row(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(log_data.get("summary", "")),
                str(log_data.get("actions", "")),
                str(log_data.get("decisions", "")),
            ]
        )
        print(f"[DEBUG] Log appended to {ws.title}")
    except Exception as e:
        print(f"[DEBUG] GSheet Logging failed: {e}")
        pass


def load_recent_logs(spreadsheet_name: str, limit: int = 5):
    """최근 로그 로드"""
    gc = get_gspread_client()
    if not gc:
        return []
    try:
        ss = gc.open(spreadsheet_name)
        ws = ss.worksheet("AuditLogs")
        data = ws.get_all_records()
        return data[-limit:] if data else []
    except Exception:
        return []
