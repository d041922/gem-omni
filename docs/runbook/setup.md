# Setup Runbook

## 1. Python Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
.\scripts\dev_tasks.ps1 bootstrap
```

Alternative (if `make` is available):
```powershell
make bootstrap
```

## 2. Environment Variables
- Copy `.env.example` to `.env`
- Choose one setup tier:
- Minimal (UI + local checks): no external API keys required for `make check/test/smoke`.
- Live integrations: set `EXA_API_KEY`, `TAVILY_API_KEY`, and one of `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
- Add provider-specific keys only for features you use (see `.env.example`).

## 3. Baseline Checks
```powershell
make check
make test
make smoke
```
Optional UI baseline:
```powershell
streamlit run app.py
```

## 4. CI Parity
- Local gates must match CI gates: `make check`, `make test`, `make smoke`.
- If local passes but CI fails, treat CI as source of truth and sync local environment/gates.

## 5. Common Issues
- If Korean console encoding breaks emoji output, use:
```powershell
$env:PYTHONUTF8='1'
```
- If `pytest` warns on `.pytest_cache` permission, tests can still run. Fix directory permissions separately.
