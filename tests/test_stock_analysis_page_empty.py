from unittest.mock import MagicMock, patch

from pages.stock_analysis import render_stock_analysis


def _ctx() -> MagicMock:
    m = MagicMock()
    m.__enter__.return_value = m
    m.__exit__.return_value = False
    return m


def _prepare_streamlit(mock_st: MagicMock) -> None:
    mock_st.session_state = {}
    mock_st.columns.side_effect = lambda spec: [_ctx() for _ in range(spec if isinstance(spec, int) else len(spec))]
    mock_st.tabs.return_value = [_ctx(), _ctx(), _ctx(), _ctx(), _ctx()]
    mock_st.sidebar = _ctx()
    mock_st.expander.return_value = _ctx()
    mock_st.spinner.return_value = _ctx()


def test_stock_analysis_warns_when_no_search_candidates() -> None:
    with patch("pages.stock_analysis.load_custom_css"):
        with patch("pages.stock_analysis.TickerSearchEngine") as mock_search_cls:
            with patch("pages.stock_analysis.DataOrchestrator"):
                with patch("pages.stock_analysis.MarketScreener"):
                    with patch("pages.stock_analysis.ResearchEngine"):
                        with patch("pages.stock_analysis.st") as mock_st:
                            _prepare_streamlit(mock_st)
                            mock_st.text_input.return_value = "UNKNOWN"
                            mock_st.button.return_value = False

                            mock_search = mock_search_cls.return_value
                            mock_search.search_symbols.return_value = []

                            render_stock_analysis()
                            assert mock_st.warning.called


def test_stock_analysis_renders_expected_tabs() -> None:
    with patch("pages.stock_analysis.load_custom_css"):
        with patch("pages.stock_analysis.TickerSearchEngine") as mock_search_cls:
            with patch("pages.stock_analysis.DataOrchestrator") as mock_orch_cls:
                with patch("pages.stock_analysis.MarketScreener"):
                    with patch("pages.stock_analysis.ResearchEngine"):
                        with patch("pages.stock_analysis.st") as mock_st:
                            _prepare_streamlit(mock_st)
                            mock_st.text_input.return_value = "NVDA"
                            mock_st.selectbox.return_value = "NVIDIA (NVDA)"
                            mock_st.button.return_value = False
                            mock_st.cache_data.clear = MagicMock()

                            mock_search = mock_search_cls.return_value
                            mock_search.search_symbols.return_value = [
                                {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"}
                            ]

                            mock_orch = mock_orch_cls.return_value
                            mock_orch.read_state.return_value = {"data": {"portfolio": {"holdings": []}}}
                            mock_orch.get_full_ticker_data.return_value = {
                                "history": {},
                                "is_ready": False,
                                "holding_info": {},
                                "last_price": 120.0,
                                "extra_stats": {},
                                "market_context": {},
                            }

                            render_stock_analysis()
                            assert mock_st.tabs.called
                            labels = mock_st.tabs.call_args[0][0]
                            assert len(labels) == 5


def test_stock_analysis_uses_legacy_tab_renderers() -> None:
    with patch("pages.stock_analysis.load_custom_css"):
        with patch("pages.stock_analysis.TickerSearchEngine") as mock_search_cls:
            with patch("pages.stock_analysis.DataOrchestrator") as mock_orch_cls:
                with patch("pages.stock_analysis.MarketScreener"):
                    with patch("pages.stock_analysis.ResearchEngine"):
                        with patch("pages.stock_analysis.render_profile_tab") as mock_profile:
                            with patch("pages.stock_analysis.render_technical_tab") as mock_technical:
                                with patch("pages.stock_analysis.render_fundamental_tab") as mock_fundamental:
                                    with patch("pages.stock_analysis.st") as mock_st:
                                        _prepare_streamlit(mock_st)
                                        mock_st.text_input.return_value = "NVDA"
                                        mock_st.selectbox.return_value = "NVIDIA (NVDA)"
                                        mock_st.button.return_value = False
                                        mock_st.cache_data.clear = MagicMock()

                                        mock_search = mock_search_cls.return_value
                                        mock_search.search_symbols.return_value = [
                                            {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"}
                                        ]

                                        mock_orch = mock_orch_cls.return_value
                                        mock_orch.read_state.return_value = {"data": {"portfolio": {"holdings": []}}}
                                        mock_orch.get_full_ticker_data.return_value = {
                                            "history": {
                                                "Open": [99, 109],
                                                "High": [101, 111],
                                                "Low": [98, 108],
                                                "Close": [100, 110],
                                                "Volume": [1_000_000, 1_100_000],
                                            },
                                            "is_ready": True,
                                            "holding_info": {},
                                            "last_price": 120.0,
                                            "extra_stats": {},
                                            "market_context": {},
                                        }

                                        render_stock_analysis()
                                        assert mock_profile.called
                                        assert mock_technical.called
                                        assert mock_fundamental.called
