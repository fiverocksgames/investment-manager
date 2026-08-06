# Worklog

## 2026-08-06 — Roadmap and Release History

### Documentation Work

- Created Issue #25 and branch `agent/roadmap-release-history`.
- Converted the existing roadmap into a release-oriented living plan.
- Recorded Release 0.1 as the application foundation and Release 0.2 as the active data-platform release.
- Added `RELEASES.md` with curated Added, Changed, Fixed, Security, Validation, and remaining-work sections.
- Added a project Definition of Done aligned with `PROJECT_POLICY.md`.
- Corrected stale FRED status in `AI_HANDOFF.md` and `CHANGELOG.md`.

### Verified FRED Completion

- PR #20 implemented the FRED economic-series adapter.
- PR #22 added the protected manual live smoke workflow.
- PR #24 corrected expected partial-result handling and merged after explicit user approval.
- Python run #7 and Documentation run #52 passed before PR #24 merge.
- Protected FRED live connectivity was successfully validated with repository secret `FRED_API_KEY`.

### Current Documentation Status

- Issue: #25 — `docs: establish roadmap and release history`
- Branch: `agent/roadmap-release-history`
- Draft PR and Documentation CI are pending.

## 2026-08-06 — FRED Smoke Partial-Result Fix

- Investigated live Actions run `31078092784` and confirmed the API key, package installation, network path, and FRED response were working.
- Identified a false-negative policy: valid DGS10 observations were accompanied by expected `MISSING_VALUE` and `OUT_OF_RANGE` conditions.
- Added a pure smoke-result validator that tolerates only those two warning codes when at least one valid observation exists.
- Preserved fatal handling for empty results and all configuration, authentication, HTTP, transport, binding, payload, and parsing failures.
- Added deterministic unit tests for tolerated partial results, fatal mixed results, and empty partial results.
- Updated `docs/FRED_LIVE_SMOKE.md` with the corrected validation contract.
- Python run #7 and Documentation run #52 passed.
- A protected live smoke run succeeded from the fix branch.
- PR #24 merged as commit `26cc2fdd6a2faa5fb542384c15aa72d39c00bbac` after explicit user approval.

## 2026-08-06 — Protected FRED Live Smoke Test

- Created Issue #21 and branch `agent/fred-live-smoke`.
- Added a manual `FRED Live Smoke` workflow using repository secret `FRED_API_KEY`.
- Added `tools/fred_smoke.py` to query bounded `DGS10` observations through the merged `FredProvider`.
- Added `docs/FRED_LIVE_SMOKE.md` with setup, execution, evidence, rotation, and security rules.
- Python run #5 and Documentation run #50 passed.
- PR #22 merged as commit `deb62203e473a5c28613020fc0e8607923084133` after explicit user approval.

## 2026-08-06 — FRED Economic Series Adapter

- Created Issue #19 and branch `agent/fred-adapter`.
- Verified the official FRED Version 1 observations contract before implementation.
- Added `FredProvider`, `FredSeriesBinding`, injectable HTTPS transport, deterministic observation IDs, and explicit failure classification.
- Added fixture-based tests for request construction, successful parsing, missing values, invalid payloads, HTTP errors, unknown bindings, unsupported datasets, and partial results.
- Added `docs/FRED_ADAPTER.md` with API-key, normalization, revision, missing-data, and testing boundaries.
- Python run #3 and Documentation run #47 passed.
- PR #20 merged as commit `510e7ad1bb801e4d3e9a220bca1c4d809033f6e2`.

## 2026-08-06 — Canonical Data Model and Provider Abstraction

- Issue #17 and PR #18 added the Python canonical model, provider contracts, unit tests, and Python CI.
- Python run #1 and Documentation run #45 passed.
- PR #18 merged and Issue #17 closed as completed.

## 2026-08-06 — Phase 2 Data Platform Design

- Issue #15 and PR #16 defined the provider-independent model, freshness, cache, retry, ingestion, failure, and immutable snapshot rules.
- Documentation run #43 passed and PR #16 merged.
- Issue #15 closed as completed.

## 2026-08-06 — Project Development Policy v1

- `fiverocksgames/investment-manager` was established as the canonical repository.
- PR #14 merged after Documentation run #41.
- Issue #13 closed as completed.

## 2026-08-06 — Phase 1 Closure

- React, TypeScript, Vite, Tailwind CSS, PWA baseline, GitHub Pages, Supabase, and Google OAuth were completed.
- Login persistence and sign-out were manually verified.
- PWA install/offline validation, package lock, user tables, RLS, and cross-user isolation remain pending.

## 2026-08-05 — Earlier Bootstrap Work

- PR #1 established governance and documentation CI.
- PR #4 established the frontend baseline.
- PR #6 established Supabase authentication.
- PR #8 wired public Supabase repository Variables.
