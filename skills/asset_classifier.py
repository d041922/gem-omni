"""
Core-Satellite Asset Classifier
Unified asset classification logic with strategy support

Key Logic:
  - QQQ, SPY 같은 지수 ETF → Core (100+ 종목 분산)
  - SMH, SOXX 같은 섹터 ETF → Satellite (특정 섹터 집중)
  - 분류 우선순위: 지수 ETF 티커 > 섹터 ETF 티커 > 카테고리 > 종목명

Usage:
    from skills.asset_classifier import AssetClassifier

    classifier = AssetClassifier(strategy='balanced')
    asset_type = classifier.classify('QQQ', '기술 ETF', 'NASDAQ 100')
    # Returns: 'Core' (지수 ETF이므로)
"""

from typing import Dict, Tuple, Literal

StrategyType = Literal['aggressive', 'balanced', 'defensive']


class AssetClassifier:
    """
    Core-Satellite 자산 분류 클래스

    3가지 투자 전략 지원:
    - aggressive: Core 40-50%, Satellite 50-60% (공격적 성장, 7-10년 목표)
    - balanced: Core 50-60%, Satellite 40-50% (균형적 성장)
    - defensive: Core 60-70%, Satellite 30-40% (자본 보전 우선)
    """

    STRATEGIES = {
        'aggressive': {
            'name': '공격적 전략',
            'core_target': (40, 50),        # Core 40-50%
            'satellite_target': (50, 60),   # Satellite 50-60%
            'default_class': 'Satellite',
            'description': '7-10년 내 경제적 자유 목표. Satellite로 초과 수익 추구.'
        },
        'balanced': {
            'name': '균형 전략',
            'core_target': (50, 60),        # Core 50-60%
            'satellite_target': (40, 50),   # Satellite 40-50%
            'default_class': 'Satellite',
            'description': '안정성과 성장의 균형. Core로 방어, Satellite로 공격.'
        },
        'defensive': {
            'name': '방어적 전략',
            'core_target': (60, 70),        # Core 60-70%
            'satellite_target': (30, 40),   # Satellite 30-40%
            'default_class': 'Core',
            'description': '자본 보전 우선. 안정적 복리 성장 지향.'
        }
    }

    # 1순위: 지수 ETF (광범위한 시장 추종) → 무조건 Core
    # QQQ는 기술주 위주지만 NASDAQ 100 '전체'를 추종하므로 Core
    CORE_INDEX_ETFS = {
        # S&P 500 ETFs (500개 종목)
        'SPY', 'VOO', 'VTI', 'IVV', 'SPLG',
        # NASDAQ 100 ETFs (100개 종목, 기술주 지수지만 Core)
        'QQQ', 'QQQM', 'QQQJ',
        # Dow Jones
        'DIA',
        # Russell 2000 (소형주)
        'IWM', 'VTWO',
        # 배당 ETFs (광범위한 배당주)
        'VIG', 'SCHD', 'VYM', 'DVY', 'DGRO', 'NOBL',
        # 채권 ETFs
        'AGG', 'BND', 'TLT', 'IEF', 'SHY',
        # 국제 ETFs
        'VEA', 'VWO', 'EFA', 'IEMG'
    }

    # 2순위: 섹터/테마 ETF (특정 섹터 집중) → Satellite
    # SMH, SOXX는 반도체만 집중하므로 Satellite
    SATELLITE_SECTOR_ETFS = {
        # 반도체 섹터
        'SMH', 'SOXX', 'PSI',
        # 기술 섹터
        'XLK', 'VGT', 'FTEC',
        # 바이오/헬스케어 섹터
        'XBI', 'IBB', 'XLV',
        # 로봇/자동화
        'BOTZ', 'ROBO', 'ARKQ',
        # Ark Innovation (테마 집중)
        'ARKK', 'ARKW', 'ARKG', 'ARKF',
        # 클린에너지/신재생
        'ICLN', 'TAN', 'FAN',
        # 기타 섹터
        'XLE', 'XLF', 'XLY', 'XLP', 'XLI', 'XLU', 'XLB', 'XLRE'
    }

    # 3순위: 대형 배당 성장주 티커 → Core
    CORE_LARGE_CAP_STOCKS = {
        # FAANG + Big Tech (시총 상위)
        'MSFT', 'AAPL', 'GOOGL', 'GOOG', 'AMZN', 'META',
        # 배당 귀족/왕
        'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE',
        'V', 'MA', 'DIS', 'UNH', 'CVX', 'XOM'
    }

    # 4순위: 개별 성장주/고위험 티커 → Satellite
    SATELLITE_GROWTH_STOCKS = {
        # AI/반도체 개별주
        'NVDA', 'AMD', 'TSM', 'ASML', 'SMCI', 'AVGO', 'QCOM', 'INTC', 'MU',
        # 바이오/헬스케어 (첨단 치료)
        'CRSP', 'EDIT', 'BEAM', 'NTLA', 'VRTX', 'MRNA', 'BNTX', 'REGN',
        # 성장주
        'PLTR', 'TSLA', 'SNOW', 'DDOG', 'NET', 'CRWD', 'ZS',
        # 한국 성장주
        '005930', '000660', '035720', '035420', '207940', '373220',
        '005930.KS', '000660.KS', '035720.KS', '035420.KS', '207940.KS', '373220.KS'
    }

    # 카테고리 키워드 (낮은 우선순위)
    CORE_CATEGORIES = [
        'index', 'sp500', 's&p500', 'nasdaq100', 'nasdaq 100',
        '배당', 'dividend', '인덱스', 'core', '채권', 'bond',
        '미국 대형주', 'large-cap', 'blue chip', 'value',
        '대형 배당', '안정', 'stable', '광범위'
    ]

    SATELLITE_CATEGORIES = [
        'ai', '반도체', 'semiconductor', 'chip', 'chipset',
        '바이오', 'biotech', 'healthcare', 'gene editing', 'mrna',
        '성장주', 'growth', 'high growth', 'aggressive',
        '한국', 'korea', 'kospi', 'k-',
        'satellite', '섹터', 'sector',
        '로봇', 'robotics', 'automation',
        '전력', 'energy', 'renewable', '신재생', 'solar', 'wind',
        '2차전지', 'battery', '전기차', 'ev'
    ]

    def __init__(self, strategy: StrategyType = 'balanced'):
        """
        Args:
            strategy: 'aggressive', 'balanced', 'defensive'
        """
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Invalid strategy: {strategy}. Choose from {list(self.STRATEGIES.keys())}")

        self.strategy_name = strategy
        self.strategy = self.STRATEGIES[strategy]

    def classify(self, ticker: str, category: str, name: str) -> Literal['Core', 'Satellite']:
        """
        자산을 Core 또는 Satellite로 분류

        우선순위:
        1. 지수 ETF 티커 매칭 (QQQ, SPY 등) → Core
        2. 섹터 ETF 티커 매칭 (SMH, SOXX 등) → Satellite
        3. 대형 배당주 티커 매칭 → Core
        4. 개별 성장주 티커 매칭 → Satellite
        5. 카테고리 키워드 매칭
        6. 종목명 패턴 매칭
        7. 기본값 (전략에 따라)

        Args:
            ticker: 종목 티커 (예: 'QQQ', 'NVDA', '005930.KS')
            category: 자산 카테고리 (예: '기술 ETF', 'AI/반도체')
            name: 종목명 (예: 'NASDAQ 100', '엔비디아')

        Returns:
            'Core' 또는 'Satellite'
        """
        # Normalize inputs
        ticker_upper = str(ticker).upper().strip()
        category_lower = str(category).lower().strip()
        name_lower = str(name).lower().strip()

        # 1순위: 지수 ETF 체크 (최우선)
        # QQQ, SPY 등은 무조건 Core
        if ticker_upper in self.CORE_INDEX_ETFS:
            return 'Core'

        # 2순위: 섹터 ETF 체크
        # SMH, SOXX 등은 Satellite
        if ticker_upper in self.SATELLITE_SECTOR_ETFS:
            return 'Satellite'

        # 3순위: 대형 배당주 체크
        if ticker_upper in self.CORE_LARGE_CAP_STOCKS:
            return 'Core'

        # 4순위: 개별 성장주 체크
        if ticker_upper in self.SATELLITE_GROWTH_STOCKS:
            return 'Satellite'

        # 5순위: 카테고리 키워드 매칭
        # 단, "ETF" + "index" 조합은 Core 우선
        has_etf = 'etf' in category_lower or 'etf' in name_lower
        has_index = any(word in category_lower for word in ['index', 'sp500', 's&p500', 'nasdaq100', '인덱스'])

        if has_etf and has_index:
            return 'Core'

        for keyword in self.CORE_CATEGORIES:
            if keyword in category_lower:
                return 'Core'

        for keyword in self.SATELLITE_CATEGORIES:
            if keyword in category_lower:
                return 'Satellite'

        # 6순위: 종목명 패턴 분석
        core_name_patterns = ['s&p', 'nasdaq 100', 'index', 'dividend', '배당', '인덱스']
        if any(pattern in name_lower for pattern in core_name_patterns):
            return 'Core'

        satellite_name_patterns = ['ai', 'semiconductor', 'biotech', 'genomics', 'robotics', '반도체', '바이오']
        if any(pattern in name_lower for pattern in satellite_name_patterns):
            return 'Satellite'

        # 7순위: 기본값 (전략에 따라)
        return self.strategy['default_class']

    def get_rebalancing_target(self, current_core_pct: float) -> Dict[str, any]:
        """
        현재 Core 비중에 따른 리밸런싱 목표 제시

        Args:
            current_core_pct: 현재 Core 자산 비중 (0-100)

        Returns:
            {
                'action': 'increase_core' | 'decrease_core' | 'maintain',
                'status': 'low' | 'high' | 'balanced',
                'target_pct': float,
                'adjustment_needed': float,
                'message': str
            }
        """
        target_min, target_max = self.strategy['core_target']
        current_satellite_pct = 100 - current_core_pct

        if current_core_pct < target_min:
            return {
                'action': 'increase_core',
                'status': 'low',
                'target_pct': target_min,
                'adjustment_needed': target_min - current_core_pct,
                'message': f"⚠️ Core 비중 {current_core_pct:.1f}% (목표: {target_min}-{target_max}%) → {target_min - current_core_pct:.1f}%p 증액 필요"
            }
        elif current_core_pct > target_max:
            return {
                'action': 'decrease_core',
                'status': 'high',
                'target_pct': target_max,
                'adjustment_needed': current_core_pct - target_max,
                'message': f"⚠️ Core 비중 {current_core_pct:.1f}% (목표: {target_min}-{target_max}%) → Satellite 기회 물색"
            }
        else:
            return {
                'action': 'maintain',
                'status': 'balanced',
                'target_pct': current_core_pct,
                'adjustment_needed': 0,
                'message': f"✅ Core {current_core_pct:.1f}%, Satellite {current_satellite_pct:.1f}% - 균형 유지"
            }

    def get_strategy_info(self) -> Dict[str, any]:
        """현재 전략 정보 반환"""
        return {
            'strategy': self.strategy_name,
            'name': self.strategy['name'],
            'core_target': self.strategy['core_target'],
            'satellite_target': self.strategy['satellite_target'],
            'description': self.strategy['description']
        }

    def calculate_allocation(self, holdings: list) -> Dict[str, any]:
        """
        보유 종목 리스트를 분석하여 Core/Satellite 비중 계산

        Args:
            holdings: [
                {'ticker': 'QQQ', 'category': '기술 ETF', 'name': 'NASDAQ 100', 'value': 50000000},
                ...
            ]

        Returns:
            {
                'core_value': float,
                'satellite_value': float,
                'total_value': float,
                'core_pct': float,
                'satellite_pct': float,
                'rebalancing': Dict,
                'holdings_classified': list
            }
        """
        core_value = 0
        satellite_value = 0
        holdings_classified = []

        for holding in holdings:
            ticker = holding.get('ticker', '')
            category = holding.get('category', '')
            name = holding.get('name', '')
            value = holding.get('value', 0)

            asset_type = self.classify(ticker, category, name)

            holding_info = holding.copy()
            holding_info['asset_type'] = asset_type
            holdings_classified.append(holding_info)

            if asset_type == 'Core':
                core_value += value
            else:
                satellite_value += value

        total_value = core_value + satellite_value

        if total_value == 0:
            return {
                'core_value': 0,
                'satellite_value': 0,
                'total_value': 0,
                'core_pct': 0,
                'satellite_pct': 0,
                'rebalancing': {'action': 'maintain', 'message': '보유 자산 없음'},
                'holdings_classified': []
            }

        core_pct = (core_value / total_value * 100)
        satellite_pct = (satellite_value / total_value * 100)
        rebalancing = self.get_rebalancing_target(core_pct)

        return {
            'core_value': core_value,
            'satellite_value': satellite_value,
            'total_value': total_value,
            'core_pct': core_pct,
            'satellite_pct': satellite_pct,
            'rebalancing': rebalancing,
            'holdings_classified': holdings_classified
        }


def classify_asset(
    ticker: str,
    category: str,
    name: str,
    strategy: StrategyType = 'balanced'
) -> Literal['Core', 'Satellite']:
    """
    Quick asset classification without creating classifier instance

    Example:
        >>> classify_asset('QQQ', '기술 ETF', 'NASDAQ 100')
        'Core'
        >>> classify_asset('NVDA', 'AI/반도체', '엔비디아')
        'Satellite'
    """
    classifier = AssetClassifier(strategy=strategy)
    return classifier.classify(ticker, category, name)


if __name__ == '__main__':
    # Test cases
    classifier = AssetClassifier(strategy='balanced')

    test_assets = [
        ('QQQ', '기술 ETF', 'NASDAQ 100 ETF'),
        ('SPY', 'ETF', 'S&P 500 ETF'),
        ('SMH', '반도체 ETF', 'VanEck Semiconductor ETF'),
        ('NVDA', 'AI/반도체', '엔비디아'),
        ('AAPL', '미국 대형주', '애플'),
        ('CRSP', '바이오', 'CRISPR Therapeutics'),
        ('005930.KS', '한국 성장주', '삼성전자'),
    ]

    print("=== Asset Classification Test ===")
    for ticker, category, name in test_assets:
        asset_type = classifier.classify(ticker, category, name)
        print(f"{name:30s} ({ticker:15s}) → {asset_type}")

    print("\n✅ Expected: QQQ → Core (지수 ETF)")
    print("✅ Expected: SMH → Satellite (섹터 ETF)")
