from skills.kis_tools import KISConnector
from skills.excel_loader import load_assets_from_excel

def test_sync():
    print("--- [GEM: OMNI] 통합 자산 동기화 테스트 ---\n")
    
    # 1. KIS API 조회
    print("[1] 증권사 API 연결 중...")
    kis = KISConnector()
    try:
        balance = kis.fetch_balance()
        api_holdings = balance['holdings']
        print(f"   => 성공: 주식 평가액 ₩{balance['total_eval_amt']:,.0f} (종목 {len(api_holdings)}개)")
    except Exception as e:
        print(f"   => 실패: {e}")
        api_holdings = []

    # 2. Excel 조회
    print("\n[2] 엑셀 자산 파일 스캔 중...")
    excel_assets = load_assets_from_excel()
    excel_total = sum([a['current_price'] * a['amount'] for a in excel_assets])
    print(f"   => 발견: 파일 자산 총액 ₩{excel_total:,.0f} (항목 {len(excel_assets)}개)")

    # 3. 통합
    total_assets = api_holdings + excel_assets
    grand_total = (balance['total_eval_amt'] if 'balance' in locals() else 0) + excel_total
    
    print(f"\n[3] 최종 통합 결과")
    print(f"   =========================================")
    print(f"   ★ 총 자산 규모: ₩{grand_total:,.0f}")
    print(f"   =========================================")
    
    print("\n[상세 내역]")
    for item in total_assets:
        source = "KIS" if 'ticker' in item and item not in excel_assets else "Excel"
        val = item['current_price'] * item['amount']
        print(f"   - [{source}] {item['name']}: ₩{val:,.0f}")

if __name__ == "__main__":
    test_sync()
