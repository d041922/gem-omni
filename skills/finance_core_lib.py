import pandas as pd
import numpy as np

def safe_float(val):
    """안전하게 float으로 변환"""
    if pd.isna(val) or val == '' or val == 'nan' or val == 'None':
        return 0.0
    try:
        # 문자열인 경우 콤마, % 제거
        if isinstance(val, str):
            clean_val = val.replace(',', '').replace('%', '').strip()
            if not clean_val: return 0.0
            return float(clean_val)
        return float(val)
    except:
        return 0.0

def calculate_portfolio_metrics(df: pd.DataFrame, current_prices: dict, usd_krw_rate: float) -> pd.DataFrame:
    """
    포트폴리오 데이터프레임을 받아 평가액, 손익, 수익률을 정밀 계산하여 반환합니다.
    """
    if df.empty:
        return df

    res = df.copy()
    
    # 1. 필수 컬럼 및 숫자형 변환 (전처리)
    numeric_cols = ['수량', '평균 단가(USD)', '평균 단가(KRW)', '수동 현재가(KRW)', '수동 수익률(%)']
    for col in numeric_cols:
        if col not in res.columns:
            res[col] = 0.0
        else:
            res[col] = res[col].apply(safe_float)

    # 2. 통화 설정
    if '통화' not in res.columns:
        res['통화'] = 'USD' # 기본값
        if '종목코드' in res.columns:
            # .KS, .KQ가 포함되어 있거나, 종목코드가 없는 경우(부동산 등)는 KRW로 간주할 수도 있음
            # 여기서는 종목코드에 .KS/.KQ가 있거나, '평균 단가(KRW)'가 있고 '평균 단가(USD)'가 없으면 KRW로 판단
            res.loc[res['종목코드'].astype(str).str.contains('.KS|.KQ', na=False), '통화'] = 'KRW'
            
            # 추가 로직: KRW 단가는 있는데 USD 단가가 0이면 KRW로 강제
            mask_krw_only = (res['평균 단가(KRW)'] > 0) & (res['평균 단가(USD)'] == 0)
            res.loc[mask_krw_only, '통화'] = 'KRW'

    # 3. 매수금액(Total Cost) 계산
    def calc_cost(row):
        qty = row['수량']
        if row['통화'] == 'KRW':
            # KRW 단가가 있으면 우선 사용
            price = row['평균 단가(KRW)'] if row['평균 단가(KRW)'] > 0 else row['평균 단가(USD)'] * usd_krw_rate
            return price * qty
        else: # USD
            # USD 단가가 있으면 우선 사용
            price = row['평균 단가(USD)'] if row['평균 단가(USD)'] > 0 else row['평균 단가(KRW)'] / usd_krw_rate
            return price * qty * usd_krw_rate # 결과는 항상 KRW 환산액

    res['매수금액(KRW)'] = res.apply(calc_cost, axis=1)

    # 4. 평가금액(Evaluation) 계산
    # API 현재가 매핑
    res['API현재가'] = res['종목코드'].map(current_prices).fillna(0)

    def calc_eval(row):
        cost = row['매수금액(KRW)']
        qty = row['수량']
        
        # Priority 1: 수동 수익률 (%)
        if row['수동 수익률(%)'] != 0:
            rate = row['수동 수익률(%)']
            # 퍼센트 단위(예: 6.62)라고 가정하고 100으로 나눔
            # 단, 이미 소수점(0.06)으로 들어왔을 가능성에 대비해, 절대값이 0.5 미만이면 그대로 씀
            # (마스터 요청: 200% 수익률도 있으므로 단순 크기 비교 위험 -> 컬럼명에 %가 있으므로 무조건 나누기?
            #  아까 합의한 대로 '컬럼명에 %가 있으니 100으로 나눈다' 원칙 적용)
            return cost * (1 + rate / 100)
            
        # Priority 2: 수동 현재가 (KRW)
        if row['수동 현재가(KRW)'] > 0:
            return row['수동 현재가(KRW)'] * qty
            
        # Priority 3: API 현재가
        if row['API현재가'] > 0:
            price = row['API현재가']
            if row['통화'] == 'USD':
                price = price * usd_krw_rate
            return price * qty
            
        # Priority 4: 데이터 없음 -> 평가액 = 매수금액 (수익률 0%)
        return cost

    res['평가금액(KRW)'] = res.apply(calc_eval, axis=1)
    
    # 5. 최종 지표 계산
    res['손익(KRW)'] = res['평가금액(KRW)'] - res['매수금액(KRW)']
    
    # 수익률 계산 (매수금액 0인 경우 방어)
    res['수익률(%)'] = res.apply(lambda x: (x['손익(KRW)'] / x['매수금액(KRW)'] * 100) if x['매수금액(KRW)'] > 0 else 0.0, axis=1)
    
    # 6. 역산된 현재가 (UI 표시용)
    def calc_implied_price(row):
        if row['수량'] <= 0: return 0.0
        # 원화 기준 1주당 가치
        price_krw = row['평가금액(KRW)'] / row['수량']
        
        if row['통화'] == 'USD':
            return price_krw / usd_krw_rate
        return price_krw

    res['최종현재가'] = res.apply(calc_implied_price, axis=1)

    return res


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.03) -> float:
    """
    샤프 지수(Sharpe Ratio) 계산

    Args:
        returns: 수익률 시계열 (예: 일별 수익률)
        risk_free_rate: 무위험 수익률 (연율, 기본값 3%)

    Returns:
        Sharpe Ratio (높을수록 위험 대비 수익이 좋음)
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0

    # 연율화된 수익률과 변동성
    mean_return = returns.mean() * 252  # 연간 거래일 252일 가정
    std_return = returns.std() * np.sqrt(252)

    sharpe = (mean_return - risk_free_rate) / std_return
    return sharpe


def calculate_portfolio_beta(portfolio_returns: pd.Series, market_returns: pd.Series) -> float:
    """
    포트폴리오 베타(Beta) 계산

    Args:
        portfolio_returns: 포트폴리오 수익률 시계열
        market_returns: 시장(벤치마크) 수익률 시계열

    Returns:
        Beta (1.0: 시장과 동일, >1.0: 시장보다 변동성 큼, <1.0: 시장보다 안정적)
    """
    if len(portfolio_returns) < 2 or len(market_returns) < 2:
        return 1.0  # 기본값

    # 공분산 / 시장 분산
    covariance = np.cov(portfolio_returns, market_returns)[0, 1]
    market_variance = np.var(market_returns)

    if market_variance == 0:
        return 1.0

    beta = covariance / market_variance
    return beta


def calculate_correlation_matrix(df: pd.DataFrame, price_history: dict) -> pd.DataFrame:
    """
    포트폴리오 종목 간 상관계수 행렬 계산

    Args:
        df: 포트폴리오 데이터프레임
        price_history: {ticker: pd.Series} 형태의 가격 히스토리

    Returns:
        상관계수 행렬 DataFrame
    """
    if df.empty or not price_history:
        return pd.DataFrame()

    # 수익률 계산
    returns_dict = {}
    for ticker, prices in price_history.items():
        if len(prices) > 1:
            returns = prices.pct_change().dropna()
            returns_dict[ticker] = returns

    if not returns_dict:
        return pd.DataFrame()

    # 데이터프레임으로 변환 후 상관계수 계산
    returns_df = pd.DataFrame(returns_dict)
    correlation_matrix = returns_df.corr()

    return correlation_matrix


def calculate_portfolio_risk_metrics(df: pd.DataFrame, risk_free_rate: float = 0.03) -> dict:
    """
    포트폴리오 종합 리스크 지표 계산

    Args:
        df: calculate_portfolio_metrics로 계산된 포트폴리오 데이터
        risk_free_rate: 무위험 수익률 (연율)

    Returns:
        리스크 지표 딕셔너리 {
            'total_return': 전체 수익률,
            'volatility': 변동성,
            'sharpe_ratio': 샤프 지수,
            'max_position_pct': 최대 종목 비중,
            'concentration_risk': 집중도 리스크 (상위 3종목 비중)
        }
    """
    if df.empty:
        return {}

    total_value = df['평가금액(KRW)'].sum()
    total_cost = df['매수금액(KRW)'].sum()

    # 전체 수익률
    total_return = (total_value - total_cost) / total_cost if total_cost > 0 else 0.0

    # 종목별 비중
    df['비중(%)'] = (df['평가금액(KRW)'] / total_value * 100) if total_value > 0 else 0

    # 집중도 리스크 (상위 3종목)
    top3_weight = df.nlargest(3, '평가금액(KRW)')['비중(%)'].sum()

    # 변동성 (종목별 수익률의 가중 표준편차 근사)
    returns = df['수익률(%)'].values
    weights = df['비중(%)'].values / 100
    portfolio_volatility = np.sqrt(np.sum((weights * returns) ** 2))

    return {
        'total_return': total_return * 100,  # 퍼센트
        'volatility': portfolio_volatility,
        'sharpe_ratio': total_return / (portfolio_volatility / 100) if portfolio_volatility > 0 else 0,
        'max_position_pct': df['비중(%)'].max(),
        'concentration_risk': top3_weight,
        'num_positions': len(df)
    }