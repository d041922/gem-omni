# GEM_OMNI

Finance-focused agent workspace with Streamlit UI, orchestrated data flow, and AI-assisted analysis.

## Active Entry Points
- App: `app.py`
- Core orchestrator: `skills/data_orchestrator.py`
- Main integrations: `skills/gsheet_loader.py`, `skills/news_manager.py`, `agents/tools/search_tool.py`

## Development Standard (Codex-first)
- Rules: `AI_RULES.md`
- Change design: `SPEC.md`
- Architecture decision records: `docs/adr/`
- Runbooks: `docs/runbook/`

## Environment
- Single source of truth: `.env`
- Template: `.env.example`
- Deprecated: `.streamlit/secrets.toml` (kept empty by policy)

## Required Python Version
- Python 3.11 (recommended)

## Environment Setup
- Copy `.env.example` to `.env` and fill required keys.
- The app fails fast if required keys are missing.

## Quick Start (Windows)
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Daily Commands
```powershell
make check
make test
make smoke
```

## Quality Gates
All changes must pass:
- `make check` (lint + type)
- `make test` (unit tests)
- `make smoke` (minimal runtime verification)
- CI enforces the same commands.

## Windows Task Runner (No make)
```powershell
.\scripts\dev_tasks.ps1 check
.\scripts\dev_tasks.ps1 test
.\scripts\dev_tasks.ps1 smoke
```

## AI Change Policy
- No implementation without `SPEC.md` update.
- No feature without test.
- No completion report without execution log summary.

## CI
CI executes:
- `make check`
- `make test`
- `make smoke`
- Branch protection must require CI to pass before merge.

## Project Structure
- Runtime code: `core/`, `skills/`, `agents/`, `pages/`
- Ops/dev scripts: `scripts/`, `tools/`
- Tests: `tests/`
- Documentation: `docs/`
- External imported references: `external_ref/`

## Notes
- Strategy/reference documents are not runtime contracts.
- Runtime truth is code + tests + CI.
