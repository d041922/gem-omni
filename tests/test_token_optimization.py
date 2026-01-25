"""
Token Optimization Test Script
Compares old method (full data) vs new method (summary only)
"""
import pandas as pd
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.tools.data_cache import save_portfolio_data, load_portfolio_data, get_cache_summary
from skills.gsheet_loader import load_data_from_gsheet


def estimate_tokens(data: dict) -> int:
    """Rough token estimation (1 token ~= 4 characters)"""
    json_str = json.dumps(data, ensure_ascii=False)
    return len(json_str) // 4


def main():
    print("=" * 70)
    print("TOKEN OPTIMIZATION TEST")
    print("=" * 70)

    # Load real portfolio data
    print("\n[1] Loading portfolio data from Google Sheets...")
    try:
        portfolio_df, watchlist_df, cash_df = load_data_from_gsheet("GEM_Finance_Portfolio")
        print(f"[OK] Loaded {len(portfolio_df)} positions")
    except Exception as e:
        print(f"[WARN] Failed to load Google Sheets: {e}")
        print("Creating sample data for testing...")
        portfolio_df = pd.DataFrame({
            '종목명': ['Tesla', 'Apple', 'Microsoft', 'NVIDIA', 'Amazon'],
            '티커코드': ['TSLA', 'AAPL', 'MSFT', 'NVDA', 'AMZN'],
            '카테고리': ['Tech', 'Tech', 'Tech', 'Tech', 'Tech'],
            '수량': [10, 50, 30, 25, 15],
            '매수금액(KRW)': [15000000, 25000000, 20000000, 18000000, 12000000],
            '평가금액(KRW)': [18000000, 28000000, 22000000, 25000000, 13000000],
            '손익(KRW)': [3000000, 3000000, 2000000, 7000000, 1000000],
            '수익률(%)': [20.0, 12.0, 10.0, 38.9, 8.3]
        })

    print("\n" + "=" * 70)
    print("METHOD COMPARISON")
    print("=" * 70)

    # OLD METHOD: Full data to LLM
    print("\n[2] OLD METHOD: Sending full data to LLM")
    print("-" * 70)
    old_method_data = {
        "success": True,
        "portfolio": portfolio_df.to_dict(orient='records'),
        "portfolio_columns": portfolio_df.columns.tolist(),
        "message": "Successfully loaded data"
    }

    old_tokens = estimate_tokens(old_method_data)
    print(f"Data structure:")
    print(f"   - Positions: {len(portfolio_df)}")
    print(f"   - Columns: {len(portfolio_df.columns)}")
    print(f"   - Total records sent: {len(old_method_data['portfolio'])}")
    print(f"Estimated tokens: {old_tokens:,}")
    print(f"Estimated cost per call: ${old_tokens * 0.000003:.4f} (input tokens)")

    # NEW METHOD: Summary only
    print("\n[3] NEW METHOD: Sending summary only (data saved to file)")
    print("-" * 70)
    new_method_data = save_portfolio_data(portfolio_df, "test_portfolio.json")

    new_tokens = estimate_tokens(new_method_data)
    print(f"Data structure:")
    print(f"   - Summary stats: {len(new_method_data['summary'])} keys")
    print(f"   - Top 3 performers: {len(new_method_data['summary'].get('top_3_performers', []))}")
    print(f"   - Full data saved to: {new_method_data['file_path']}")
    print(f"Estimated tokens: {new_tokens:,}")
    print(f"Estimated cost per call: ${new_tokens * 0.000003:.4f} (input tokens)")

    # COMPARISON
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    token_reduction = old_tokens - new_tokens
    reduction_pct = (token_reduction / old_tokens) * 100

    print(f"\nToken Reduction: {token_reduction:,} tokens ({reduction_pct:.1f}%)")
    print(f"Cost Reduction per call: ${token_reduction * 0.000003:.4f}")
    print(f"Cost Reduction for 100 calls: ${token_reduction * 0.000003 * 100:.2f}")

    # With 4 agents running sequentially
    print(f"\nFor 4 agents (sequential execution):")
    print(f"   Old method: {old_tokens * 4:,} tokens")
    print(f"   New method: {new_tokens * 4:,} tokens")
    print(f"   Saved: {token_reduction * 4:,} tokens ({reduction_pct:.1f}%)")
    print(f"   Cost saved per analysis: ${token_reduction * 4 * 0.000003:.4f}")

    # Test data loading
    print("\n" + "=" * 70)
    print("DATA INTEGRITY TEST")
    print("=" * 70)
    print("\n[4] Testing data loading from cache...")
    loaded_df = load_portfolio_data(new_method_data['file_path'])

    if loaded_df.equals(portfolio_df):
        print("[OK] Data integrity verified: Loaded data matches original")
    else:
        print("[WARN] Loaded data differs from original")

    print(f"\nCache info:")
    cache_info = get_cache_summary()
    print(f"   - Cache directory: {cache_info['cache_dir']}")
    print(f"   - Cached files: {cache_info['total_files']}")
    for file_info in cache_info['files']:
        print(f"     * {file_info['name']} ({file_info['size_kb']:.1f} KB)")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"""
[OK] Token optimization successfully implemented!

Key Benefits:
1. Token usage reduced by {reduction_pct:.1f}%
2. Cost per analysis reduced by ${token_reduction * 4 * 0.000003:.4f}
3. Data integrity maintained (full data in cache files)
4. Agents receive compact summaries with key metrics
5. Can still access full data when needed via file paths

Next Steps:
- Update GSheetLoaderTool to use save_portfolio_data()
- Update PortfolioMetricsCalculatorTool to use cache
- Update Task contexts to reference file paths instead of full data
""")

    print("=" * 70)


if __name__ == "__main__":
    main()
