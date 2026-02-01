# GEM: OMNI - Streamlit 배포 가이드

## 📋 목차
1. [로컬 테스트](#1-로컬-테스트)
2. [Streamlit Cloud 배포](#2-streamlit-cloud-배포)
3. [배포 전 체크리스트](#3-배포-전-체크리스트)
4. [환경 변수 설정](#4-환경-변수-설정)
5. [트러블슈팅](#5-트러블슈팅)

---

## 1. 로컬 테스트

### 1.1 가상환경 활성화
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 1.2 로컬 실행
```bash
streamlit run app.py
```

기본 포트: `http://localhost:8501`

### 1.3 포트 변경 (선택)
```bash
streamlit run app.py --server.port 8080
```

---

## 2. Streamlit Cloud 배포

### 2.1 사전 준비
1. **GitHub 저장소 생성**
   - 프로젝트를 GitHub에 푸시
   - Private 저장소 권장 (API 키 보안)

2. **필수 파일 확인**
   ```
   GEM_OMNI/
   ├── app.py              # 메인 앱
   ├── requirements.txt    # 의존성 (필수!)
   ├── .streamlit/         # 설정 (선택)
   │   └── config.toml
   └── .gitignore          # API 키 제외
   ```

3. **`.gitignore` 설정 (중요!)**
   ```
   .env
   *.env
   __pycache__/
   *.pyc
   .venv/
   venv/
   tmp/
   *.log
   credentials.json
   token.json
   ```

### 2.2 Streamlit Cloud 배포 단계

#### Step 1: Streamlit Cloud 가입
- https://streamlit.io/cloud 접속
- GitHub 계정으로 로그인

#### Step 2: 새 앱 배포
1. "New app" 클릭
2. 저장소 선택: `rogicx_dev/GEM_OMNI`
3. Branch: `master` (또는 `main`)
4. Main file path: `app.py`
5. App URL (선택): `gem-omni-portfolio` (커스텀 URL)

#### Step 3: Advanced settings 클릭
- Python version: `3.11` (권장)
- Secrets 설정 (다음 섹션 참고)

#### Step 4: Deploy 클릭
- 배포 시작 (2-5분 소요)
- 실시간 로그 확인 가능

---

## 3. 배포 전 체크리스트

### 3.1 코드 점검
- [ ] `app.py`에 하드코딩된 비밀키 없음
- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] `requirements.txt` 최신 상태
- [ ] Google Sheets API 인증 설정 확인

### 3.2 성능 최적화
- [ ] `@st.cache_data` 데코레이터 사용 (시장 데이터 로딩)
- [ ] 대용량 데이터는 `tmp/cache/` 저장 (토큰 최적화)
- [ ] 불필요한 API 호출 제거

### 3.3 UI/UX
- [ ] 모바일 반응형 확인
- [ ] 로딩 스피너 표시 (`st.spinner`)
- [ ] 에러 메시지 명확성 (`st.error`)

---

## 4. 환경 변수 설정

### 4.1 Streamlit Cloud Secrets 설정

#### 접근 방법
1. Streamlit Cloud 대시보드 → 앱 선택
2. Settings → Secrets 클릭

#### Secrets 형식 (TOML)
```toml
# Google API Key (Gemini)
GOOGLE_API_KEY = "AIzaSy..."

# Google Sheets Credentials (JSON 형식)
[gcp_service_account]
type = "service_account"
project_id = "gem-finance-..."
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\nMII...\n-----END PRIVATE KEY-----\n"
client_email = "gem-service@gem-finance.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."

# Optional: KIS API (향후)
# KIS_APP_KEY = "..."
# KIS_APP_SECRET = "..."
```

#### 주의 사항
- **private_key**: `\n` 개행 문자 유지 필수
- JSON → TOML 변환 시 따옴표 주의
- 저장 후 앱 자동 재시작

### 4.2 로컬 환경 변수 (.env)
```env
GOOGLE_API_KEY=AIzaSy...
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
```

### 4.3 코드에서 Secrets 접근
```python
import streamlit as st
import os

# Streamlit Cloud
if hasattr(st, 'secrets'):
    api_key = st.secrets["GOOGLE_API_KEY"]

    # Google Sheets credentials
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        # gspread 인증에 사용
else:
    # 로컬 환경
    api_key = os.getenv("GOOGLE_API_KEY")
```

---

## 5. 트러블슈팅

### 5.1 일반적인 오류

#### 오류 1: `ModuleNotFoundError`
```
ModuleNotFoundError: No module named 'crewai'
```
**해결책**:
- `requirements.txt`에 누락된 패키지 추가
- Streamlit Cloud에서 앱 재배포 (Reboot)

#### 오류 2: Google Sheets 인증 실패
```
gspread.exceptions.APIError: PERMISSION_DENIED
```
**해결책**:
1. Google Cloud Console → IAM에서 서비스 계정 확인
2. Google Sheets에 서비스 계정 이메일 공유 (편집자 권한)
3. Google Sheets API 활성화 확인

#### 오류 3: Gemini API 할당량 초과
```
google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded
```
**해결책**:
- Google AI Studio에서 API 할당량 확인
- 무료 tier: 분당 15회 제한
- 필요시 캐싱 강화 (`tmp/cache/`)

#### 오류 4: 메모리 초과 (Streamlit Cloud)
```
Your app has gone over the allotted memory limit
```
**해결책**:
- 무료 tier: 1GB RAM 제한
- 대용량 데이터프레임 최적화
- `st.cache_data` 사용 최소화
- 필요시 유료 플랜 업그레이드 ($20/월)

### 5.2 성능 최적화

#### 캐싱 전략
```python
# 5분마다 시장 데이터 갱신
@st.cache_data(ttl=300)
def fetch_market_data():
    # ...

# 세션당 1회만 포트폴리오 로드
@st.cache_data
def load_portfolio():
    # ...
```

#### 토큰 절감 (Gemini API)
- 포트폴리오 데이터 → JSON 파일 저장 (`tmp/cache/`)
- AI 분석 시 요약 통계만 전달 (< 500 토큰)
- 전체 데이터 반환 금지 (CLAUDE.md 참고)

### 5.3 배포 후 모니터링

#### Streamlit Cloud 로그 확인
1. 앱 대시보드 → "Manage app"
2. "Logs" 탭 클릭
3. 실시간 로그 스트림 확인

#### 로그 레벨 설정
```toml
# .streamlit/config.toml
[logger]
level = "info"  # debug, info, warning, error
```

---

## 6. 고급 설정

### 6.1 커스텀 도메인 연결 (유료)
Streamlit Cloud Pro ($20/월) 이상에서 가능:
1. Settings → Custom subdomain
2. DNS CNAME 레코드 추가: `portfolio.yourdomain.com` → `your-app.streamlit.app`

### 6.2 비밀번호 보호
```python
# app.py 상단에 추가
import streamlit as st

def check_password():
    """Simple password protection"""
    def password_entered():
        if st.session_state["password"] == st.secrets.get("app_password", ""):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password",
                      on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password",
                      on_change=password_entered, key="password")
        st.error("Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# 이후 메인 앱 코드...
```

### 6.3 Analytics 추가 (선택)
```python
# Google Analytics 예시
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
""", unsafe_allow_html=True)
```

---

## 7. 배포 워크플로우 (권장)

### 개발 → 배포 프로세스
```bash
# 1. 로컬 개발
git checkout -b feature/new-chart
# 코드 수정...

# 2. 로컬 테스트
streamlit run app.py

# 3. 커밋 & 푸시
git add .
git commit -m "Feat: Add new chart"
git push origin feature/new-chart

# 4. GitHub Pull Request 생성
# 코드 리뷰 후 master로 머지

# 5. Streamlit Cloud 자동 배포
# (master 브랜치 변경 감지 시 자동)
```

### CI/CD with GitHub Actions (선택)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/  # 테스트 실행
```

---

## 8. 참고 자료

### 공식 문서
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Google Sheets API Python](https://developers.google.com/sheets/api/quickstart/python)

### 커뮤니티
- [Streamlit Forum](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

---

## 9. 요금 정보 (2026년 기준)

### Streamlit Cloud Tier

| Tier | 가격 | 리소스 | 특징 |
|------|------|--------|------|
| Community (무료) | $0 | 1GB RAM, 1 CPU | Public apps, 3개 앱 제한 |
| Team | $42/월 | 2GB RAM, 2 CPU | Private apps, 무제한 |
| Enterprise | 문의 | 커스텀 | SSO, 전용 지원 |

### Gemini API (Google AI)

| Tier | RPM | TPM | 가격 |
|------|-----|-----|------|
| 무료 | 15 | 32,000 | $0 |
| Pay-as-you-go | 1,000 | 4M | $0.35 / 1M tokens |

---

## 10. Quick Start 명령어 모음

```bash
# 로컬 실행
streamlit run app.py

# 캐시 삭제
streamlit cache clear

# 설정 확인
streamlit config show

# 버전 확인
streamlit --version

# 개발 모드 (hot reload)
streamlit run app.py --server.runOnSave true
```

---

**마지막 업데이트**: 2026-01-25
**작성자**: GEM: OMNI 팀
**문의**: GitHub Issues
