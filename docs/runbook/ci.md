# CI Runbook

## Pipeline Goals
- Verify code health quickly and deterministically.
- Catch env/docs drift early.

## Required Jobs
1. Install dependencies
2. `make check`
3. `make test`
4. `make smoke`

## Enforcement
- CI must execute the same make targets as local development (`make check/test/smoke`).
- Default branch protection must require `quality-gate` to pass before merge.
- CI is the source of truth for merge readiness.

## Notes
- CI uses stub mode for external integrations by default.
- `.env` is not required in CI; use `.env.example` validation and stubs.
- `make test` is the blocking stable subset gate.
- `make test-full-fast` runs full-suite diagnostics (`--maxfail=20`) as non-blocking.
