"""
SEC Edgar API 통합 - 미국 기업 실적 자료 수집 및 요약
토큰 최적화: 원본 50k 토큰 → 요약 500 토큰 (99% 절감)
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import requests
from google import genai


class SECEdgar:
    """SEC Edgar 공시 자료 수집 및 AI 요약"""

    def __init__(self, cache_dir: str = "tmp/research"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # SEC Edgar API
        self.sec_base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'GEM-OMNI research@example.com',  # SEC requires User-Agent
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }

        # Gemini client
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            self.gemini_client = genai.Client(api_key=api_key)
        else:
            self.gemini_client = None
            print("⚠️ GOOGLE_API_KEY not found. AI summarization disabled.")

    def fetch_latest_filings(
        self,
        ticker: str,
        form_types: list = None
    ) -> Dict:
        """
        최신 SEC 공시 자료 가져오기

        Args:
            ticker: 종목 티커 (예: NVDA, AAPL)
            form_types: 공시 유형 리스트 (기본: ['10-K', '10-Q', '8-K'])

        Returns:
            {
                'ticker': 'NVDA',
                'filings': [
                    {
                        'form_type': '10-K',
                        'filing_date': '2024-01-15',
                        'accession_number': '0001045810-24-000004',
                        'summary': {  # ⭐ AI 요약 (500 토큰)
                            'revenue': '$22.1B (+126% YoY)',
                            'net_income': '$12.3B (+581% YoY)',
                            'key_highlights': [
                                '데이터센터 매출 $47.5B (+217% YoY)',
                                'AI 칩 수요 지속 강세, 공급 부족',
                                '2025 Q1 가이던스: $24B (컨센서스 $22B 상회)'
                            ],
                            'risks': [
                                '공급망 제약으로 단기 매출 제한',
                                '경쟁 심화 (AMD, Intel 추격)'
                            ]
                        },
                        'full_text_path': 'tmp/research/NVDA/10K_2024.txt',  # 원본 (AI에 안 넣음!)
                        'summary_tokens': 487  # 토큰 사용량
                    },
                    ...
                ]
            }
        """
        if form_types is None:
            form_types = ['10-K', '10-Q', '8-K']

        # 1. CIK 번호 조회 (SEC 내부 식별자)
        cik = self._get_cik(ticker)
        if not cik:
            return {'error': f'Ticker {ticker} not found in SEC database'}

        # 2. 최근 공시 목록 조회
        filings_data = self._fetch_recent_filings(cik, form_types)

        if not filings_data:
            return {'error': 'No filings found'}

        # 3. 각 공시별로 처리
        processed_filings = []
        for filing in filings_data[:3]:  # 최근 3개만
            try:
                # 3-1. 전체 텍스트 다운로드
                full_text = self._download_filing_text(filing['url'])

                if not full_text:
                    continue

                # 3-2. 로컬 저장 (원본)
                ticker_dir = self.cache_dir / ticker
                ticker_dir.mkdir(parents=True, exist_ok=True)

                form_type = filing['form_type'].replace('-', '')
                date_str = filing['filing_date'].replace('-', '')
                full_text_path = ticker_dir / f"{form_type}_{date_str}.txt"

                with open(full_text_path, 'w', encoding='utf-8') as f:
                    f.write(full_text)

                # 3-3. AI 요약 (핵심!)
                summary = self._summarize_filing(full_text, filing['form_type'])

                # 3-4. 결과 구성
                processed_filings.append({
                    'form_type': filing['form_type'],
                    'filing_date': filing['filing_date'],
                    'accession_number': filing['accession_number'],
                    'summary': summary,
                    'full_text_path': str(full_text_path),
                    'summary_tokens': self._estimate_tokens(str(summary))
                })

            except Exception as e:
                print(f"Error processing {filing['form_type']}: {e}")
                continue

        # 4. 캐시 저장
        cache_file = ticker_dir / "filings_summary.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'ticker': ticker,
                'update_time': datetime.now().isoformat(),
                'filings': processed_filings
            }, f, indent=2, ensure_ascii=False)

        return {
            'ticker': ticker,
            'filings': processed_filings,
            'cache_file': str(cache_file)
        }

    def _get_cik(self, ticker: str) -> Optional[str]:
        """티커로 CIK 번호 조회"""
        try:
            # SEC ticker-CIK 매핑 파일
            url = f"{self.sec_base_url}/files/company_tickers.json"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # 티커로 검색
                for company in data.values():
                    if company['ticker'].upper() == ticker.upper():
                        # CIK를 10자리로 패딩
                        return str(company['cik_str']).zfill(10)

            return None

        except Exception as e:
            print(f"CIK lookup error: {e}")
            return None

    def _fetch_recent_filings(self, cik: str, form_types: list) -> list:
        """최근 공시 목록 조회"""
        try:
            # SEC submissions API
            url = f"{self.sec_base_url}/cgi-bin/browse-edgar"
            params = {
                'action': 'getcompany',
                'CIK': cik,
                'type': '',
                'dateb': '',
                'owner': 'exclude',
                'output': 'atom',
                'count': 100
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            # Parse XML (간단한 파싱)
            filings = []
            lines = response.text.split('\n')

            current_filing = {}
            for line in lines:
                if '<filing-type>' in line:
                    form_type = line.split('>')[1].split('<')[0].strip()
                    if form_type in form_types:
                        current_filing['form_type'] = form_type

                elif '<filing-date>' in line and 'form_type' in current_filing:
                    filing_date = line.split('>')[1].split('<')[0].strip()
                    current_filing['filing_date'] = filing_date

                elif '<accession-number>' in line and 'form_type' in current_filing:
                    accession = line.split('>')[1].split('<')[0].strip()
                    current_filing['accession_number'] = accession

                    # URL 구성
                    accession_clean = accession.replace('-', '')
                    current_filing['url'] = (
                        f"{self.sec_base_url}/cgi-bin/viewer?"
                        f"action=view&cik={cik}&accession_number={accession}&xbrl_type=v"
                    )

                    filings.append(current_filing.copy())
                    current_filing = {}

                    if len(filings) >= 5:
                        break

            return filings

        except Exception as e:
            print(f"Filings fetch error: {e}")
            return []

    def _download_filing_text(self, url: str) -> Optional[str]:
        """공시 원문 다운로드"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)

            if response.status_code == 200:
                # HTML 태그 제거 (간단한 처리)
                text = response.text
                text = text.replace('<', ' <').replace('>', '> ')
                text = ' '.join([word for word in text.split() if not word.startswith('<')])

                return text[:100000]  # 100k 글자 제한 (토큰 약 25k)

            return None

        except Exception as e:
            print(f"Download error: {e}")
            return None

    def _summarize_filing(self, full_text: str, form_type: str) -> Dict:
        """
        ⭐ 핵심 기능: AI로 공시 요약 (500 토큰 이내)

        원본 50,000 토큰 → 요약 500 토큰 (99% 절감)
        """
        if not self.gemini_client:
            return {'error': 'Gemini API not configured'}

        try:
            # 프롬프트 구성
            if form_type == '10-K':
                instruction = """
다음 10-K 연간 보고서를 **500단어 이내**로 요약하세요.

필수 포함 항목 (JSON 형식):
{
    "revenue": "매출액과 전년 대비 증감율",
    "net_income": "순이익과 전년 대비 증감율",
    "key_highlights": ["핵심 성과 3가지"],
    "guidance_2025": "2025년 전망 (있다면)",
    "risks": ["주요 리스크 2가지"]
}

⚠️ 중요: 숫자는 정확히, 불필요한 설명 제외, JSON만 반환
"""
            elif form_type == '10-Q':
                instruction = """
다음 10-Q 분기 보고서를 **300단어 이내**로 요약하세요.

필수 포함 항목 (JSON 형식):
{
    "revenue": "분기 매출액과 전년 대비 증감율",
    "net_income": "분기 순이익과 전년 대비 증감율",
    "key_highlights": ["핵심 성과 2가지"],
    "outlook": "다음 분기 전망 (있다면)"
}
"""
            else:  # 8-K
                instruction = """
다음 8-K 특별 공시를 **200단어 이내**로 요약하세요.

필수 포함 항목 (JSON 형식):
{
    "event_type": "공시 사유",
    "key_points": ["핵심 내용 2-3가지"],
    "impact": "주가 영향 (긍정/중립/부정)"
}
"""

            # Gemini 호출 (처음 20k 토큰만 사용)
            truncated_text = full_text[:80000]  # 글자 제한 (약 20k 토큰)

            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",  # 빠르고 저렴한 모델
                contents=f"{instruction}\n\n{truncated_text}"
            )

            # JSON 파싱
            summary_text = response.text.strip()

            # JSON 추출 (markdown 코드 블록 제거)
            if '```json' in summary_text:
                summary_text = summary_text.split('```json')[1].split('```')[0].strip()
            elif '```' in summary_text:
                summary_text = summary_text.split('```')[1].split('```')[0].strip()

            summary = json.loads(summary_text)

            return summary

        except Exception as e:
            print(f"Summarization error: {e}")
            # Fallback: 간단한 요약
            return {
                'error': str(e),
                'raw_text_preview': full_text[:500]
            }

    def _estimate_tokens(self, text: str) -> int:
        """토큰 수 추정 (1 토큰 ≈ 4 글자)"""
        return len(text) // 4

    def load_summary(self, ticker: str) -> Optional[Dict]:
        """캐시된 요약 로드"""
        cache_file = self.cache_dir / ticker / "filings_summary.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # TTL 확인 (7일)
            update_time = datetime.fromisoformat(data['update_time'])
            if (datetime.now() - update_time).days > 7:
                return None

            return data

        except Exception as e:
            print(f"Cache load error: {e}")
            return None


# ========== Standalone Functions ==========

def fetch_latest_filings(ticker: str, form_types: list = None) -> Dict:
    """편의 함수: SEC 공시 가져오기"""
    edgar = SECEdgar()
    return edgar.fetch_latest_filings(ticker, form_types)


def load_summary(ticker: str) -> Optional[Dict]:
    """편의 함수: 캐시된 요약 로드"""
    edgar = SECEdgar()
    return edgar.load_summary(ticker)


# ========== CLI Test ==========

if __name__ == "__main__":
    print("=" * 80)
    print("📄 SEC Edgar API Test")
    print("=" * 80)

    ticker = "NVDA"  # Test with NVIDIA

    print(f"\n🔍 Fetching latest filings for {ticker}...")
    print("-" * 80)

    edgar = SECEdgar()

    # Test 1: Fetch latest 10-K
    result = edgar.fetch_latest_filings(ticker, form_types=['10-K'])

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"\n✅ Found {len(result['filings'])} filings:")

        for filing in result['filings']:
            print(f"\n📑 {filing['form_type']} - {filing['filing_date']}")
            print(f"   Accession: {filing['accession_number']}")
            print(f"   Summary Tokens: {filing['summary_tokens']}")

            if 'summary' in filing and 'revenue' in filing['summary']:
                summary = filing['summary']
                print(f"\n   📊 Summary:")
                print(f"   - Revenue: {summary.get('revenue', 'N/A')}")
                print(f"   - Net Income: {summary.get('net_income', 'N/A')}")

                if 'key_highlights' in summary:
                    print(f"   - Highlights:")
                    for i, highlight in enumerate(summary['key_highlights'][:3], 1):
                        print(f"     {i}. {highlight}")

            print(f"   📁 Full Text: {filing['full_text_path']}")

    print("\n" + "=" * 80)
    print("✅ Test completed!")
    print(f"⚠️ Note: If Gemini API is not configured, summaries will be empty.")
    print(f"   Set GOOGLE_API_KEY environment variable to enable AI summarization.")
