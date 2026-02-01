from skills.kis_tools import KISConnector

def test():
    try:
        kis = KISConnector()
        print(f"[*] 접속 모드: {'모의투자' if kis.is_paper else '실전투자'}")
        print("[*] 토큰 발급 및 잔고 조회 시도 중...")
        
        balance = kis.fetch_balance()
        
        print("\n[✅ 동기화 성공!]")
        print(f"- 총 평가 금액: {balance['total_eval_amt']:,.0f}원")
        print(f"- 총 평가 손익: {balance['total_profit_amt']:,.0f}원")
        print("\n[보유 종목 리스트]")
        for h in balance['holdings']:
            print(f"- {h['name']} ({h['ticker']}): {h['amount']}주 / 평단 {h['avg_price']:,.0f}원")
            
    except Exception as e:
        print(f"\n[❌ 동기화 실패]")
        print(f"사유: {str(e)}")

if __name__ == "__main__":
    test()
