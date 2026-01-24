import pandas as pd
import os
import glob
from typing import List, Dict

def load_assets_from_excel(assets_dir: str = "assets") -> List[Dict]:
    """
    finance_core.py의 검증된 로직을 이식하여 엑셀 자산을 로드합니다.
    - 문자열 전처리 및 to_numeric을 통한 안전한 숫자 변환
    - USD/KRW 자동 구분
    """
    all_assets = []
    files = glob.glob(os.path.join(assets_dir, "*.xlsx")) + \
            glob.glob(os.path.join(assets_dir, "*.xls")) + \
            glob.glob(os.path.join(assets_dir, "*.csv"))
    
    for file_path in files:
        try:
            # 1. 파일 읽기
            if file_path.endswith('.xls'):
                df = pd.read_excel(file_path, engine='xlrd')
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # 컬럼명 공백 제거
            df.columns = [str(c).strip() for c in df.columns]
            
            # 2. 핵심 컬럼 찾기 (finance_core.py 스타일)
            # 종목명
            name_col = next((c for c in df.columns if any(x in str(c) for x in ['종목', '상품', 'Name'])), None)
            if not name_col: continue

            # 수량
            qty_col = next((c for c in df.columns if any(x in str(c).upper() for x in ['수량', 'QTY'])), None)
            if not qty_col: continue

            # 단가 (USD, KRW 구분)
            price_usd_col = next((c for c in df.columns if 'USD' in str(c).upper() and '단가' in str(c)), None)
            price_krw_col = next((c for c in df.columns if 'KRW' in str(c).upper() and '단가' in str(c)), None)
            # 일반 단가 (화폐 단위 명시 없는 경우)
            price_gen_col = next((c for c in df.columns if '단가' in str(c) and 'USD' not in str(c) and 'KRW' not in str(c)), None)

            # 3. 데이터 전처리 (finance_core.py 로직 적용)
            # 모든 데이터를 일단 문자열로 변환 후 콤마 제거
            for col in [qty_col, price_usd_col, price_krw_col, price_gen_col]:
                if col:
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # 4. 데이터 추출
            for _, row in df.iterrows():
                name = str(row[name_col])
                if name in ['nan', 'None', '', '합계']:
                    continue
                
                amount = float(row[qty_col])
                if amount <= 0:
                    continue

                avg_price = 0.0
                currency = "KRW"

                # USD 우선 확인
                if price_usd_col and row[price_usd_col] > 0:
                    avg_price = float(row[price_usd_col])
                    currency = "USD"
                # 없으면 KRW 확인
                elif price_krw_col and row[price_krw_col] > 0:
                    avg_price = float(row[price_krw_col])
                    currency = "KRW"
                # 그것도 없으면 일반 단가 (KRW 가정)
                elif price_gen_col and row[price_gen_col] > 0:
                    avg_price = float(row[price_gen_col])
                    currency = "KRW"

                # 현재가(평가액) 계산을 위해 임시로 평단가 사용 (추후 API로 업데이트됨)
                current_price = avg_price

                all_assets.append({
                    "name": name,
                    "ticker": name, # 일단 이름으로 설정
                    "amount": amount,
                    "avg_price": avg_price,
                    "current_price": current_price,
                    "currency": currency,
                    "source": os.path.basename(file_path)
                })

        except Exception as e:
            print(f"[ExcelLoader] Error reading {file_path}: {e}")
            
    return all_assets
