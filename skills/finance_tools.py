"""Legacy finance tools compatibility helpers."""

from skills.ticker_search import TickerSearchEngine


def search_ticker_by_name(query: str) -> str:
    """Return the best-match symbol for a query, or empty string."""
    engine = TickerSearchEngine()
    results = engine.search_symbols(query)
    return results[0]["symbol"] if results else ""
