# AI Rules

This file defines mandatory rules for Codex/Gemini-assisted development in this repo.

## 1. Scope and Safety
- Work from an issue and keep one purpose per branch.
- Keep commits small and revertable.
- Do not ship unverified assumptions about external APIs.
- Do not modify code outside the approved `SPEC.md` scope.
- If unknown, do not guess. Add a TODO with verification plan and risk note.

## 2. Runtime vs Tooling Separation
- Runtime code must be deterministic and testable.
- AI tooling is for development support only, not runtime dependency.
- External integrations must be called through code modules under `skills/` or `agents/tools/`.

## 3. Required Workflow
- Update `SPEC.md` before substantial changes.
- Run `make check` and `make test` before completion.
- Update docs when behavior, setup, env keys, or commands change.
- Behavior-changing work must include at least one test. Exceptions must be documented in `SPEC.md`.

## 4. Environment Rules
- Single source of truth: `.env`.
- Never commit secrets.
- Add/modify keys in `.env.example` and keep `tools/verify_docs.py` green.

## 5. Quality Gates
- Lint/format/type checks should pass where configured.
- Add at least one test for changed behavior whenever feasible.
- Keep smoke checks runnable from one command (`make smoke`).
- Completion report must include executed commands, pass/fail result, and log summary path.

## 6. CI Enforcement
- CI (`quality-gate`) must pass before merge.
- Branch protection must require CI status checks on the default branch.
