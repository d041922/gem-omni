import pandas as pd
from core.strategy_engine import StrategyEngine

def test_strategy_engine():
    print("1. Mock Data Setup...")
    # 모의 포트폴리오 데이터 생성
    data = {
        '종목명': ['Samsung Elec', 'SK Hynix', 'Naver', 'Tesla'],
        '카테고리': ['Technology', 'Technology', 'Technology', 'Automotive'],
        '평가금액(KRW)': [50000000, 30000000, 10000000, 20000000]
    }
    df = pd.DataFrame(data)
    
    print("2. Initialize Engine...")
    engine = StrategyEngine()
    
    print("\n3. Health Check Analysis...")
    health = engine.analyze_portfolio_health(df)
    print(f"Violations: {health['violations']}")
    print(f"Sector Gaps: {health['sector_gaps']}")
    
    print("\n4. AI Advice Generation (Simulation)...")
    advice = engine.generate_strategic_advice(market_summary="미국 기술주 조정 국면 진입, 금리 인하 기대감 후퇴")
    print("\n[AI ADVICE]\n")
    print(advice)

if __name__ == "__main__":
    test_strategy_engine()

