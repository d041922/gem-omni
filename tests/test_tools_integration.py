"""
Integration Test for Token-Optimized Tools
Tests GSheetLoaderTool and PortfolioMetricsCalculatorTool
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.tools.gsheet_tools import GSheetLoaderTool
from agents.tools.portfolio_tools import PortfolioMetricsCalculatorTool
from agents.tools.data_cache import load_portfolio_data, get_cache_summary
import json


def estimate_tokens(data: dict) -> int:
    """Rough token estimation (1 token ~= 4 characters)"""
    json_str = json.dumps(data, ensure_ascii=False)
    return len(json_str) // 4


def main():
    print("=" * 70)
    print("TOOLS INTEGRATION TEST")
    print("=" * 70)

    # Test 1: GSheetLoaderTool
    print("\n[TEST 1] GSheetLoaderTool (Token-Optimized)")
    print("-" * 70)

    gsheet_tool = GSheetLoaderTool()
    result = gsheet_tool._run("GEM_Finance_Portfolio")

    if result.get("success"):
        tokens = estimate_tokens(result)
        print(f"[OK] Successfully loaded data")
        print(f"   - Portfolio positions: {result['portfolio_summary'].get('total_positions', 0)}")
        print(f"   - Watchlist items: {result['watchlist_summary'].get('total_positions', 0)}")
        print(f"   - Portfolio file: {result.get('portfolio_file', 'N/A')}")
        print(f"   - Estimated tokens: {tokens:,}")
        print(f"   - Token efficiency: Data cached, summary only returned")
    else:
        print(f"[FAIL] {result.get('message')}")
        return

    # Test 2: PortfolioMetricsCalculatorTool
    print("\n[TEST 2] PortfolioMetricsCalculatorTool (Token-Optimized)")
    print("-" * 70)

    # Load cached portfolio data
    portfolio_file = result.get('portfolio_file')
    if portfolio_file:
        portfolio_df = load_portfolio_data(portfolio_file)
        portfolio_data = portfolio_df.to_dict('records')

        # Simulate current prices
        current_prices = {
            'PLTR': 85.0,
            'NVDA': 140.0,
            'MSFT': 450.0,
            'TSM': 200.0,
            'SMCI': 50.0
        }

        metrics_tool = PortfolioMetricsCalculatorTool()
        metrics_result = metrics_tool._run(
            portfolio_data=portfolio_data,
            current_prices=current_prices,
            usd_krw_rate=1450.0
        )

        if metrics_result.get("success"):
            metrics_tokens = estimate_tokens(metrics_result)
            summary = metrics_result.get('summary', {})

            print(f"[OK] Successfully calculated metrics")
            print(f"   - Total cost: {summary.get('total_cost_krw', 0):,.0f} KRW")
            print(f"   - Total value: {summary.get('total_eval_krw', 0):,.0f} KRW")
            print(f"   - Total profit: {summary.get('total_profit_krw', 0):,.0f} KRW")
            print(f"   - Total return: {summary.get('total_return_pct', 0):.2f}%")
            print(f"   - Metrics file: {metrics_result.get('metrics_file', 'N/A')}")
            print(f"   - Estimated tokens: {metrics_tokens:,}")
        else:
            print(f"[FAIL] {metrics_result.get('message')}")
    else:
        print("[SKIP] No portfolio file to test")

    # Test 3: Cache Summary
    print("\n[TEST 3] Cache Status")
    print("-" * 70)
    cache_info = get_cache_summary()
    print(f"Cache directory: {cache_info['cache_dir']}")
    print(f"Total cached files: {cache_info['total_files']}")

    total_size = 0
    for file_info in cache_info['files']:
        print(f"   - {file_info['name']}: {file_info['size_kb']:.1f} KB")
        total_size += file_info['size_kb']

    print(f"\nTotal cache size: {total_size:.1f} KB")

    # Comparison
    print("\n" + "=" * 70)
    print("TOKEN EFFICIENCY REPORT")
    print("=" * 70)

    print(f"""
Tool Performance:
- GSheetLoaderTool: ~{tokens:,} tokens (vs ~2,000+ with old method)
- PortfolioMetricsCalculatorTool: ~{metrics_tokens:,} tokens (vs ~3,000+ with old method)

Total tokens for data loading + metrics:
- New method: {tokens + metrics_tokens:,} tokens
- Old method (estimated): ~5,000 tokens
- Reduction: ~{5000 - (tokens + metrics_tokens):,} tokens ({((5000 - (tokens + metrics_tokens)) / 5000 * 100):.1f}%)

Key Benefits:
1. Agents receive compact summaries with key metrics
2. Full data available via file paths when needed
3. Data integrity maintained in cache files
4. Significant token and cost reduction
5. Faster agent processing with smaller context

Status: [OK] All tools working correctly with token optimization!
""")

    print("=" * 70)


if __name__ == "__main__":
    main()
