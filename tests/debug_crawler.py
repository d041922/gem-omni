from skills.kr_market_crawler import get_kr_stock_info
import requests

def debug():
    ticker = "423180.KS"
    print(f"--- Debugging {ticker} ---")
    
    # 1. 크롤러 호출 결과
    info = get_kr_stock_info(ticker)
    print(f"Crawler Result: {info}")
    
    # 2. 크롤러 내부의 원천 데이터 확인
    code = ticker.replace('.KS', '').replace('.KQ', '')
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print(f"HTTP Status: {res.status_code}")
    
    if "no_today" in res.text:
        print("Found 'no_today' in HTML")
    else:
        print("COULD NOT find 'no_today' in HTML")

if __name__ == "__main__":
    debug()
