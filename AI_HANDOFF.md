# AI Handoff

## Current State

Phase 1 infrastructure is complete. Phase 2 design and the canonical Python provider foundation were merged in PRs #16 and #18. The first real provider adapter, FRED economic series, is active.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/fred-adapter`
- Issue: #19 — `feat: implement FRED economic series adapter`
- PR: not yet created

## Implemented on the Active Branch

- `investment_manager/data/fred.py` with `FredProvider`, `FredSeriesBinding`, injectable transport and clock, official observations request construction, normalization, and failure classification.
- `tests/test_fred_provider.py` with deterministic fixture coverage and no live network dependency.
- `docs/FRED_ADAPTER.md` with official contract, API-key boundary, normalization, missing-data, revision, and test rules.
- Data package exports for the FRED adapter.

## FRED Rules Enforced

- The adapter accepts only a runtime-injected 32-character lowercase alphanumeric FRED API key.
- The key is not committed, logged, returned, or exposed to the frontend.
- Series IDs map to canonical subject IDs and units only through explicit bindings.
- Requests use the official Version 1 observations JSON endpoint with observation bounds and ascending sort.
- Values use `Decimal`; observation dates become UTC timestamps.
- FRED `.` missing values cannot become observations.
- Real-time start and end fields are preserved as revision metadata.
- Transport, HTTP, payload, binding, parsing, missing-value, and range failures are explicit.
- Mixed valid and failed series produce a partial `FetchResult`.

## Validation

Pending Draft PR execution:

```text
python -m compileall -q investment_manager tests
python -m unittest discover -s tests -v
```

Documentation CI and Python CI must both pass before Ready for Review. Live FRED access is not part of CI and is not yet claimed.

## Known Limitations

- No runtime FRED credential has been configured or live integration tested.
- No production FRED series catalog has been approved.
- No Yahoo Finance, ECOS, or FX adapter exists.
- No cache executor, retry executor, persistence, database migration, scheduled ingestion, analysis, portfolio, or recommendation logic exists.
- PWA install/offline validation, user tables, RLS, and cross-user isolation remain pending.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Keep provider payloads and credentials behind trusted adapters.
3. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md`.
4. Never use binary floating point for canonical financial values.
5. Never commit secrets, tokens, or personal portfolio data.
6. Do not claim live-provider validation without evidence.
7. Never merge without explicit user approval.

## Exact Next Recommended Task

Complete Issue #19 by updating traceability and Changelog, creating a Draft PR, and passing Python and Documentation CI. After merge, separately configure a protected FRED API key and controlled live smoke test, or proceed to the ECOS adapter after verifying its current official contract.
