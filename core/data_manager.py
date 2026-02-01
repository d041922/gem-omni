"""
Central Data Manager [GEM: OMNI] - Strategic Edition
Handles global macro, portfolio mapping, and master profile integration.
"""
import streamlit as st
import yfinance as yf
import pandas as pd
from typing import Dict
from core.models import Portfolio, MacroIndicators

class DataManager:
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_macro_indicators() -> MacroIndicators:
        """글로벌 거시 지표 수집"""
        try:
            usd_krw = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1]
            us_10y = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            nasdaq_hist = yf.Ticker("^IXIC").history(period="2d")['Close']
            kospi_hist = yf.Ticker("^KS11").history(period="2d")['Close']
            btc = yf.Ticker("BTC-USD").history(period="1d")['Close'].iloc[-1]
            
            nq_change = ((nasdaq_hist.iloc[-1] - nasdaq_hist.iloc[-2]) / nasdaq_hist.iloc[-2] * 100) if len(nasdaq_hist) > 1 else 0
            ks_change = ((kospi_hist.iloc[-1] - kospi_hist.iloc[-2]) / kospi_hist.iloc[-2] * 100) if len(kospi_hist) > 1 else 0
            
            return MacroIndicators(
                usd_krw=float(usd_krw), us_10y_yield=float(us_10y), vix=float(vix),
                nasdaq_change=float(nq_change), kospi_change=float(ks_change),
                btc_price=float(btc)
            )
        except Exception:
            return MacroIndicators(1450.0, 4.2, 15.0, 0.0, 0.0, 95000.0)

    @staticmethod
    @st.cache_data(ttl=86400)
    def get_ticker_mapping() -> Dict[str, str]:
        """티커와 실제 종목명 매핑 테이블 (주요 종목 우선)"""
        return {
            "AAPL": "애플", "NVDA": "엔비디아", "MSFT": "마이크로소프트", 
            "GOOGL": "구글", "TSLA": "테슬라", "PLTR": "팔란티어",
            "AMZN": "아마존", "META": "메타", "005930.KS": "삼성전자",
            "000660.KS": "SK하이닉스", "379810.KS": "TIGER 미국나스닥100",
            "423180.KS": "TIGER 필라델피아반도체", "487230.KS": "KODEX AI전력핵심인프라"
        }

    @staticmethod
    def get_portfolio_data(force_refresh: bool = False) -> Portfolio:
        """마스터 프로필 및 매크로가 통합된 포트폴리오 로드"""
        from skills.gsheet_loader import load_data_from_gsheet, load_mandalart_goals
        from skills.finance_core_lib import calculate_portfolio_metrics
        
        if force_refresh or 'portfolio_obj' not in st.session_state:
            spreadsheet_name = "GEM_Finance_Portfolio"
            p_df, w_df, c_df = load_data_from_gsheet(spreadsheet_name)
            goal_data = load_mandalart_goals(spreadsheet_name)
            macro = DataManager.get_macro_indicators()
            mapping = DataManager.get_ticker_mapping()
            
            # 컬럼 표준화
            def standardize_col(df, target, candidates):
                for c in candidates:
                    if c in df.columns:
                        if c != target:
                            df = df.rename(columns={c: target})
                        others = [x for x in candidates if x in df.columns and x != target]
                        df = df.drop(columns=others)
                        break
                return df

            p_df = standardize_col(p_df, '종목코드', ['종목코드', '티커코드', 'symbol'])
            p_df = standardize_col(p_df, '계좌', ['account', 'Account'])
            
            current_prices = {}
            for ticker in p_df['종목코드'].dropna().unique():
                ticker_str = str(ticker).strip()
                try:
                    price = yf.Ticker(ticker_str).history(period="1d")['Close'].iloc[-1]
                    current_prices[ticker_str] = float(price)
                except Exception:
                    current_prices[ticker_str] = 0.0
            
            calc_df = calculate_portfolio_metrics(p_df, current_prices, macro.usd_krw)
            
            # 종목명 매핑 및 반올림
            calc_df['종목명'] = calc_df['종목코드'].map(mapping).fillna(calc_df['종목코드'])
            calc_df['수량'] = calc_df['수량'].round(2)
            
            total_stock = calc_df['평가금액(KRW)'].sum()
            total_cost = calc_df['매수금액(KRW)'].sum()
            total_cash = 0
            if not c_df.empty:
                c_col = next((c for c in ['금액', 'amount', '금액(KRW)'] if c in c_df.columns), None)
                if c_col:
                    total_cash = pd.to_numeric(c_df[c_col], errors='coerce').sum()

            best_stock = calc_df.nlargest(1, '수익률(%)').iloc[0]['종목명'] if not calc_df.empty else "N/A"
            insight = f"🔍 **AI Insight**: 환율 {macro.usd_krw:,.1f}원과 국채 금리 {macro.us_10y_yield:.2f}%를 고려할 때, 현재 나스닥 지수는 {macro.nasdaq_change:+.2f}% 움직이고 있습니다. {best_stock}의 성과가 두드러집니다."

            p_obj = Portfolio(
                total_net_worth_krw=total_stock + total_cash,
                stock_value_krw=total_stock, cash_krw=total_cash,
                profit_krw=total_stock - total_cost,
                return_pct=((total_stock - total_cost) / total_cost * 100) if total_cost > 0 else 0,
                goal_amount_krw=float(goal_data['total_goal']),
                daily_insight=insight,
                macro=macro,
                holdings=calc_df.to_dict(orient='records')
            )
            st.session_state.portfolio_obj = p_obj
            
        return st.session_state.portfolio_obj

def get_data_manager(): return DataManager()