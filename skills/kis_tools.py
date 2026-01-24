import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class KISConnector:
    """
    한국투자증권 Open API 커넥터
    """
    def __init__(self):
        load_dotenv(override=True) # .env 파일 강제 재로드
        self.app_key = os.getenv("KIS_APP_KEY")
        self.app_secret = os.getenv("KIS_APP_SECRET")
        self.account_no = os.getenv("KIS_ACCOUNT_NO")
        
        # 문자열 비교 로직 강화
        paper_env = str(os.getenv("KIS_PAPER_TRADING", "true")).strip().lower()
        self.is_paper = (paper_env == "true")
        
        # 실전/모의 서버 주소 설정
        if self.is_paper:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
        else:
            self.base_url = "https://openapi.koreainvestment.com:9443"
            
        self.access_token = None

    def get_access_token(self):
        """OAuth2 토큰 발급"""
        path = "/oauth2/tokenP"
        url = f"{self.base_url}{path}"
        headers = {"content-type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        res = requests.post(url, headers=headers, data=json.dumps(data))
        if res.status_code == 200:
            self.access_token = res.json()["access_token"]
            return self.access_token
        else:
            raise Exception(f"Failed to get access token: {res.text}")

    def fetch_balance(self):
        """실시간 잔고 및 보유 종목 리스트 조회 (국내주식 기준)"""
        if not self.access_token:
            self.get_access_token()
            
        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        url = f"{self.base_url}{path}"
        
        # 계좌번호 파싱 (앞 8자리, 뒤 2자리)
        cano = self.account_no[:8]
        acnt_prdt_cd = self.account_no[8:]
        
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "VTTC8434R" if self.is_paper else "TTTC8434R" # 주식잔고조회 TR ID
        }
        
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "AFHR_FLPR_YN": "N",
            "OVR_RSVN_YN": "N",
            "OTSC_DTC_GBN_CD": "00",
            "PRDT_TYPE_CD": "01",
            "UNPR_DVSN_CD": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            # 보유 종목만 정리해서 반환
            holdings = []
            for item in data.get("output1", []):
                if int(item['hldg_qty']) > 0:
                    holdings.append({
                        "ticker": item['pdno'] + (".KS" if item['prdt_name'] != "" else ""), # 단순화된 티커 처리
                        "name": item['prdt_name'],
                        "amount": int(item['hldg_qty']),
                        "avg_price": float(item['pchs_avg_pric']),
                        "current_price": float(item['prpr']),
                        "profit_pct": float(item['evlu_pfit_rt'])
                    })
            
            summary = data.get("output2", [{}])[0]
            return {
                "holdings": holdings,
                "total_eval_amt": float(summary.get("tot_evlu_amt", 0)),
                "total_profit_amt": float(summary.get("evlu_pfit_smtl_amt", 0)),
            }
        else:
            raise Exception(f"Balance inquiry failed: {res.text}")
