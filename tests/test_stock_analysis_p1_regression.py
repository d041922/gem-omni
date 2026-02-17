from unittest.mock import MagicMock, patch

import pandas as pd
from datetime import datetime, timedelta, timezone

from pages.analysis_tabs.fundamental import render_fundamental_tab
from pages.stock_analysis import render_stock_analysis


def _ctx() -> MagicMock:
    m = MagicMock()
    m.__enter__.return_value = m
    m.__exit__.return_value = False
    return m


def _prepare_streamlit(mock_st: MagicMock, session_state: dict | None = None) -> None:
    mock_st.session_state = session_state or {}
    mock_st.columns.side_effect = lambda spec: [
        _ctx() for _ in range(spec if isinstance(spec, int) else len(spec))
    ]
    mock_st.tabs.return_value = [_ctx(), _ctx(), _ctx(), _ctx(), _ctx()]
    mock_st.sidebar = _ctx()
    mock_st.expander.return_value = _ctx()
    mock_st.spinner.return_value = _ctx()


def test_fundamental_tab_uses_neutral_comparison_copy() -> None:
    with patch("pages.analysis_tabs.fundamental.st") as mock_st:
        _prepare_streamlit(mock_st)

        with patch(
            "pages.analysis_tabs.fundamental.FactorEngine.generate_comprehensive_verdict",
            return_value={"valuation": "v", "growth": "g", "risk": "r"},
        ):
            with patch(
                "pages.analysis_tabs.fundamental.FactorEngine.generate_peer_comparison",
                return_value="peer summary",
            ):
                with patch(
                    "pages.analysis_tabs.fundamental.FactorEngine.generate_fundamental_report",
                    return_value=[],
                ):
                    screener = MagicMock()
                    screener.get_financial_data.return_value = pd.DataFrame()
                    render_fundamental_tab("NVDA", screener, {"profile": {"sector": "Technology"}}, 100.0)

        rendered = [c.args[0] for c in mock_st.markdown.call_args_list if c.args]
        assert any("상대 평가" in s for s in rendered)
        assert all("압도적 최상위" not in s for s in rendered)


def test_stock_analysis_f_score_badge_uses_research_metadata_details() -> None:
    with patch("pages.stock_analysis.load_custom_css"):
        with patch("pages.stock_analysis.TickerSearchEngine") as mock_search_cls:
            with patch("pages.stock_analysis.DataOrchestrator") as mock_orch_cls:
                with patch("pages.stock_analysis.MarketScreener"):
                    with patch("pages.stock_analysis.ResearchEngine"):
                        with patch("pages.stock_analysis.render_profile_tab"):
                            with patch("pages.stock_analysis.render_technical_tab"):
                                with patch("pages.stock_analysis.render_fundamental_tab"):
                                    with patch(
                                        "pages.stock_analysis.get_analyst_ratings",
                                        return_value={
                                            "consensus": "Hold",
                                            "total_analysts": 0,
                                            "status": "limited_data",
                                        },
                                    ):
                                        with patch(
                                            "pages.stock_analysis.analyze_news_sentiment",
                                            return_value="➡️ 중립",
                                        ):
                                            with patch("pages.stock_analysis.st") as mock_st:
                                                _prepare_streamlit(
                                                    mock_st,
                                                    session_state={
                                                        "news_NVDA": [],
                                                        "research_NVDA": {
                                                            "metadata": {
                                                                "details": {
                                                                    "f_score_rating": "Strong Quality (우량)"
                                                                }
                                                            }
                                                        },
                                                    },
                                                )
                                                mock_st.text_input.return_value = "NVDA"
                                                mock_st.selectbox.return_value = "NVIDIA (NVDA)"
                                                mock_st.button.return_value = False
                                                mock_st.cache_data.clear = MagicMock()

                                                mock_search = mock_search_cls.return_value
                                                mock_search.search_symbols.return_value = [
                                                    {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"}
                                                ]

                                                mock_orch = mock_orch_cls.return_value
                                                mock_orch.read_state.return_value = {
                                                    "data": {"portfolio": {"holdings": []}}
                                                }
                                                mock_orch.get_full_ticker_data.return_value = {
                                                    "history": {"Close": [100, 101]},
                                                    "is_ready": False,
                                                    "holding_info": {},
                                                    "last_price": 120.0,
                                                    "extra_stats": {},
                                                    "market_context": {},
                                                }

                                                render_stock_analysis()

        rendered = [c.args[0] for c in mock_st.markdown.call_args_list if c.args]
        f_score_blocks = [s for s in rendered if "F-Score" in s]
        assert f_score_blocks
        assert any("Strong Quality (우량)" in s for s in f_score_blocks)


def test_stock_analysis_news_timeline_escapes_html_like_content() -> None:
    with patch("pages.stock_analysis.load_custom_css"):
        with patch("pages.stock_analysis.TickerSearchEngine") as mock_search_cls:
            with patch("pages.stock_analysis.DataOrchestrator") as mock_orch_cls:
                with patch("pages.stock_analysis.MarketScreener"):
                    with patch("pages.stock_analysis.ResearchEngine"):
                        with patch("pages.stock_analysis.render_profile_tab"):
                            with patch("pages.stock_analysis.render_technical_tab"):
                                with patch("pages.stock_analysis.render_fundamental_tab"):
                                    with patch(
                                        "pages.stock_analysis.get_analyst_ratings",
                                        return_value={
                                            "consensus": "Hold",
                                            "total_analysts": 0,
                                            "status": "limited_data",
                                        },
                                    ):
                                        with patch("pages.stock_analysis.st") as mock_st:
                                            _prepare_streamlit(
                                                mock_st,
                                                session_state={
                                                    "news_NVDA": [
                                                        {
                                                            "headline": "More for you <<tag>>",
                                                            "sentiment": "Neutral",
                                                            "summary": "line1\nline2 <b>raw</b>",
                                                        }
                                                    ],
                                                    "research_NVDA": {"metadata": {"details": {}}},
                                                },
                                            )
                                            mock_st.text_input.return_value = "NVDA"
                                            mock_st.selectbox.return_value = "NVIDIA (NVDA)"
                                            mock_st.button.return_value = False
                                            mock_st.cache_data.clear = MagicMock()

                                            mock_search = mock_search_cls.return_value
                                            mock_search.search_symbols.return_value = [
                                                {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"}
                                            ]

                                            mock_orch = mock_orch_cls.return_value
                                            mock_orch.read_state.return_value = {
                                                "data": {"portfolio": {"holdings": []}}
                                            }
                                            mock_orch.get_full_ticker_data.return_value = {
                                                "history": {"Close": [100, 101]},
                                                "is_ready": False,
                                                "holding_info": {},
                                                "last_price": 120.0,
                                                "extra_stats": {},
                                                "market_context": {},
                                            }

                                            render_stock_analysis()

    rendered = [c.args[0] for c in mock_st.markdown.call_args_list if c.args]
    timeline_blocks = [s for s in rendered if "More for you" in s]
    assert timeline_blocks
    assert any("&lt;&lt;tag&gt;&gt;" in s for s in timeline_blocks)
    assert any("line1<br>line2 &lt;b&gt;raw&lt;/b&gt;" in s for s in timeline_blocks)


def test_stock_analysis_research_reuses_news_cache_for_consistency() -> None:
    with patch("pages.stock_analysis.load_custom_css"):
        with patch("pages.stock_analysis.TickerSearchEngine") as mock_search_cls:
            with patch("pages.stock_analysis.DataOrchestrator") as mock_orch_cls:
                with patch("pages.stock_analysis.MarketScreener"):
                    with patch("pages.stock_analysis.ResearchEngine") as mock_research_cls:
                        with patch("pages.stock_analysis.render_profile_tab"):
                            with patch("pages.stock_analysis.render_technical_tab"):
                                with patch("pages.stock_analysis.render_fundamental_tab"):
                                    with patch(
                                        "pages.stock_analysis.get_analyst_ratings",
                                        return_value={
                                            "consensus": "Hold",
                                            "total_analysts": 0,
                                            "status": "limited_data",
                                        },
                                    ):
                                        with patch(
                                            "pages.stock_analysis.analyze_news_sentiment",
                                            return_value="➡️ 중립",
                                        ):
                                            with patch("pages.stock_analysis.st") as mock_st:
                                                cached_news = [
                                                    {"headline": "h1", "sentiment": "Neutral", "summary": "s1"}
                                                ]
                                                _prepare_streamlit(
                                                    mock_st,
                                                    session_state={"news_NVDA": cached_news},
                                                )
                                                mock_st.text_input.return_value = "NVDA"
                                                mock_st.selectbox.return_value = "NVIDIA (NVDA)"
                                                mock_st.button.return_value = False
                                                mock_st.cache_data.clear = MagicMock()

                                                mock_search = mock_search_cls.return_value
                                                mock_search.search_symbols.return_value = [
                                                    {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"}
                                                ]

                                                mock_orch = mock_orch_cls.return_value
                                                mock_orch.read_state.return_value = {
                                                    "data": {"portfolio": {"holdings": []}}
                                                }
                                                mock_ticker_info = {
                                                    "ticker": "NVDA",
                                                    "history": {"Close": [100, 101]},
                                                    "is_ready": False,
                                                    "holding_info": {},
                                                    "last_price": 120.0,
                                                    "extra_stats": {},
                                                    "market_context": {},
                                                }
                                                mock_orch.get_full_ticker_data.return_value = mock_ticker_info

                                                mock_research = mock_research_cls.return_value
                                                mock_research.get_report_with_cache.return_value = {"metadata": {}}

                                                render_stock_analysis()

    assert mock_research.get_report_with_cache.called
    args, kwargs = mock_research.get_report_with_cache.call_args
    assert args and args[0] == "NVDA"
    assert kwargs.get("market_news") == cached_news
    assert kwargs.get("ticker_info") == mock_ticker_info


def test_stock_analysis_news_shows_source_asof_and_stale_warning() -> None:
    stale_iso = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
    with patch("pages.stock_analysis.load_custom_css"):
        with patch("pages.stock_analysis.TickerSearchEngine") as mock_search_cls:
            with patch("pages.stock_analysis.DataOrchestrator") as mock_orch_cls:
                with patch("pages.stock_analysis.MarketScreener"):
                    with patch("pages.stock_analysis.ResearchEngine"):
                        with patch("pages.stock_analysis.render_profile_tab"):
                            with patch("pages.stock_analysis.render_technical_tab"):
                                with patch("pages.stock_analysis.render_fundamental_tab"):
                                    with patch(
                                        "pages.stock_analysis.get_analyst_ratings",
                                        return_value={
                                            "consensus": "Hold",
                                            "total_analysts": 0,
                                            "status": "limited_data",
                                        },
                                    ):
                                        with patch(
                                            "pages.stock_analysis.analyze_news_sentiment",
                                            return_value="Neutral",
                                        ):
                                            with patch("pages.stock_analysis.st") as mock_st:
                                                _prepare_streamlit(
                                                    mock_st,
                                                    session_state={
                                                        "news_NVDA": [
                                                            {
                                                                "headline": "h1",
                                                                "sentiment": "Neutral",
                                                                "summary": "s1",
                                                                "source": "yFinance",
                                                                "published_at": stale_iso,
                                                                "url": "https://example.com/n1",
                                                            }
                                                        ],
                                                        "research_NVDA": {"metadata": {"details": {}}},
                                                    },
                                                )
                                                mock_st.text_input.return_value = "NVDA"
                                                mock_st.selectbox.return_value = "NVIDIA (NVDA)"
                                                mock_st.button.return_value = False
                                                mock_st.cache_data.clear = MagicMock()

                                                mock_search = mock_search_cls.return_value
                                                mock_search.search_symbols.return_value = [
                                                    {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"}
                                                ]

                                                mock_orch = mock_orch_cls.return_value
                                                mock_orch.read_state.return_value = {
                                                    "data": {"portfolio": {"holdings": []}}
                                                }
                                                mock_orch.get_full_ticker_data.return_value = {
                                                    "history": {"Close": [100, 101]},
                                                    "is_ready": False,
                                                    "holding_info": {},
                                                    "last_price": 120.0,
                                                    "extra_stats": {},
                                                    "market_context": {},
                                                }

                                                render_stock_analysis()

    rendered = [c.args[0] for c in mock_st.markdown.call_args_list if c.args]
    assert any("source: yFinance" in s and "as_of:" in s for s in rendered)
    assert any("View source" in s for s in rendered)
    assert mock_st.warning.called
