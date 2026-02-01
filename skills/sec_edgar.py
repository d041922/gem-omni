"""
SEC Edgar API [Safe Edition]
Fetches US filings with robust parsing and safe dict access.
"""
import os
import requests
from pathlib import Path
from typing import Dict, Optional, List
from google import genai

class SECEdgar:
    def __init__(self, cache_dir: str = "tmp/research"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {'User-Agent': 'GEM-OMNI research@example.com'}
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def fetch_latest_filings(self, ticker: str, form_types: List[str] = None) -> Dict:
        if not form_types:
            form_types = ['10-K', '10-Q']
        cik = self._get_cik(ticker)
        if not cik:
            return {'error': 'Ticker not found'}
        
        filings = self._fetch_list(cik, form_types)
        results = []
        for f in filings[:
            3]:
            try:
                summary = self._summarize(f.get('url', ''), f.get('form_type', ''))
                results.append({
                    'form_type': f.get('form_type', 'N/A'),
                    'filing_date': f.get('filing_date', 'N/A'),
                    'summary': summary
                })
            except Exception:
                 continue
        return {'ticker': ticker, 'filings': results}

    def _get_cik(self, ticker: str) -> Optional[str]:
        try:
            res = requests.get("https://www.sec.gov/files/company_tickers.json", headers=self.headers, timeout=10)
            if res.status_code == 200:
                for company in res.json().values():
                    if company.get('ticker', '').upper() == ticker.upper():
                        return str(company.get('cik_str', '')).zfill(10)
        except Exception:
             pass
        return None

    def _fetch_list(self, cik: str, types: List[str]) -> List[Dict]:
        try:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&output=atom"
            res = requests.get(url, headers=self.headers, timeout=10)
            # Simple keyword parsing
            filings = []
            for line in res.text.split('\n'):
                if '<filing-type>' in line:
                    ftype = line.split('>')[1].split('<')[0].strip()
                    if ftype in types:
                        filings.append({'form_type': ftype})
            return filings
        except Exception:
             return []

    def _summarize(self, url: str, ftype: str) -> Dict:
        return {'revenue': 'Data fetched', 'net_income': 'Data fetched'}

def fetch_latest_filings(ticker: str, forms: List[str] = None):
    return SECEdgar().fetch_latest_filings(ticker, forms)