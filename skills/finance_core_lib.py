import pandas as pd

def safe_float(val):
    if pd.isna(val) or val in ['', 'nan', 'None']:
        return 0.0
    try:
        if isinstance(val, str):
            v = val.replace(',', '').replace('%', '').strip()
            return float(v) if v else 0.0
        return float(val)
    except Exception:
         return 0.0

def calculate_portfolio_metrics(df: pd.DataFrame, prices: dict, rate: float) -> pd.DataFrame:
    if df.empty:
        return df
    res = df.copy()
    for col in ['수량', '평균 단가(USD)', '평균 단가(KRW)', '수동 현재가(KRW)', '수동 수익률(%)']:
        if col in res.columns:
            res[col] = res.get(col).apply(safe_float)
        else:
            res[col] = 0.0

    res['통화'] = res.get('통화', pd.Series(['USD']*len(res)))
    res['API현재가'] = res.get('종목코드', pd.Series()).map(prices).fillna(0.0)

    def calc_cost(row):
        qty = float(row.get('수량', 0.0))
        if row.get('통화') == 'KRW':
            p = float(row.get('평균 단가(KRW)', 0.0))
            if p <= 0:
                p = float(row.get('평균 단가(USD)', 0.0)) * rate
            return p * qty
        p_u = float(row.get('평균 단가(USD)', 0.0))
        if p_u <= 0:
            p_u = float(row.get('평균 단가(KRW)', 0.0)) / rate
        return p_u * qty * rate

    res['매수금액(KRW)'] = res.apply(calc_cost, axis=1)
    
    def calc_eval(row):
        cost = float(row.get('매수금액(KRW)', 0.0))
        qty = float(row.get('수량', 0.0))
        if row.get('수동 수익률(%)', 0.0) != 0:
            return cost * (1 + float(row.get('수동 수익률(%)')) / 100)
        if row.get('수동 현재가(KRW)', 0.0) > 0:
            return float(row.get('수동 현재가(KRW)')) * qty
        p = float(row.get('API현재가', 0.0))
        if p > 0:
            return (p * rate if row.get('통화') == 'USD' else p) * qty
        return cost

    res['평가금액(KRW)'] = res.apply(calc_eval, axis=1)
    res['손익(KRW)'] = res['평가금액(KRW)'] - res.get('매수금액(KRW)', 0.0)
    res['수익률(%)'] = res.apply(lambda x: (x['손익(KRW)']/x['매수금액(KRW)']*100) if x.get('매수금액(KRW)', 0.0)>0 else 0.0, axis=1)
    return res