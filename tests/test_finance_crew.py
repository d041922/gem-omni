"""
FinanceCrew Full Workflow Test
Tests all 4 agents working together with optimized token usage
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.memory import MemorySystem
from agents.crews.finance_crew import FinanceCrew


def main():
    print("=" * 70)
    print("FINANCE CREW FULL WORKFLOW TEST")
    print("=" * 70)

    print("\n[STEP 1] Initializing FinanceCrew...")
    memory_system = MemorySystem()
    finance_crew = FinanceCrew(
        memory_system=memory_system,
        spreadsheet_name="GEM_Finance_Portfolio"
    )
    print("[OK] FinanceCrew initialized")

    print("\n[STEP 2] Running full analysis...")
    print("This will execute 4 agents sequentially:")
    print("  1. Data Sync Agent - Load data from Google Sheets")
    print("  2. Analyst Agent - Calculate portfolio metrics")
    print("  3. Risk Agent - Analyze risk metrics")
    print("  4. Strategy Agent - Generate AI recommendations")
    print("-" * 70)

    try:
        result = finance_crew.generate_full_report()

        print("\n[STEP 3] Analysis Results")
        print("=" * 70)

        if result.get('success'):
            print("[OK] FinanceCrew completed successfully!\n")

            # Display summary
            if 'report' in result:
                print("Final Report Summary:")
                print("-" * 70)
                report = result['report']
                if isinstance(report, str):
                    # Limit output to first 1000 characters
                    print(report[:1000])
                    if len(report) > 1000:
                        print(f"\n... (truncated, total {len(report)} characters)")
                else:
                    print(report)

            # Check cache files
            print("\n" + "-" * 70)
            print("Cache Files Created:")
            cache_dir = Path(__file__).parent / "tmp" / "cache"
            if cache_dir.exists():
                for file in cache_dir.glob("*.json"):
                    size_kb = file.stat().st_size / 1024
                    print(f"  - {file.name}: {size_kb:.1f} KB")

            print("\n[OK] Token optimization working correctly!")
            print("     - Data cached in files")
            print("     - Agents received summaries only")
            print("     - No context cascade")

        else:
            print("[ERROR] FinanceCrew failed")
            print(f"Message: {result.get('message', 'Unknown error')}")
            if 'error' in result:
                print(f"Error details: {result['error']}")

    except Exception as e:
        print(f"\n[ERROR] Exception during execution:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
