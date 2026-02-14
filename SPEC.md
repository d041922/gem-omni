# SPEC Template

Use one template:
- `SPEC-Lite`: small bugfixes/refactors with low integration risk
- `SPEC-Full`: behavior/integration/data/env changes

---

## SPEC-Lite

### Title
- Change name:

### Goal
- What problem this change solves:

### Scope
- In scope:
- Out of scope:

### Assumptions / Unknowns
- Assumptions (must be verified):
- Unknowns / TBD:
- Verification plan for unknowns:

### Validation Plan
- Required commands (attach evidence):
  - make check:
  - make test:
  - make smoke:

### Result
- Summary:
- Evidence (required):
  - Commands executed + results:
  - Changed files list:
  - Test report snippet:

---

## SPEC-Full

## Title
- Change name:

## Goal
- What problem this change solves:

## Non-Goals
- What this change intentionally does not do:

## Scope
- In scope:
- Out of scope:

## Design
- Key decisions:
- Data flow / integration impact:
- Risk and rollback plan:

## Assumptions / Unknowns
- Assumptions (must be verified):
- Unknowns / TBD:
- Verification plan for unknowns:

## External Integrations (Hallucination Risk)
- APIs/SDKs touched:
- Version/endpoint references:
- Stub vs Live behavior:

## Environment / Config Changes
- New/changed env keys:
- Required/optional classification:
- Backward compatibility:

## Validation Plan
- Unit tests:
- Smoke tests:
- Manual checks:
- Required commands (attach evidence):
  - make check:
  - make test:
  - make smoke:

## Docs to Update
- README:
- Runbook:
- ADR:

## Result
- Summary:
- Evidence (required):
  - Commands executed + results:
  - Changed files list:
  - Test report snippet:
