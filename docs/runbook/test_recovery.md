# Test Recovery Runbook

## Goal
- Keep `quality-gate` stable while recovering the legacy full test suite.

## Status
- Completed: CI gate has returned to full discovery via `make test`.
- `make test-full` is retained as an alias for operator convenience.

## Recovery Process
1. Run `make test-full`.
2. Group failures by root cause:
- Missing compatibility APIs
- Behavior regressions
- External dependency/network assumptions
3. Fix one group per PR.
4. Keep `make test` mapped to full discovery.

## Exit Criteria
- `make test-full` passes on CI and local.
- `make test` equals full discovery.
- This runbook can be archived.
