"""
Agent Briefing Skill - 시스템의 지능형 요약 및 전략 제안 엔진
마스터의 자산, 현금, 시장 상황을 종합하여 '오늘의 행동'을 제안함
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class AgentBriefing:
    def __init__(self, portfolio_df: pd.DataFrame, cash_df: pd.DataFrame, market_data: Dict):
        self.portfolio = portfolio_df
        self.cash = cash_df
        self.market = market_data
        
    def generate_briefing(self) -> Dict[str, Any]:
        """마스터를 위한 종합 브리핑 생성"""
        nudges = []
        
        # 1. 현금 전략 분석 (Reference: ISA/IRP 절세 전략)
        total_cash = 0
        if not self.cash.empty:
            # 금액 컬럼 찾기 (한글/영문 대응)
            amt_col = '금액' if '금액' in self.cash.columns else 'amount'
            if amt_col in self.cash.columns:
                total_cash = self.cash[amt_col].sum()
                
                # 전략 1: ISA 납입 유도 (현금 비중이 높을 때)
                if total_cash > 10000000: # 1천만원 이상 유휴 현금
                    nudges.append({
                        "type": "Tax",
                        "title": "💎 ISA 절세 계좌 활용",
                        "content": f"현재 ₩{total_cash/1e6:.0f}M의 유휴 현금이 확인됩니다. 연간 2,000만원 한도의 ISA 계좌를 활용해 배당소득세를 절세하세요."
                    })

        # 2. 포트폴리오 건강도 체크
        if not self.portfolio.empty:
            total_v = self.portfolio['평가금액(KRW)'].sum()
            
            # 전략 2: 집중도 리스크
            top_stock = self.portfolio.nlargest(1, '평가금액(KRW)').iloc[0]
            weight = (top_stock['평가금액(KRW)'] / total_v * 100)
            if weight > 25:
                nudges.append({
                    "type": "Risk",
                    "title": "⚠️ 특정 종목 집중도 높음",
                    "content": f"{top_stock['종목명']}의 비중이 {weight:.1f}%입니다. 포트폴리오 안정성을 위해 일부 수익 실현 후 Core 자산(지수 ETF) 편입을 고려하세요."
                })

            # 전략 3: 수익률 기반 행동 및 상승 여력 분석
            high_earners = self.portfolio[self.portfolio['수익률(%)'] > 20]
            if not high_earners.empty:
                from skills.news_analyzer import get_analyst_ratings
                from skills.market_screener import MarketScreener
                
                screener = MarketScreener()
                for _, stock in high_earners.head(1).iterrows():
                    ticker = stock.get('티커코드', stock.get('종목코드', ''))
                    if ticker:
                        # 애널리스트 의견 가져오기 시도
                        ratings = get_analyst_ratings(ticker)
                        upside = ratings.get('upside_pct', 0) if (ratings and ratings.get('status') != 'error') else None
                        
                        # 판별 로직: upside가 5% 미만이거나, 데이터가 없는데 수익률이 너무 높을 때(과열)
                        should_sell = False
                        reason = ""
                        
                        if upside is not None:
                            if upside < 5 and stock['수익률(%)'] > 25:
                                should_sell = True
                                reason = f"애널리스트 목표가 대비 상승 여력이 {upside:.1f}%로 제한적입니다."
                        else:
                            # 데이터가 없는 경우 (ETF 등) 수익률 기준 30% 초과 시 경고
                            if stock['수익률(%)'] > 30:
                                should_sell = True
                                reason = f"단기 수익률 {stock['수익률(%)']:.1f}%로 기술적 과열 구간에 진입했습니다."

                        if should_sell:
                            # 실시간 스크리닝을 통해 대체 종목 발굴
                            top_momentum = screener.screen_momentum_stocks(top_n=5)
                            portfolio_tickers = self.portfolio['티커코드'].tolist() if '티커코드' in self.portfolio.columns else []
                            recommendations = [s['ticker'] for s in top_momentum if s['ticker'] not in portfolio_tickers][:2]
                            
                            rec_text = f"**{', '.join(recommendations)}**" if recommendations else "현금 대기(MMF)"
                            advice = f"익절 자금은 현재 모멘텀이 강력한 {rec_text} 종목으로의 교체 매수를 검토하세요."
                            
                            nudges.append({
                                "type": "Action",
                                "title": f"💰 {stock['종목명']} 익절 및 교체 추천",
                                "content": f"{reason} 일부 익절 후 {advice}"
                            })
                        elif upside is not None and upside > 15:
                            nudges.append({
                                "type": "Action",
                                "title": f"🚀 {stock['종목명']} 보유 지속 권장",
                                "content": f"수익률 {stock['수익률(%)']:.1f}%를 기록 중이나, **추가 상승 여력 {upside:.1f}%**가 남아있습니다. 추세가 꺾이기 전까지 홀딩을 추천합니다."
                            })

        # 3. 시장 상황 및 공포 지수
        vix = self.market.get('VIX', {}).get('value', 0)
        if vix > 25:
            nudges.append({
                "type": "Market",
                "title": "🌪️ 시장 변동성 확대",
                "content": "VIX 지수가 높습니다. 공격적인 매수보다는 보유 종목의 손절선(PSAR)을 점검하고 보수적으로 대응하세요."
            })

        # 4. 종합 요약 문구 개선
        if not nudges:
            if self.portfolio.empty:
                summary = "데이터 로딩 중이거나 포트폴리오가 비어 있습니다. '포트폴리오 관리'에서 데이터를 불러와 주세요."
            else:
                total_profit = self.portfolio['손익(KRW)'].sum() if '손익(KRW)' in self.portfolio.columns else 0
                avg_return = self.portfolio['수익률(%)'].mean() if '수익률(%)' in self.portfolio.columns else 0
                
                if total_profit < 0:
                    summary = f"현재 포트폴리오가 전체적으로 **₩{abs(total_profit)/1e4:.0f}만원 손실** 중입니다. 시장 반등을 기다리며 리스크 관리 위주로 대응이 필요합니다."
                elif avg_return < -5:
                    summary = "평균 수익률이 부진합니다. 종목 교체나 섹터 비중 조절을 검토할 시기입니다."
                else:
                    summary = "현재 포트폴리오는 표면적으로 안정적이나, 추가적인 알파 수익 창출을 위한 종목 발굴이 필요합니다."
        else:
            summary = f"오늘 마스터를 위해 {len(nudges)}개의 전략적 제안이 준비되었습니다. 특히 리스크 관리와 익절 전략에 주목하세요."

        return {
            "summary": summary,
            "nudges": nudges,
            "total_cash": total_cash,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
