import pandas as pd

from skills.quant_engine import FactorEngine


def _make_ohlcv(close_values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Close": close_values,
            "High": [c + 1.0 for c in close_values],
            "Low": [c - 1.0 for c in close_values],
            "Volume": [1_000_000 + i * 2_000 for i in range(len(close_values))],
        }
    )


def test_generate_strategic_analysis_detects_bearish_regime() -> None:
    close = [250 - i for i in range(80)]
    df = _make_ohlcv(close)
    report = FactorEngine.generate_strategic_analysis("MSFT", float(close[-1]), df, {})

    assert "BEARISH" in report["trend"] or "Regime=DOWN" in report["trend"]
    assert "완만한 우상향 흐름 유지" not in report["trend"]


def test_generate_strategic_analysis_detects_bullish_regime() -> None:
    close = [100 + i * 0.8 for i in range(80)]
    df = _make_ohlcv(close)
    report = FactorEngine.generate_strategic_analysis("NVDA", float(close[-1]), df, {})

    assert "BULLISH" in report["trend"] or "Regime=UP" in report["trend"]
    assert "신뢰도:" in report["action"]


def test_generate_strategic_analysis_sideways_prefers_watch_like_action() -> None:
    close = [100 + ((-1) ** i) * 0.5 for i in range(80)]
    df = _make_ohlcv(close)
    report = FactorEngine.generate_strategic_analysis("AAPL", float(close[-1]), df, {})

    assert "Regime=SIDE" in report["trend"] or "NEUTRAL" in report["trend"]
    assert any(level in report["action"] for level in ["WATCH", "REDUCE", "AVOID", "ENTER"])
