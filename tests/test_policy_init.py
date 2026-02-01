from skills.policy_manager import PolicyManager, get_policy_context

def test_policy_manager():
    print("1. Initialize PolicyManager...")
    pm = PolicyManager()
    
    print("\n2. Initial Context Check:")
    print(pm.get_strategy_context())
    
    print("\n3. Update Policy Test...")
    pm.update_policy('constraints', 'min_cash_buffer_krw', 20000000)
    
    print("\n4. Add Decision Log Test...")
    pm.add_decision_log(
        action="포트폴리오 리밸런싱 지시", 
        reason="기술주 과열 우려로 비중 5% 축소 및 현금 확보",
        related_assets=["XLK", "NVDA"]
    )
    
    print("\n5. Updated Context Check:")
    print(get_policy_context())
    
    print("\nDone.")

if __name__ == "__main__":
    test_policy_manager()

