import pandas as pd

data = {
    "종목명": ["부동산(서울 아파트)", "비트코인", "삼성전자(키움)", "현금(신한은행)"],
    "티커": ["REAL_ESTATE", "BTC-USD", "005930.KS", "CASH"],
    "수량": [1, 0.5, 50, 1],
    "평단가": [1500000000, 85000000, 72000, 5000000],
    "현재가": [1600000000, 92000000, 74000, 5000000],
    "카테고리": ["부동산", "암호화폐", "주식", "현금"]
}

df = pd.DataFrame(data)
df.to_excel("assets/my_assets_template.xlsx", index=False)
