# GEM OMNI - 프로젝트 구조 분석 및 정리 계획

**분석 일시**: 2026-01-25 12:35 KST

---

## 현재 구조 문제점

### 1. 루트 디렉토리 과부하
**문제**: 루트에 22개 파일이 산재되어 있음

```
루트 디렉토리 (22개 파일):
├── app.py                              (메인 앱)
├── pages_stock_analysis.py             (Streamlit 페이지)
├── test_*.py (7개)                     (테스트 파일들)
├── *.md (9개)                          (문서 파일들)
├── check_env_fix.py                    (유틸리티)
├── debug_portfolio.py                  (디버그 스크립트)
├── list_models.py                      (유틸리티)
└── verify_kis_english.py               (검증 스크립트)
```

### 2. 문서 파일 분산
```
현재 위치:
루트/               - 9개 .md 파일
docs/              - 3개 .md 파일
ref/               - 3개 .md 파일
core/              - 1개 RULES.md
```

### 3. 테스트 파일 미정리
```
루트에 산재:
- test_context_optimization.py
- test_finance_crew.py
- test_full_optimization.py
- test_kis_sync.py
- test_search.py
- test_token_optimization.py
- test_tools_integration.py
```

### 4. Streamlit 페이지 위치 오류
```
현재: pages_stock_analysis.py (루트)
표준: pages/stock_analysis.py (pages/ 폴더 내)
```

### 5. 유틸리티 스크립트 미분류
```
- check_env_fix.py
- debug_portfolio.py
- list_models.py
- verify_kis_english.py
```

---

## 정리 계획

### 목표 구조
```
GEM_OMNI/
├── app.py                          (메인 앱 - 루트 유지)
├── README.md                       (프로젝트 설명 - 루트 유지)
├── .claude/                        (AI 프롬프트)
│   ├── agents/
│   └── prompts/
├── agents/                         (CrewAI 에이전트)
│   ├── crewai_agents/
│   ├── crews/
│   ├── tools/
│   └── templates/
├── core/                           (핵심 시스템)
│   ├── base.py
│   ├── memory.py
│   └── models.py
├── skills/                         (재사용 가능 라이브러리)
│   ├── finance_core_lib.py
│   ├── stock_analyzer.py
│   └── ...
├── pages/                          (Streamlit 페이지) ← 신규!
│   └── stock_analysis.py
├── tests/                          (테스트 파일들) ← 신규!
│   ├── test_context_optimization.py
│   ├── test_finance_crew.py
│   └── ...
├── scripts/                        (유틸리티 스크립트) ← 신규!
│   ├── check_env_fix.py
│   ├── debug_portfolio.py
│   └── ...
├── docs/                           (프로젝트 문서)
│   ├── guides/                     ← 신규 서브폴더!
│   │   ├── ARCHITECTURE.md
│   │   ├── CREWAI_GUIDE.md
│   │   └── DOMAIN_EXPANSION_GUIDE.md
│   ├── reports/                    ← 신규 서브폴더!
│   │   ├── FINAL_OPTIMIZATION_REPORT.md
│   │   ├── OPTIMIZATION_REPORT.md
│   │   ├── TEST_RESULTS.md
│   │   ├── CLEANUP_REPORT.md
│   │   ├── FIXES_APPLIED.md
│   │   ├── IMPROVEMENTS_v2.md
│   │   └── STOCK_ANALYSIS_FEATURE.md
│   └── reference/                  ← ref/ 폴더 이름 변경!
│       ├── Claude CLI 기반 자산 관리 에이전트 설계.md
│       ├── Claude Code 기반 지능형 자산 관리 시스템 통합 가이드.md
│       └── ref_finance_core.py
├── rules/                          (코딩 규칙)
├── memory/                         (메모리 데이터)
├── tmp/                            (임시 파일)
└── venv/                           (가상환경)
```

---

## 정리 작업 단계

### Phase 1: 폴더 생성
```bash
mkdir -p pages
mkdir -p tests
mkdir -p scripts
mkdir -p docs/guides
mkdir -p docs/reports
```

### Phase 2: Streamlit 페이지 이동
```bash
mv pages_stock_analysis.py pages/stock_analysis.py
```
**주의**: app.py에서 import 경로 수정 필요!

### Phase 3: 테스트 파일 이동
```bash
mv test_*.py tests/
```

### Phase 4: 유틸리티 스크립트 이동
```bash
mv check_env_fix.py scripts/
mv debug_portfolio.py scripts/
mv list_models.py scripts/
mv verify_kis_english.py scripts/
```

### Phase 5: 문서 정리
```bash
# 가이드 문서
mv docs/ARCHITECTURE.md docs/guides/
mv docs/CREWAI_GUIDE.md docs/guides/
mv docs/DOMAIN_EXPANSION_GUIDE.md docs/guides/

# 리포트 문서
mv FINAL_OPTIMIZATION_REPORT.md docs/reports/
mv OPTIMIZATION_REPORT.md docs/reports/
mv TEST_RESULTS.md docs/reports/
mv CLEANUP_REPORT.md docs/reports/
mv FIXES_APPLIED.md docs/reports/
mv IMPROVEMENTS_v2.md docs/reports/
mv STOCK_ANALYSIS_FEATURE.md docs/reports/

# 레퍼런스 이름 변경
mv ref docs/reference
```

### Phase 6: 루트에 남을 파일
```
GEM_OMNI/
├── app.py                          (메인 앱)
├── README.md                       (추가 생성 필요)
├── CLAUDE.md                       (프로젝트 설명서 - 유지)
├── GEMINI.md                       (API 설정 - 유지)
└── requirements.txt                (의존성 - 확인 필요)
```

---

## 장점

### 1. 가독성 향상
- 루트 디렉토리가 깔끔해짐 (22개 → 5개 파일)
- 파일 찾기 쉬워짐

### 2. Streamlit 표준 준수
```
pages/
└── stock_analysis.py

→ Streamlit이 자동으로 멀티페이지로 인식
```

### 3. 테스트 관리 용이
```
tests/
├── test_context_optimization.py
├── test_finance_crew.py
└── ...

→ pytest 실행 시 자동 인식
```

### 4. 문서 체계화
```
docs/
├── guides/         (사용 가이드)
├── reports/        (분석 리포트)
└── reference/      (참고 자료)
```

### 5. CI/CD 준비
```
tests/              → pytest 실행
scripts/            → 배포 스크립트 추가 가능
docs/               → 자동 문서 생성 가능
```

---

## 주의사항

### 1. Import 경로 수정
```python
# app.py
# Before
from pages_stock_analysis import render_stock_analysis_page

# After
from pages.stock_analysis import render_stock_analysis_page
```

### 2. Streamlit 멀티페이지 자동 인식
```
pages/ 폴더가 있으면 Streamlit이 자동으로 멀티페이지 앱으로 인식
→ 사이드바에 자동으로 페이지 링크 생성
→ 기존 radio 버튼 네비게이션과 충돌 가능

해결책:
1. 수동 네비게이션 유지 (현재 방식)
2. Streamlit 자동 멀티페이지 사용 (권장)
```

### 3. Git 이력 유지
```bash
# mv 대신 git mv 사용
git mv pages_stock_analysis.py pages/stock_analysis.py
```

### 4. 상대 경로 확인
```python
# 파일 이동 후 상대 경로 확인 필요
# 예: .claude/prompts/ 접근 시
Path(__file__).parent.parent / ".claude" / "prompts"
```

---

## 예상 효과

### Before (현재)
```
$ ls
app.py  check_env_fix.py  CLAUDE.md  CLEANUP_REPORT.md  ...
(22개 파일이 한 화면에 안 보임)
```

### After (정리 후)
```
$ ls
app.py  CLAUDE.md  GEMINI.md  README.md  requirements.txt

$ ls -l
agents/     core/      pages/     skills/    tests/
docs/       rules/     scripts/   tmp/       venv/
```

---

## 실행 여부 확인

**정리 작업을 진행할까요?**

### 옵션 1: 전체 정리 (권장)
- Phase 1-6 모두 실행
- 프로젝트 구조 완전히 재정비
- 예상 시간: 5분

### 옵션 2: 단계별 정리
- Phase 1: 폴더 생성만
- Phase 2-3: 핵심 파일만 이동
- Phase 4-5: 나중에 정리

### 옵션 3: 유지
- 현재 구조 유지
- 문서만 정리

**어떤 옵션을 선택하시겠습니까?**

---

## 롤백 계획

만약 문제가 생기면:
```bash
# 1. Git 커밋 전이면
git checkout .

# 2. Git 커밋 후면
git revert HEAD

# 3. 백업 복원
cp -r GEM_OMNI.backup/* GEM_OMNI/
```

---

**분석 완료**: 2026-01-25 12:35 KST
