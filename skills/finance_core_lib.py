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