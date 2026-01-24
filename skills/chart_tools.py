import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
import pandas as pd
from datetime import datetime

def generate_stock_chart(ticker: str, period: str = "6mo", save_dir: str = "charts") -> str:
    """
    특정 주식의 차트(캔들스틱/라인 + 이평선)를 생성하고 이미지 경로를 반환합니다.
    """
    try:
        # 1. 데이터 가져오기
        ticker = ticker.upper()
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return None

        # 2. 차트 설정
        plt.style.use('bmh') # 깔끔한 스타일
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 종가 라인 그리기
        ax.plot(hist.index, hist['Close'], label='Close Price', color='#1f77b4', linewidth=2)
        
        # 이동평균선 추가
        ma20 = hist['Close'].rolling(window=20).mean()
        ma60 = hist['Close'].rolling(window=60).mean()
        
        ax.plot(hist.index, ma20, label='MA 20', color='#ff7f0e', linestyle='--', alpha=0.8)
        ax.plot(hist.index, ma60, label='MA 60', color='#2ca02c', linestyle='--', alpha=0.8)

        # 3. 레이아웃 꾸미기
        ax.set_title(f"{ticker} Stock Price ({period})", fontsize=16)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (USD)")
        ax.legend(loc='best')
        ax.grid(True, which='both', linestyle='--', alpha=0.5)
        
        # 날짜 포맷
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        fig.autofmt_xdate()

        # 4. 저장
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{ticker}_{timestamp}.png"
        filepath = os.path.join(save_dir, filename)
        
        plt.savefig(filepath, dpi=100)
        plt.close(fig) # 메모리 해제
        
        return filepath

    except Exception as e:
        print(f"Chart generation failed: {e}")
        return None
