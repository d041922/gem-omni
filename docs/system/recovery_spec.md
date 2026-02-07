# Recovery Spec: Data Integrity & Metadata Robustness

## 1. 개요 (Overview)
본 문서는 OMNI 시스템에서 발생한 **데이터 누락(Account/Tier)** 및 **페칭 실패(ETF 가격)** 문제를 해결하기 위한 복구 설계를 정의한다.

## 2. Robust Column Normalization (유연한 컬럼 매핑)
구글 시트의 컬럼명 다양성에 대응하기 위해, 모든 컬럼을 정규화하여 매핑한다.

- **Normalization Algorithm**: 
    1. 모든 컬럼명에서 양끝 공백 제거 (`strip()`).
    2. 소문자 변환 (`lower()`).
    3. 핵심 키워드 포함 여부로 판단.
- **Mapping Table**:
    - `ticker`: ['종목코드', '티커', 'symbol', 'ticker']
    - `account`: ['계좌', 'account']
    - `tier`: ['카테고리', '구분', 'tier', 'category']
    - `quantity`: ['수량', 'quantity', 'qty']

## 3. Triple-Shield Price Fetching (3중 가격 방어선)
특정 종목의 가격이 0으로 표시되는 현상을 방지한다.

| Level | Method | Target | Reason |
|:---:|:---|:---|:---|
| **L1** | `yf.download` | Batch (All) | 가장 빠름 (1회 호출) |
| **L2** | `yf.fast_info` | Individual (Missing) | 개별 종목의 지연된 데이터 확보 |
| **L3** | `KR Crawler` | Individual (KR Stocks) | 한국 ETF 및 주가 최종 보루 |

## 4. Metadata Preservation (메타데이터 보존)
- 모든 `holding` 객체는 `tier`, `account`, `name`을 필수 필드로 가진다.
- 값이 누락된 경우 `Unknown`이 아닌, `Default (Unclassified)` 등으로 가독성을 높인다.

## 5. Test Verification (검증 전략)
- **Recovery-UT-01**: 다양한 컬럼명의 시트를 주입했을 때 정규화된 데이터가 추출되는지 확인.
- **Recovery-UT-02**: `yfinance`가 실패하는 티커를 강제로 주입하여 크롤러로 성공하는지 확인.
