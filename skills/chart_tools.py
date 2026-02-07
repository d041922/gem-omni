"""
OMNI Chart Engine (v1.1)
Advanced Plotly Visualizations & Technical Interpreter
"""
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any

class ChartEngine:
    """
    기술적 지표(Bollinger, Pivot, MA)가 오버레이된 전문가용 차트 생성기.
    """

    def get_bollinger_bands(self, df: pd.DataFrame) -> Dict[str, float]:
        """최종 볼린저 밴드 상/하단 수치 반환"""
        if len(df) < 20:
            return {"upper": 0, "lower": 0}
        sma20 = df['Close'].rolling(window=20).mean()
        std20 = df['Close'].rolling(window=20).std()
        return {
            "upper": round(float(sma20.iloc[-1] + (std20.iloc[-1] * 2)), 2),
            "lower": round(float(sma20.iloc[-1] - (std20.iloc[-1] * 2)), 2)
        }

    def create_technical_chart(self, ticker: str, df: pd.DataFrame, pivots: Dict[str, float]) -> go.Figure:
        """
        캔들스틱 + 볼린저 밴드 + Pivot Lines + 거래량을 포함한 복합 차트 생성.
        """
        fig = go.Figure()

        # 1. Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="Price"
        ))

        # 2. Bollinger Bands
        sma20 = df['Close'].rolling(window=20).mean()
        std20 = df['Close'].rolling(window=20).std()
        upper = sma20 + (std20 * 2)
        lower = sma20 - (std20 * 2)

        fig.add_trace(go.Scatter(
            x=df.index, y=upper, name="Bollinger Upper",
            line=dict(color='rgba(255, 255, 255, 0.3)', width=1),
            legendgroup="Bollinger"
        ))
        fig.add_trace(go.Scatter(
            x=df.index, y=lower, name="Bollinger Lower",
            line=dict(color='rgba(255, 255, 255, 0.3)', width=1),
            fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)',
            legendgroup="Bollinger"
        ))

        # 3. Pivot Lines (Horizontal)
        if pivots:
            last_date = df.index[-1]
            first_date = df.index[0]
            
            fig.add_shape(type="line", x0=first_date, x1=last_date, y0=pivots['R1'], y1=pivots['R1'],
                          line=dict(color="#FF4B4B", width=1, dash="dash"), name="R1")
            fig.add_annotation(x=last_date, y=pivots['R1'], text="R1", showarrow=False, xanchor="left", font=dict(color="#FF4B4B"))

            fig.add_shape(type="line", x0=first_date, x1=last_date, y0=pivots['S1'], y1=pivots['S1'],
                          line=dict(color="#3182F6", width=1, dash="dash"), name="S1")
            fig.add_annotation(x=last_date, y=pivots['S1'], text="S1", showarrow=False, xanchor="left", font=dict(color="#3182F6"))

        # Layout
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#E6EDF3"),
            height=600,
            margin=dict(t=40, b=20, l=20, r=20),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        return fig

class ChartInterpreter:
    """
    수치형 기술 지표를 인간이 이해할 수 있는 전략적 조언으로 변환.
    """

    def interpret_trend(self, ribbon: Dict[str, str]) -> Dict[str, str]:
        """MA Ribbon 상태를 기반으로 추세 진단"""
        bullish_count = sum(1 for v in ribbon.values() if v == "Bullish")
        
        if bullish_count == 6:
            return {"title": "🟢 초강력 상승 추세 (Strong Bull)", "description": "모든 이평선이 정배열 상태입니다. 조정 시 매수 관점이 유효합니다."}
        elif bullish_count >= 4:
            return {"title": "📈 상승 추세 우위 (Bullish Bias)", "description": "대부분의 이평선이 지지해주고 있습니다. 상승 흐름에 편승하십시오."}
        elif bullish_count <= 1:
            return {"title": "🔴 하락 추세 지속 (Strong Bear)", "description": "역배열 상태가 심화되고 있습니다. 섣불리 바닥을 예단하지 마십시오."}
        else:
            return {"title": "⚪ 혼조세 (Neutral)", "description": "방향성이 뚜렷하지 않습니다. 박스권 매매 전략이 유리합니다."}

    def interpret_momentum(self, tech_data: Dict[str, Any]) -> Dict[str, str]:
        """볼린저 밴드 및 RSI 기반 모멘텀 진단"""
        price = tech_data.get("current_price", 0)
        upper = tech_data.get("bollinger", {}).get("upper", 999999)
        lower = tech_data.get("bollinger", {}).get("lower", 0)
        rsi = tech_data.get("rsi", 50)
        
        if price >= upper:
            return {"title": "⚠️ 과매수 경고 (Overbought)", "description": "볼린저 밴드 상단을 돌파했습니다. 단기 차익 실현 매물이 출회될 수 있습니다."}
        elif price <= lower:
            return {"title": "📉 과매도 구간 (Oversold)", "description": "볼린저 하단을 이탈했습니다. 기술적 반등이 임박했을 수 있습니다."}
        elif rsi >= 70:
            return {"title": "🔥 과열권 진입", "description": "RSI 70 이상입니다. 추격 매수는 자제하고 보유 물량을 관리하십시오."}
        elif rsi <= 30:
            return {"title": "❄️ 침체권 진입", "description": "RSI 30 이하입니다. 바닥 다지기를 확인한 후 분할 매수를 고려하십시오."}
        else:
            return {"title": "⚖️ 균형 상태", "description": "과열도 침체도 아닙니다. 추세 추종 전략을 유지하십시오."}