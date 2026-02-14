# Test Recovery Runbook

## Goal
- Keep `quality-gate` stable while recovering the legacy full test suite.

## Status
- Active recovery mode:
- Blocking gate: `make test` (stable subset)
- Non-blocking diagnostic: `make test-full-fast` (`pytest --maxfail=20 tests`)
- Failure catalog: `docs/runbook/full_test_failure_catalog.md`

## Recovery Process
1. Run `make test-full`.
2. Group failures by root cause:
- Missing compatibility APIs
- Behavior regressions
- External dependency/network assumptions
3. Fix one group per PR.
4. Fix one failure bucket per PR until `make test-full` is green.

## Exit Criteria
- `make test-full` passes on CI and local.
- `make test` equals full discovery.
- This runbook can be archived.
