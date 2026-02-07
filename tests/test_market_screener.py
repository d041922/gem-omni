import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from skills.market_screener import MarketScreener, FactorEngine
from skills.data_orchestrator import DataOrchestrator

@pytest.fixture
def mock_orchestrator():
    """DataOrchestrator 모킹"""
    return MagicMock(spec=DataOrchestrator)

@pytest.fixture
def factor_engine():
    """FactorEngine 인스턴스"""
    return FactorEngine()

@pytest.fixture
def screener(mock_orchestrator):
    """MarketScreener 인스턴스 (모킹된 오케스트레이터 주입)"""
    return MarketScreener(orchestrator=mock_orchestrator)

def test_factor_rsi_calculation(factor_engine):
    """UT-F01: RSI 계산 정확도 확인"""
    # 14일 연속 상승 시나리오 (강한 모멘텀)
    prices = [100 + i for i in range(20)]
    df = pd.DataFrame({"Close": prices})
    rsi = factor_engine.calculate_rsi(df, period=14)
    assert rsi > 70  # 강세 구간 진입 확인

def test_factor_volume_surge(factor_engine):
    """UT-F02: 거래량 급증률 계산 확인"""
    # 평균 100, 현재 300 -> 3배(300%) 급증
    volumes = [100] * 5 + [300]
    df = pd.DataFrame({"Volume": volumes})
    surge_ratio = factor_engine.calculate_volume_surge(df, window=5)
    assert surge_ratio == 3.0

def test_scoring_logic_full_data(screener):
    """UT-S01: 모든 데이터가 완벽할 때 OMNI Score 산출 확인"""
    factors = {
        "rsi": 75.0,        # Technical (Weight 20%)
        "macd_hist": 1.0,   # Technical (Weight 10%)
        "ma_cross": 1.0,    # Technical (Weight 10%)
        "per_rel": 0.8,     # Fundamental (Weight 20%) -> 저평가 상태
        "eps_growth": 0.25, # Fundamental (Weight 10%)
        "vol_surge": 2.5,   # Flow (Weight 20%)
        "rel_strength": 1.2 # Flow (Weight 10%)
    }
    score = screener.calculate_omni_score(factors)
    assert 0 <= score <= 100
    assert isinstance(score, float)

def test_weight_normalization_missing_data(screener):
    """UT-S02: 데이터 결측 시 가중치 재분배(Normalization) 확인"""
    # PER 데이터(per_rel)가 누락된 상황
    factors = {
        "rsi": 70.0,
        "vol_surge": 2.0,
        "per_rel": None,  # 결측치 발생
        "eps_growth": 0.2
    }
    score = screener.calculate_omni_score(factors)
    # 크래시 없이 점수가 나와야 하며, 0~100 사이여야 함
    assert 0 <= score <= 100

def test_integration_with_orchestrator(screener, mock_orchestrator):
    """IT-01: 오케스트레이터 연동 및 데이터 저장 확인"""
    results = [
        {"ticker": "NVDA", "score": 88.5, "signals": ["Momentum", "Vol Surge"]},
        {"ticker": "TSLA", "score": 42.0, "signals": ["Neutral"]}
    ]
    
    screener.save_results(results)
    # orchestrator.update_state가 "intelligence" 섹션에 대해 호출되었는지 확인
    mock_orchestrator.update_state.assert_called_once()
    args, _ = mock_orchestrator.update_state.call_args
    assert args[0] == "intelligence"
    assert "screener_results" in args[1]
