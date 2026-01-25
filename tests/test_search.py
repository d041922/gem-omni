from skills.finance_tools import search_ticker_by_name

queries = ["삼성전자", "삼전", "애플", "엔비디아"]

print("=== Ticker Search Diagnostics ===")
for q in queries:
    result = search_ticker_by_name(q)
    print(f"Query: '{q}' -> Result: {result}")
