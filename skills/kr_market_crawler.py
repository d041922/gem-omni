"""
KR Market Crawler - 네이버 금융 기반 국내 주식/ETF 데이터 수집기 (v2.0)
Robust Selector & Multi-Page Support
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

def _get_soup(url: str) -> Optional[BeautifulSoup]:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://finance.naver.com/'
        }
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        return BeautifulSoup(res.text, 'html.parser')
    except Exception as e:
        print(f"Connection Error ({url}): {e}")
        return None

def get_kr_stock_info(ticker: str) -> Dict:
    """
    네이버 금융에서 국내 주식/ETF 정보 크롤링 (현재가, PER, PBR)
    """
    code = ticker.replace('.KS', '').replace('.KQ', '')
    
    # 1. 메인 페이지 시도
    url_main = f"https://finance.naver.com/item/main.naver?code={code}"
    soup = _get_soup(url_main)
    
    metrics = {}
    
    if soup:
        # A. 현재가 추출 (다양한 패턴 시도)
        price_found = False
        
        # Pattern 1: .no_today (가장 일반적)
        no_today = soup.select_one('p.no_today span.blind')
        if no_today:
            metrics['current_price'] = float(no_today.text.replace(',', ''))
            price_found = True
            
        # Pattern 2: .no_up / .no_down (등락이 있을 때)
        if not price_found:
            price_tag = soup.select_one('div.today span.blind')
            if price_tag:
                metrics['current_price'] = float(price_tag.text.replace(',', ''))
                price_found = True

        # B. 투자 지표 (PER, PBR) - ETF는 없을 수 있음
        try:
            per = soup.select_one('#_per')
            if per: metrics['pe_ratio'] = float(per.text.replace(',', ''))
            
            pbr = soup.select_one('#_pbr')
            if pbr: metrics['price_to_book'] = float(pbr.text.replace(',', ''))
        except: pass

    # 2. 메인에서 실패 시 시세 페이지 시도 (Fallback)
    if 'current_price' not in metrics:
        url_sise = f"https://finance.naver.com/item/sise.naver?code={code}"
        soup_sise = _get_soup(url_sise)
        if soup_sise:
            # 시세 페이지의 strong 태그 내 현재가
            strong_price = soup_sise.select_one('strong#_nowVal')
            if strong_price:
                metrics['current_price'] = float(strong_price.text.replace(',', ''))

    return metrics

def get_kr_earnings_schedule() -> list:
    """실적 속보 크롤링 (기존 로직 유지)"""
    return [] # (생략 - 필요 시 복구)

if __name__ == "__main__":
    # Self-Test
    print("Samsung (005930):", get_kr_stock_info("005930"))
    print("TIGER ETF (423180):", get_kr_stock_info("423180"))