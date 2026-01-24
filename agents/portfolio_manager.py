import pandas as pd
import yfinance as yf
from typing import List, Dict, Any, Tuple
from core.models import Asset, Portfolio, StrategyReport
from skills.gsheet_loader import load_data_from_gsheet
from skills.finance_core_lib import calculate_portfolio_metrics
from agents.quant_analyst import QuantAnalyst

class PortfolioManager:
    """자산 사령부의 팀장 에이전트"""
    def __init__(self, memory: Any = None):
        self.memory = memory
        self.quant = QuantAnalyst()
        self.current_portfolio = Portfolio()
        self.spreadsheet_name = "GEM_Finance_Portfolio"

    def sync_all(self) -> Portfolio:
        """구글 시트와 API 데이터를 가져와 병합 및 계산함."""
        # 1. 구글 시트 데이터 로드
        pf_df, wl_df, cash_df = load_data_from_gsheet(self.spreadsheet_name)
        if pf_df.empty: return self.current_portfolio

        # 2. 실시간 가격 및 환율 정보 획득
        tickers = pf_df['종목코드'].dropna().unique().tolist()
        api_tickers = [t for t in tickers if not str(t).endswith('.KS') and t != '']
        
        try:
            rate = yf.Ticker("USDKRW=X").history(period='1d')['Close'].iloc[-1]
        except: rate = 1450.0 # Fallback
        
        current_prices = {}
        if api_tickers:
            try:
                price_data = yf.download(api_tickers, period='1d', progress=False)['Close']
                if isinstance(price_data, pd.Series):
                    current_prices = {api_tickers[0]: price_data.iloc[-1]}
                else:
                    current_prices = price_data.iloc[-1].to_dict()
            except: pass

        # 3. 정밀 계산 (Skill 호출)
        df_calc = calculate_portfolio_metrics(pf_df, current_prices, rate)
        
        # 4. Asset 객체화
        updated_assets = []
        portfolio_dict_list = []
        for _, row in df_calc.iterrows():
            asset = Asset(
                ticker=str(row.get('종목코드', 'UNKNOWN')),
                name=str(row.get('종목명', 'Unknown')),
                amount=float(row.get('수량', 0)),
                avg_price=float(row.get('평균 단가(KRW)', 0) if row.get('통화') == 'KRW' else row.get('평균 단가(USD)', 0)),
                current_price=float(row.get('최종현재가', 0)),
                currency=str(row.get('통화', 'KRW')),
                category=str(row.get('계좌구분', '기타')),
                source="GSheet",
                total_purchase_value=float(row.get('매수금액(KRW)', 0)),
                total_evaluation_value=float(row.get('평가금액(KRW)', 0)),
                profit_amount=float(row.get('손익(KRW)', 0)),
                profit_pct=float(row.get('수익률(%)', 0))
            )
            updated_assets.append(asset)
            
            d = asset.model_dump()
            portfolio_dict_list.append(d)
            
        self.current_portfolio.assets = updated_assets
        self.current_portfolio.total_asset_value = df_calc['평가금액(KRW)'].sum()
        
        # 5. 메모리 저장
        if self.memory:
            self.memory.user_profile['portfolio'] = portfolio_dict_list
            self.memory.user_profile['total_asset_value'] = self.current_portfolio.total_asset_value
            self.memory.save_all_memory()
            
        return self.current_portfolio

    def get_full_command_report(self, ai_agent: Any) -> Tuple[StrategyReport, Dict[str, Any]]:
        """AI 분석 보고서와 퀀트 리포트를 한 번에 생성"""
        if not self.current_portfolio.assets:
            self.sync_all()
            
        risk_data = self.quant.analyze_portfolio_risk(self.current_portfolio.assets)
        report = ai_agent.generate_portfolio_strategy(self.current_portfolio.assets, risk_data)
        
        return report, risk_data