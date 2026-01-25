import sys
import os
import traceback
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from skills.valuation_engine import ValuationEngine
    from skills.news_analyzer import get_analyst_ratings, get_company_news
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def verify_stock(ticker, expected_style):
    print(f"\n" + "="*50)
    print(f"🔍 검증 대상: {ticker} (예상 스타일: {expected_style})")
    print("="*50)
    
    try:
        engine = ValuationEngine()
        result = engine.calculate_valuation_metrics(ticker)
        
        if not result:
            print("❌ 결과가 None입니다.")
            return

        if 'error' in result:
            print(f"❌ 분석 실패 (엔진 내부 에러): {result['error']}")
            return

        # 1. 스타일 판별 확인
        style = result.get('style', 'Unknown')
        print(f"✅ 판별된 스타일: {style}")
        print(f"💡 판별 근거: {result.get('style_reason', 'N/A')}")
        
        # 2. 밸류에이션 결과 확인
        assessment = result.get('assessment', 'N/A')
        score = result.get('valuation_score', 0)
        print(f"📊 종합 평가: {assessment} (점수: {score}/10)")
        
        # 3. 스타일별 핵심 지표 확인
        style_analysis = result.get('style_analysis', {})
        key_metrics = style_analysis.get('key_metrics', {})
        print(f"🎯 핵심 지표: {key_metrics}")
        
        # 4. 요약 문구 확인
        print(f"📝 요약: {result.get('summary', 'N/A')}")
        
        # 5. 데이터 수집기(Analyst) 확인
        try:
            ratings = get_analyst_ratings(ticker)
            print(f"💼 애널리스트 의견: {ratings.get('consensus', 'N/A')} (목표가: {ratings.get('target_mean', 'N/A')})")
        except Exception as e:
            print(f"⚠️ 애널리스트 데이터 수집 중 예외 발생: {e}")
        
        # 6. 뉴스 수집 확인
        try:
            news = get_company_news(ticker, limit=1)
            news_status = "✅ 수집 성공" if news else "⚠️ 데이터 없음"
            print(f"📰 뉴스 수집 상태: {news_status}")
        except Exception as e:
            print(f"⚠️ 뉴스 수집 중 예외 발생: {e}")

    except Exception as e:
        print(f"❌ 검증 중 예상치 못한 에러 발생: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    stocks = [
        ("NVDA", "Growth"),
        ("KO", "Value"),
        ("XOM", "Cyclical"),
        ("005930.KS", "Mixed")
    ]
    
    for ticker, style in stocks:
        verify_stock(ticker, style)