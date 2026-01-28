"""
AI Strategy Tools - 전략 에이전트 전용 도구 모음 (Optimized)
AI가 대화 중에 시스템 기능을 호출할 때 사용하며, 속도를 위해 캐시된 세션 데이터를 최우선으로 사용함.
"""
import streamlit as st
import json
from typing import Any, Type, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from skills.portfolio_utils import get_portfolio_summary
from skills.stock_analyzer import analyze_stock, get_fundamental_insight, get_technical_insight
from skills.policy_manager import PolicyManager

class StrategyToolInput(BaseModel):
    """Input schema for Gemini Strategy Tool"""
    action: str = Field(..., description="Action to perform: 'get_portfolio_status', 'analyze_stock', 'update_policy', 'get_policy', 'record_decision'")
    ticker: Optional[str] = Field(None, description="Stock ticker for analysis (e.g., 'AAPL')")
    policy_section: Optional[str] = Field(None, description="Policy section to update")
    policy_key: Optional[str] = Field(None, description="Policy key to update")
    policy_value: Optional[Any] = Field(None, description="New policy value")
    decision_action: Optional[str] = Field(None, description="Action taken for decision log")
    decision_reason: Optional[str] = Field(None, description="Reason for the decision")

class GeminiStrategyTool(BaseTool):
    name: str = "Gemini Strategy Execution Tool"
    description: str = (
        "A multi-functional tool for strategic operations. "
        "Can retrieve portfolio status, analyze specific stocks, reading/updating system policies, "
        "and recording strategic decisions. "
        "Select the appropriate 'action' and provide necessary parameters."
    )
    args_schema: Type[BaseModel] = StrategyToolInput

    def _run(self, action: str, ticker: Optional[str] = None, 
             policy_section: Optional[str] = None, policy_key: Optional[str] = None, policy_value: Optional[Any] = None,
             decision_action: Optional[str] = None, decision_reason: Optional[str] = None) -> str:
        
        try:
            if action == 'get_portfolio_status':
                return get_ai_portfolio_status()
            
            elif action == 'analyze_stock':
                if not ticker: return "Error: 'ticker' is required for stock analysis."
                return get_ai_stock_analysis(ticker)
            
            elif action == 'update_policy':
                if not (policy_section and policy_key and policy_value):
                    return "Error: section, key, and value are required for policy update."
                return update_system_policy(policy_section, policy_key, policy_value)
            
            elif action == 'get_policy':
                return get_current_policy()
            
            elif action == 'record_decision':
                if not (decision_action and decision_reason):
                    return "Error: action and reason are required for recording decision."
                return record_strategic_decision(decision_action, decision_reason)
            
            else:
                return f"Error: Unknown action '{action}'"
                
        except Exception as e:
            return f"Tool Execution Error: {str(e)}"

def get_ai_portfolio_status() -> str:
    """
    [속도 최적화] 현재 포트폴리오의 요약 상태를 반환합니다.
    외부 API 호출 없이 이미 로딩된 세션 데이터를 사용하여 즉시 응답합니다.
    """
    # 세션에서 직접 데이터 확인 (가장 빠름)
    if 'calculated_portfolio' not in st.session_state:
        return "데이터가 로딩되지 않았습니다. 홈 화면에서 '데이터 갱신'을 먼저 눌러주세요."

    df = st.session_state.calculated_portfolio
    summary = get_portfolio_summary() # 캐시된 DF 기반 계산
    
    if df is None or df.empty:
        return "포트폴리오가 비어 있습니다."

    # 상위 5개 종목 요약
    total_v = df['평가금액(KRW)'].sum()
    top_5 = df.nlargest(5, '평가금액(KRW)')
    holdings_list = []
    for _, row in top_5.iterrows():
        weight = (row['평가금액(KRW)'] / total_v) * 100
        holdings_list.append(f"- {row.get('종목명', 'Unknown')}: {weight:.1f}%")
    top_holdings = "\n".join(holdings_list)

    # 현금 비중 (세션에서 가져오기)
    cash_df = st.session_state.get('cash_df')
    total_cash = 0
    if cash_df is not None and not cash_df.empty:
        try:
            # 컬럼명 자동 탐색
            col = next((c for c in ['금액', 'amount', '금액(KRW)'] if c in cash_df.columns), None)
            if col: total_cash = cash_df[col].replace(',','', regex=True).astype(float).sum()
        except: pass

    status = f"""
[내 자산 현황 요약]
- 총 평가액(주식): ₩{total_v/1e8:.2f}억
- 현금 보유액: ₩{total_cash/1e6:.0f}백만
- 총 자산 합계: ₩{(total_v + total_cash)/1e8:.2f}억
- 주요 보유: {', '.join([h.split(':')[0] for h in top_5['종목명']])}

[섹터 비중]
{json.dumps(summary['sectors'], ensure_ascii=False)}
"""
    return status

def get_ai_stock_analysis(ticker: str) -> str:
    """
    특정 종목 분석 (캐시 우선)
    """
    # 이미 분석된 데이터가 세션에 있다면 재활용 가능하지만, 
    # 종목 분석은 실시간성이 중요하므로 API 호출 유지 (단, 로딩 메시지 필요)
    try:
        res = analyze_stock(ticker)
        if not res.get('success'):
            return f"분석 실패: {res.get('error')}"
        
        s = res['summary']
        analysis = f"""
[{ticker} 핵심 요약]
- 가격: ${s['current_price']:.2f} ({s['price_change_pct']:+.2f}%)
- 기술적: {get_technical_insight(s)}
- 펀더멘털: {get_fundamental_insight(s)}
"""
        return analysis
    except Exception as e:
        return f"분석 중 오류: {str(e)}"

def update_system_policy(section: str, key: str, value: Any) -> str:
    pm = PolicyManager()
    if pm.update_policy(section, key, value):
        return f"✅ 정책 수정 완료: {key} -> {value}"
    return "❌ 정책 수정 실패"

def get_current_policy() -> str:
    return PolicyManager().get_strategy_context()

def record_strategic_decision(action: str, reason: str) -> str:
    PolicyManager().add_decision_log(action, reason)
    return f"📝 기록됨: {action}"
