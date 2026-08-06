# AI Handoff

## Current State

Phase 1 application infrastructure is complete with residual PWA and data-isolation validation work. Phase 2 data-platform design, canonical Python models, provider contracts, the FRED adapter, and protected FRED live connectivity validation are complete.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/roadmap-release-history`
- Issue: #25 — `docs: establish roadmap and release history`
- PR: not yet created

## Verified Completed Work

- PR #16: Phase 2 Data Platform design
- PR #18: canonical data model and provider abstraction
- PR #20: FRED economic-series adapter
- PR #22: protected FRED live smoke workflow
- PR #24: corrected expected partial-result handling for live smoke validation
- Python and Documentation CI passed for the FRED adapter and smoke fix.
- Live FRED connectivity was successfully validated with repository secret `FRED_API_KEY`.

## Active Documentation Work

- Refresh `ROADMAP.md` with release-oriented status and exit criteria.
- Add `RELEASES.md` as the curated product-level release history.
- Define the project Definition of Done without weakening explicit user approval before merge.
- Correct stale FRED status in living documentation.

## FRED Rules Enforced

- The FRED API key is runtime-only and stored as an encrypted GitHub Actions secret.
- The key is not committed, logged, returned, or exposed to the frontend.
- Series IDs map to canonical subject IDs and units only through explicit bindings.
- Requests use the official Version 1 observations JSON endpoint.
- Values use `Decimal`; observation dates become UTC timestamps.
- FRED `.` values never become observations.
- Revision metadata and explicit provider failures are preserved.
- Live smoke validation succeeds only when valid observations exist and all failure codes are expected `MISSING_VALUE` or `OUT_OF_RANGE` warnings.
- Authentication, HTTP, transport, payload, binding, parsing, and empty-result failures remain fatal.

## Known Limitations

- No production FRED series catalog is approved.
- No Yahoo, ECOS, or FX adapter exists.
- No cache executor, retry executor, persistence, migration, scheduled ingestion, analysis, portfolio, recommendation, or backtest logic exists.
- PWA install/offline validation, user-owned tables, RLS, and cross-user isolation remain pending.
- Frontend CI still lacks a committed package lockfile.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Keep provider payloads and credentials behind trusted adapters.
3. Preserve Requirement IDs and update traceability documents.
4. Never use binary floating point for canonical financial values.
5. Never commit secrets, tokens, or personal portfolio data.
6. Do not claim live-provider validation without evidence.
7. Substantial pull requests begin as Draft.
8. Never merge without explicit user approval.
9. Update roadmap, release history, worklog, changelog, and handoff for completed milestones.

## Exact Next Recommended Task

Complete Issue #25 by updating living documents, opening a Draft PR, and passing Documentation CI. After user-approved merge, create a separately scoped Issue for the Yahoo market-data adapter only after verifying the current provider contract, access method, stability, and legal or operational constraints.
