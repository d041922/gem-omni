import pytest
import importlib

def test_pages_contract():
    """4대 허브 페이지가 필수 렌더링 함수를 보유하고 있는지 확인"""
    pages = [
        ("pages.market_overview", "render_market_overview"),
        ("pages.screener", "render_screener"),
        ("pages.stock_analysis", "render_stock_analysis")
    ]
    
    for module_path, function_name in pages:
        try:
            module = importlib.import_module(module_path)
            assert hasattr(module, function_name), f"{module_path}에 {function_name} 함수가 없습니다."
        except ModuleNotFoundError:
            pytest.fail(f"{module_path} 파일이 존재하지 않습니다.")

def test_app_routing_config():
    """app.py에서 새로운 4단 라우팅 메뉴가 정의되어 있는지 논리적 확인"""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
        # 신규 메뉴 키워드 포함 여부 확인
        expected_menus = ["market", "screener", "analysis"]
        for menu in expected_menus:
            assert menu in content.lower(), f"app.py에 '{menu}' 라우팅 로직이 누락된 것으로 보입니다."
