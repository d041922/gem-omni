from core.application.query_service import QueryService


class _FakeOrchestrator:
    def get_full_ticker_data(self, ticker: str):
        closes = [100 + i for i in range(60)]
        return {
            "ticker": ticker,
            "name": "NVIDIA Corp",
            "last_price": closes[-1],
            "history": {
                "Close": closes,
                "High": [c + 1 for c in closes],
                "Low": [c - 1 for c in closes],
                "Volume": [1_000_000 + i * 1000 for i in range(60)],
            },
            "extra_stats": {
                "profile": {
                    "sector": "Technology",
                    "industry": "Semiconductors",
                    "website": "https://www.nvidia.com",
                },
                "financials": {
                    "total_rev": 10_000_000_000,
                    "gross_margin": 0.55,
                    "roe": 0.34,
                    "roa": 0.18,
                    "fcf": 2_000_000_000,
                },
            },
        }


def test_get_stock_analysis_payload_is_deterministic_and_has_core_fields() -> None:
    qs = QueryService(orchestrator=_FakeOrchestrator())

    payload_1 = qs.get_stock_analysis_payload("NVDA", "NASDAQ", "2026-02-15")
    payload_2 = qs.get_stock_analysis_payload("NVDA", "NASDAQ", "2026-02-15")

    assert payload_1 == payload_2
    assert "basics" in payload_1
    assert "price_snapshot" in payload_1
    assert "technical" in payload_1
    assert "fundamentals" in payload_1
    assert "ai_insights" in payload_1
    assert "warnings" in payload_1
    assert "as_of" in payload_1
    assert "data_health" in payload_1
    assert "evidence_fields" in payload_1
    assert "score_breakdown" in payload_1

    technical = payload_1["technical"]
    assert "ma20" in technical
    assert "rsi14" in technical
    assert "volatility_20d" in technical

    fundamentals = payload_1["fundamentals"]
    assert len(fundamentals) >= 3
    assert payload_1["data_health"]["status"] in {"healthy", "partial", "weak"}
    assert "technical" in payload_1["evidence_fields"]
    assert "overall" in payload_1["score_breakdown"]


def test_get_stock_analysis_payload_marks_data_unavailable_on_fetch_failure() -> None:
    class _FailingOrchestrator:
        def get_full_ticker_data(self, ticker: str):
            return {
                "ticker": ticker,
                "is_ready": False,
                "data_unavailable": True,
                "data_unavailable_reason": "unable to open database file",
            }

    qs = QueryService(orchestrator=_FailingOrchestrator())
    payload = qs.get_stock_analysis_payload("NVDA", "NASDAQ", "2026-02-15")

    assert payload["data_unavailable"] is True
    assert payload["data_unavailable_reason"] == "unable to open database file"
    assert "data_unavailable" in payload["warnings"]
    assert payload["data_health"]["status"] == "unavailable"
