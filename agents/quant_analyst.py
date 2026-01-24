from typing import Dict, Any, List
import pandas as pd
import numpy as np
from core.models import Asset
from skills.quant_engine import fetch_historical_prices, calculate_correlation, calculate_portfolio_beta

class QuantAnalyst:
    """정량 리스크 분석 서브 에이전트"""
    def __init__(self):
        pass

    def analyze_portfolio_risk(self, assets: List[Asset]) -> Dict[str, Any]:
        """
        포트폴리오의 상관계수, 베타, 리스크 점수를 계산함.
        """
        if not assets:
            return {"correlation": None, "beta": 0.0, "risk_score": 0}

        # 1. 티커 및 비중 추출
        tickers = [a.ticker for a in assets if a.amount > 0 and "." not in str(a.ticker)] # 현금성 자산 제외
        # 한국 주식 처리 (이미 .KS 등이 붙어있다고 가정)
        tickers = list(set([a.ticker for a in assets if a.amount > 0]))
        
        total_eval = sum(a.total_evaluation_value for a in assets)
        weights = {a.ticker: (a.total_evaluation_value / total_eval) for a in assets if total_eval > 0}

        # 2. 데이터 확보 (Skill 호출)
        price_df = fetch_historical_prices(tickers)
        
        if price_df.empty:
            return {"correlation": None, "beta": 1.0, "risk_score": 50}

        # 3. 상관계수 및 베타 계산
        corr_matrix = calculate_correlation(price_df)
        beta = calculate_portfolio_beta(price_df, weights)
        
        # 4. 리스크 점수 산출 (베타와 분산도 기준)
        # Beta 1.0 기준 50점, 1.5 이상이면 80점 이상
        risk_score = min(100, int(beta * 50))
        
        return {
            "correlation": corr_matrix,
            "beta": beta,
            "risk_score": risk_score
        }
