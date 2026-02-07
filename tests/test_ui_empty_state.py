import pytest
from unittest.mock import MagicMock, patch, call
from pages.wealth_home import render_wealth_home

@pytest.fixture
def mock_streamlit():
    with patch('pages.wealth_home.st') as mock_st:
        # Session State 모킹 (속성 접근 지원)
        mock_st.session_state = MagicMock()
        mock_st.session_state.current_page = "wealth" # 기본값 설정
        
        # Columns 모킹 (Dynamic Unpacking 지원)
        def columns_side_effect(spec):
            count = spec if isinstance(spec, int) else len(spec)
            return [MagicMock() for _ in range(count)]
        
        mock_st.columns.side_effect = columns_side_effect
        yield mock_st

@pytest.fixture
def mock_orchestrator():
    with patch('pages.wealth_home.DataOrchestrator') as MockOrch:
        instance = MockOrch.return_value
        # 빈 데이터 상황 시뮬레이션
        instance.read_state.return_value = {
            "data": {
                "portfolio": {"summary": {}, "holdings": []}, # 데이터 없음
                "intelligence": {"screener_results": []}
            }
        }
        yield instance

def test_no_phantom_cards_on_empty_data(mock_streamlit, mock_orchestrator):
    """
    UT-UI-01: 데이터가 없을 때 'glass-card' 스타일의 빈 박스가 렌더링되지 않아야 한다.
    """
    render_wealth_home()
    
    # st.markdown 호출 인자들을 전수 조사
    markdown_calls = mock_streamlit.markdown.call_args_list
    
    # 'glass-card' 클래스가 포함된 마크다운 호출 횟수 카운트
    # 예상: Header용 카드들은 있겠지만, Row 2(Deep Analysis)나 Row 3(Inventory)의 카드는 없어야 함.
    
    glass_card_calls = [
        args[0] for args, _ in markdown_calls 
        if args and "glass-card" in str(args[0])
    ]
    
    # 상단 Metric Card 3개는 항상 나오므로 최소 3개는 있음.
    # 하지만 데이터가 없으면 Row 2, Row 3의 컨테이너용 glass-card는 없어야 함.
    # 현재 코드에서는 Row 2(Main, Side), Row 3에 대해 glass-card div를 열고 있음.
    
    # 실패 조건: 데이터가 없는데도 Row 3(Inventory) 영역의 glass-card가 생성됨
    # Row 3는 "Detailed Asset Inventory" 헤더를 포함함.
    
    row3_leak = any("Detailed Asset Inventory" in str(c) for c in markdown_calls)
    
    assert not row3_leak, "데이터가 없는데 Row 3(Inventory) 섹션이 렌더링되었습니다."
