import pytest

def calculate_position_details(holding: dict, current_price: float):
    """UI에 표시될 상세 수익 데이터를 계산하는 로직 (To-be implemented)"""
    qty = holding.get('quantity', 0)
    avg_price = holding.get('average_price', 0)
    
    if qty <= 0 or avg_price <= 0 or current_price <= 0:
        return {"pnl_pct": 0.0, "pnl_val": 0.0, "formatted_pnl": "₩0"}
    
    total_cost = qty * avg_price
    current_value = qty * current_price
    pnl_val = current_value - total_cost
    pnl_pct = (pnl_val / total_cost) * 100
    
    return {
        "pnl_pct": round(pnl_pct, 2),
        "pnl_val": round(pnl_val, 2),
        "total_cost": total_cost,
        "current_value": current_value
    }

def test_position_calculation():
    """수익률 및 손익금액 계산 정확성 검증"""
    mock_holding = {"quantity": 10, "average_price": 100.0}
    current_p = 150.0 # 50% 상승 상황
    
    details = calculate_position_details(mock_holding, current_p)
    
    assert details["pnl_pct"] == 50.0
    assert details["pnl_val"] == 500.0
    assert details["current_value"] == 1500.0

def test_position_calculation_zero_case():
    """데이터 결측 시 방어 로직 검증"""
    invalid_holding = {"quantity": 0, "average_price": 0}
    details = calculate_position_details(invalid_holding, 100.0)
    assert details["pnl_pct"] == 0.0