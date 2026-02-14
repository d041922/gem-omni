# Test Recovery Runbook

## Goal
- Keep `quality-gate` stable while recovering the legacy full test suite.

## Current Gate
- Blocking in CI: `make test` (stable subset)
- Full suite (non-blocking/manual): `make test-full`

## Stable Subset
- `tests/test_policy_init.py`
- `tests/test_news_intelligence.py`
- `tests/test_ui_empty_state.py`
- `tests/test_ui_binding_technicals.py`

## Recovery Process
1. Run `make test-full`.
2. Group failures by root cause:
- Missing compatibility APIs
- Behavior regressions
- External dependency/network assumptions
3. Fix one group per PR.
4. Add fixed tests to stable subset.
5. When full suite is green, switch CI `make test` back to full discovery.

## Exit Criteria
- `make test-full` passes on CI and local.
- `make test` equals full discovery.
- This runbook can be archived.
