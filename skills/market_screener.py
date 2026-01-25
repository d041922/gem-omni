"""
Market Screener - 실시간 종목 스크리닝 시스템
모멘텀, RSI, 거래량 기반으로 매수/매도 후보 종목 발굴
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta


class MarketScreener:
    """시장 전체를 스크리닝하여 투자 기회 발굴"""

    def __init__(self, cache_dir: str = "tmp/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "screener_results.json"
        self.cache_ttl = 300  # 5분

        # S&P 500 주요 종목 (Top 100)
        self.universe = self._get_stock_universe()

    def _get_stock_universe(self) -> List[str]:
        """스크리닝 대상 종목 리스트"""
        # S&P 500 시가총액 상위 100개 + 주요 성장주
        sp500_top = [
            # Mega Cap
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
            "UNH", "JNJ", "XOM", "V", "PG", "JPM", "MA", "HD", "CVX", "MRK",
            "ABBV", "KO", "PEP", "AVGO", "COST", "WMT", "LLY", "MCD", "TMO",

            # Tech & AI
            "AMD", "INTC", "CRM", "ORCL", "ADBE", "CSCO", "ACN", "TXN", "QCOM",
            "INTU", "IBM", "NOW", "AMAT", "LRCX", "KLAC", "SNPS", "CDNS", "ASML",

            # Semiconductors
            "TSM", "SMCI", "MRVL", "MU", "NXPI", "ADI", "ON",

            # Healthcare & Biotech
            "PFE", "ABT", "DHR", "BMY", "AMGN", "GILD", "VRTX", "REGN",
            "CRSP", "EDIT", "BEAM", "NTLA",

            # Energy & Renewables
            "ENPH", "FSLR", "NEE", "DUK", "SO", "D",

            # Consumer
            "AMZN", "NKE", "SBUX", "TGT", "LOW",

            # Financials
            "BAC", "WFC", "C", "GS", "MS", "BLK", "SCHW",

            # ETFs
            "SPY", "QQQ", "DIA", "IWM", "VTI", "VOO",
            "XLK", "XLV", "XLF", "XLE", "XLY", "XLP", "XLI", "XLB", "XLRE", "XLU", "XLC"
        ]

        return list(set(sp500_top))  # 중복 제거

    def _load_cache(self) -> Optional[Dict]:
        """캐시 파일 로드"""
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)

            # TTL 확인
            cached_time = datetime.fromisoformat(cache.get('timestamp', '2000-01-01'))
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cache

            return None
        except Exception as e:
            print(f"Cache load error: {e}")
            return None

    def _save_cache(self, data: Dict):
        """캐시 파일 저장"""
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Cache save error: {e}")

    def screen_momentum_stocks(
        self,
        rsi_min: float = 30,
        rsi_max: float = 70,
        volume_surge_min: float = 1.5,
        top_n: int = 20
    ) -> List[Dict]:
        """
        모멘텀 기반 종목 스크리닝

        Args:
            rsi_min: 최소 RSI (과매도 필터)
            rsi_max: 최대 RSI (과매수 필터)
            volume_surge_min: 평균 거래량 대비 배수 (1.5 = 150%)
            top_n: 상위 N개 종목

        Returns:
            [
                {
                    'ticker': 'NVDA',
                    'name': 'NVIDIA Corp',
                    'price': 780.50,
                    'change_pct': 2.3,
                    'rsi': 65.2,
                    'volume_surge': 2.3,  # 평균 대비 230%
                    'position_52w': 78.5,  # 52주 고점 대비 위치
                    'momentum_score': 8.5  # 0-10 스코어
                },
                ...
            ]
        """
        # 캐시 확인
        cache = self._load_cache()
        if cache and 'momentum' in cache:
            print("📦 Using cached momentum screening results")
            return cache['momentum'][:top_n]

        print(f"🔍 Screening {len(self.universe)} stocks for momentum...")

        results = []
        for ticker in self.universe:
            try:
                stock = yf.Ticker(ticker)

                # 가격 데이터 (3개월)
                hist = stock.history(period='3mo')
                if hist.empty or len(hist) < 20:
                    continue

                # 현재가 및 변동률
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_close) / prev_close) * 100

                # RSI 계산 (14일)
                rsi = self._calculate_rsi(hist['Close'], period=14)
                if rsi is None or rsi < rsi_min or rsi > rsi_max:
                    continue

                # 거래량 급증 확인
                avg_volume = hist['Volume'].iloc[:-1].mean()
                current_volume = hist['Volume'].iloc[-1]
                volume_surge = current_volume / avg_volume if avg_volume > 0 else 0

                if volume_surge < volume_surge_min:
                    continue

                # 52주 고점 대비 위치
                high_52w = hist['High'].max()
                low_52w = hist['Low'].min()
                position_52w = ((current_price - low_52w) / (high_52w - low_52w) * 100) if high_52w > low_52w else 50

                # 모멘텀 스코어 계산 (0-10)
                momentum_score = self._calculate_momentum_score(
                    rsi, volume_surge, position_52w, change_pct
                )

                # 종목 정보
                info = stock.info
                name = info.get('longName', info.get('shortName', ticker))

                results.append({
                    'ticker': ticker,
                    'name': name,
                    'price': float(current_price),
                    'change_pct': float(change_pct),
                    'rsi': float(rsi),
                    'volume_surge': float(volume_surge),
                    'position_52w': float(position_52w),
                    'momentum_score': float(momentum_score)
                })

            except Exception as e:
                # 개별 종목 오류 무시
                continue

        # 모멘텀 스코어 기준 정렬
        results.sort(key=lambda x: x['momentum_score'], reverse=True)
        top_results = results[:top_n]

        # 캐시 저장
        self._save_cache({'momentum': top_results})

        print(f"✅ Found {len(top_results)} momentum stocks")
        return top_results

    def screen_undervalued_stocks(
        self,
        max_pe: float = 20,
        max_pb: float = 3,
        min_market_cap: float = 10e9,  # 100억 달러
        top_n: int = 10
    ) -> List[Dict]:
        """
        저평가 종목 스크리닝 (가치 투자)

        Args:
            max_pe: 최대 PER
            max_pb: 최대 PBR
            min_market_cap: 최소 시가총액 (달러)
            top_n: 상위 N개 종목

        Returns:
            저평가 종목 리스트
        """
        # 캐시 확인
        cache = self._load_cache()
        if cache and 'undervalued' in cache:
            print("📦 Using cached undervalued screening results")
            return cache['undervalued'][:top_n]

        print(f"🔍 Screening for undervalued stocks...")

        results = []
        for ticker in self.universe:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                # 시가총액 필터
                market_cap = info.get('marketCap', 0)
                if market_cap < min_market_cap:
                    continue

                # PER, PBR 필터
                pe_ratio = info.get('forwardPE', info.get('trailingPE', 999))
                pb_ratio = info.get('priceToBook', 999)

                if pe_ratio > max_pe or pb_ratio > max_pb:
                    continue

                # 배당 수익률
                dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0

                # 가격 데이터
                hist = stock.history(period='1mo')
                if hist.empty:
                    continue

                current_price = hist['Close'].iloc[-1]
                change_1m = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

                results.append({
                    'ticker': ticker,
                    'name': info.get('longName', info.get('shortName', ticker)),
                    'price': float(current_price),
                    'pe_ratio': float(pe_ratio) if pe_ratio < 999 else None,
                    'pb_ratio': float(pb_ratio) if pb_ratio < 999 else None,
                    'dividend_yield': float(dividend_yield),
                    'market_cap_b': float(market_cap / 1e9),
                    'change_1m': float(change_1m),
                    'value_score': self._calculate_value_score(pe_ratio, pb_ratio, dividend_yield)
                })

            except Exception as e:
                continue

        # 가치 스코어 기준 정렬
        results.sort(key=lambda x: x['value_score'], reverse=True)
        top_results = results[:top_n]

        # 캐시 업데이트
        cache_data = cache if cache else {}
        cache_data['undervalued'] = top_results
        self._save_cache(cache_data)

        print(f"✅ Found {len(top_results)} undervalued stocks")
        return top_results

    def screen_breakout_candidates(self, top_n: int = 10) -> List[Dict]:
        """
        52주 고점 돌파 후보 스크리닝

        Returns:
            브레이크아웃 후보 종목 리스트
        """
        # 캐시 확인
        cache = self._load_cache()
        if cache and 'breakout' in cache:
            print("📦 Using cached breakout screening results")
            return cache['breakout'][:top_n]

        print(f"🔍 Screening for breakout candidates...")

        results = []
        for ticker in self.universe:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1y')

                if hist.empty or len(hist) < 100:
                    continue

                current_price = hist['Close'].iloc[-1]
                high_52w = hist['High'].max()

                # 52주 고점 대비 거리 (95% 이상)
                distance_from_high = (current_price / high_52w) * 100

                if distance_from_high < 95:
                    continue

                # 거래량 증가
                avg_volume_30d = hist['Volume'].iloc[-30:].mean()
                avg_volume_100d = hist['Volume'].iloc[:-30].mean()
                volume_increase = (avg_volume_30d / avg_volume_100d) if avg_volume_100d > 0 else 1

                # 추세 강도 (ADX 대용)
                change_3m = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-60]) / hist['Close'].iloc[-60]) * 100

                info = stock.info
                results.append({
                    'ticker': ticker,
                    'name': info.get('longName', info.get('shortName', ticker)),
                    'price': float(current_price),
                    'distance_from_high_pct': float(distance_from_high),
                    'volume_increase': float(volume_increase),
                    'change_3m': float(change_3m),
                    'breakout_score': float(distance_from_high + (volume_increase - 1) * 10)
                })

            except Exception as e:
                continue

        # 브레이크아웃 스코어 기준 정렬
        results.sort(key=lambda x: x['breakout_score'], reverse=True)
        top_results = results[:top_n]

        # 캐시 업데이트
        cache_data = cache if cache else {}
        cache_data['breakout'] = top_results
        self._save_cache(cache_data)

        print(f"✅ Found {len(top_results)} breakout candidates")
        return top_results

    def get_sector_leaders(self, sector: str = "Technology", top_n: int = 5) -> List[Dict]:
        """
        특정 섹터 내 상위 종목

        Args:
            sector: 섹터명 (Technology, Healthcare, Energy...)
            top_n: 상위 N개

        Returns:
            섹터 리더 종목 리스트
        """
        print(f"🔍 Finding leaders in {sector} sector...")

        results = []
        for ticker in self.universe:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                stock_sector = info.get('sector', '')
                if sector.lower() not in stock_sector.lower():
                    continue

                hist = stock.history(period='3mo')
                if hist.empty:
                    continue

                current_price = hist['Close'].iloc[-1]
                change_3m = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

                results.append({
                    'ticker': ticker,
                    'name': info.get('longName', ticker),
                    'price': float(current_price),
                    'change_3m': float(change_3m),
                    'market_cap_b': float(info.get('marketCap', 0) / 1e9)
                })

            except Exception as e:
                continue

        # 3개월 수익률 기준 정렬
        results.sort(key=lambda x: x['change_3m'], reverse=True)
        return results[:top_n]

    # ========== Helper Methods ==========

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """RSI 계산"""
        if len(prices) < period + 1:
            return None

        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1] if not rsi.empty else None

    def _calculate_momentum_score(
        self,
        rsi: float,
        volume_surge: float,
        position_52w: float,
        change_pct: float
    ) -> float:
        """
        모멘텀 스코어 계산 (0-10)

        요소:
        - RSI (40-60 최적)
        - 거래량 급증
        - 52주 위치
        - 최근 변동률
        """
        score = 0.0

        # RSI 점수 (40-60 최적, 3점)
        if 40 <= rsi <= 60:
            score += 3.0
        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            score += 2.0
        else:
            score += 1.0

        # 거래량 급증 점수 (3점)
        if volume_surge >= 3.0:
            score += 3.0
        elif volume_surge >= 2.0:
            score += 2.0
        elif volume_surge >= 1.5:
            score += 1.0

        # 52주 위치 점수 (2점)
        if position_52w >= 70:
            score += 2.0
        elif position_52w >= 50:
            score += 1.0

        # 최근 변동률 점수 (2점)
        if change_pct >= 5:
            score += 2.0
        elif change_pct >= 2:
            score += 1.0
        elif change_pct >= 0:
            score += 0.5

        return min(score, 10.0)

    def _calculate_value_score(
        self,
        pe_ratio: float,
        pb_ratio: float,
        dividend_yield: float
    ) -> float:
        """
        가치 스코어 계산 (0-10)

        낮은 PER, 낮은 PBR, 높은 배당수익률 선호
        """
        score = 0.0

        # PER 점수 (4점)
        if pe_ratio < 999:
            if pe_ratio < 10:
                score += 4.0
            elif pe_ratio < 15:
                score += 3.0
            elif pe_ratio < 20:
                score += 2.0
            else:
                score += 1.0

        # PBR 점수 (3점)
        if pb_ratio < 999:
            if pb_ratio < 1.5:
                score += 3.0
            elif pb_ratio < 2.5:
                score += 2.0
            elif pb_ratio < 3.0:
                score += 1.0

        # 배당 수익률 점수 (3점)
        if dividend_yield >= 4:
            score += 3.0
        elif dividend_yield >= 2:
            score += 2.0
        elif dividend_yield >= 1:
            score += 1.0

        return min(score, 10.0)


# ========== Standalone Functions ==========

def screen_momentum_stocks(**kwargs) -> List[Dict]:
    """편의 함수: 모멘텀 종목 스크리닝"""
    screener = MarketScreener()
    return screener.screen_momentum_stocks(**kwargs)


def screen_undervalued_stocks(**kwargs) -> List[Dict]:
    """편의 함수: 저평가 종목 스크리닝"""
    screener = MarketScreener()
    return screener.screen_undervalued_stocks(**kwargs)


def screen_breakout_candidates(**kwargs) -> List[Dict]:
    """편의 함수: 브레이크아웃 후보 스크리닝"""
    screener = MarketScreener()
    return screener.screen_breakout_candidates(**kwargs)


# ========== CLI Test ==========

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Market Screener Test")
    print("=" * 60)

    screener = MarketScreener()

    # Test 1: Momentum Stocks
    print("\n1️⃣ Momentum Stocks (RSI 30-70, Volume 1.5x+)")
    print("-" * 60)
    momentum = screener.screen_momentum_stocks(top_n=10)
    for i, stock in enumerate(momentum, 1):
        print(f"{i}. {stock['ticker']:6s} {stock['name'][:30]:30s} "
              f"${stock['price']:7.2f} | RSI {stock['rsi']:5.1f} | "
              f"Vol {stock['volume_surge']:4.1f}x | Score {stock['momentum_score']:.1f}")

    # Test 2: Undervalued Stocks
    print("\n2️⃣ Undervalued Stocks (PER < 20, PBR < 3)")
    print("-" * 60)
    undervalued = screener.screen_undervalued_stocks(top_n=5)
    for i, stock in enumerate(undervalued, 1):
        print(f"{i}. {stock['ticker']:6s} {stock['name'][:30]:30s} "
              f"${stock['price']:7.2f} | PER {stock['pe_ratio']:5.1f} | "
              f"PBR {stock['pb_ratio']:4.2f} | Score {stock['value_score']:.1f}")

    # Test 3: Breakout Candidates
    print("\n3️⃣ Breakout Candidates (52W High 95%+)")
    print("-" * 60)
    breakout = screener.screen_breakout_candidates(top_n=5)
    for i, stock in enumerate(breakout, 1):
        print(f"{i}. {stock['ticker']:6s} {stock['name'][:30]:30s} "
              f"${stock['price']:7.2f} | Distance {stock['distance_from_high_pct']:5.1f}% | "
              f"3M {stock['change_3m']:+6.1f}%")

    print("\n" + "=" * 60)
    print("✅ Test completed!")
