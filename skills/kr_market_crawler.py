"""
KR Market Crawler - 네이버 금융 기반 국내 주식 데이터 수집기
yfinance에서 누락되는 국내 주식의 핵심 재무 지표(PER, PBR, ROE)를 실제 데이터로 보완함.
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, Optional

def get_kr_stock_info(ticker: str) -> Dict:
    """
    네이버 금융에서 국내 주식 재무 지표 크롤링
    ticker: '005930.KS' 또는 '005930' 형식
    """
    code = ticker.replace('.KS', '').replace('.KQ', '')
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 현재가 및 기본 정보
        # 네이버 금융의 'aside_invest' 영역에서 PER, PBR 등을 추출
        invest_info = soup.find('div', {'class': 'aside_invest'})
        if not invest_info:
            return {}

        metrics = {}
        
        # PER 추출
        per_tag = soup.find('em', id='_per')
        if per_tag:
            metrics['pe_ratio'] = float(per_tag.text.replace(',', ''))
            
        # PBR 추출
        pbr_tag = soup.find('em', id='_pbr')
        if pbr_tag:
            metrics['price_to_book'] = float(pbr_tag.text.replace(',', ''))
            
        # ROE 및 추가 지표 (기업실적분석 테이블)
        # 보통 첫 번째 테이블의 최근 연간 실적 행에서 ROE를 가져옴
        section = soup.find('div', {'class': 'section cop_analysis'})
        if section:
            table = section.find('table', {'class': 'tb_type1'})
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    if th and 'ROE' in th.text:
                        # 최근 연간 실적 (보통 4번째-6번째 td)
                        tds = row.find_all('td')
                        for td in reversed(tds): # 가장 최근 값부터
                            val = td.text.strip().replace(',', '')
                            if val and val != '-':
                                try:
                                    metrics['roe'] = float(val)
                                    break
                                except: continue
        
        return metrics

    except Exception as e:
        print(f"KR Crawler Error for {ticker}: {e}")
        return {}

def get_kr_earnings_schedule() -> list:
    """
    네이버 금융 '실적 속보' 페이지에서 최근/예정 실적 발표 리스트 크롤링
    URL: https://finance.naver.com/research/earnings_list.naver
    """
    url = "https://finance.naver.com/research/earnings_list.naver"
    results = []
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 메인 테이블 찾기
        box = soup.find('div', {'class': 'box_type_m'})
        if not box:
            return []
            
        table = box.find('table', {'class': 'type_1'})
        if not table:
            return []
            
        rows = table.find_all('tr')
        
        # 헤더 건너뛰고 데이터 파싱 (보통 2번째 행부터 데이터)
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5: # 구분선이나 빈 행 제외
                continue
                
            # 데이터 추출
            # 0: 종목명, 1: 실적발표일(링크), 2: 분기, ...
            try:
                name = cols[0].text.strip()
                date = cols[1].text.strip()
                quarter = cols[2].text.strip()
                
                # 링크에서 코드 추출 (optional)
                link = cols[0].find('a')
                code = ""
                if link and 'code=' in link['href']:
                    code = link['href'].split('code=')[1]
                
                results.append({
                    "name": name,
                    "code": code,
                    "date": date,
                    "quarter": quarter,
                    "revenue": cols[3].text.strip(), # 매출액
                    "profit": cols[4].text.strip(), # 영업이익
                    "net_income": cols[5].text.strip() if len(cols) > 5 else "-"
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Earnings Crawler Error: {e}")
        
    return results

if __name__ == "__main__":
    # Test
    print("Samsung Electronics (005930):", get_kr_stock_info("005930.KS"))
    print("Earnings Schedule Sample:", get_kr_earnings_schedule()[:3])
