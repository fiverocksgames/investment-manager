# Worklog

## 2026-08-06 — Protected FRED Live Smoke Test

### Live Validation Work

- Created Issue #21 and branch `agent/fred-live-smoke`.
- Added a manual `FRED Live Smoke` workflow using repository secret `FRED_API_KEY`.
- Added `tools/fred_smoke.py` to query the bounded `DGS10` fixture through the merged `FredProvider`.
- Added `docs/FRED_LIVE_SMOKE.md` with setup, execution, evidence, rotation, and security rules.

### Live Validation Boundaries

- The workflow is manual only and never runs on pull requests, pushes, or schedules.
- The API key must exist only as an encrypted Actions secret.
- Logs contain only safe summary metadata and never the key or raw request URL.
- No live run is claimed until the user registers the secret and a workflow run succeeds.

### Live Validation Remaining Work

- Create a Draft PR and pass Python and Documentation CI.
- Ask the user to register `FRED_API_KEY` without sharing its value.
- Run the manual workflow and retain the run number as validation evidence.
- Request explicit approval before merge.

## 2026-08-06 — FRED Economic Series Adapter

### FRED Adapter Work

- Created Issue #19 and branch `agent/fred-adapter`.
- Verified the current official FRED Version 1 observations contract before implementation.
- Added `FredProvider`, `FredSeriesBinding`, injectable HTTPS transport, deterministic observation IDs, and explicit failure classification.
- Added fixture-based tests for request construction, successful parsing, missing values, invalid payloads, HTTP errors, unknown bindings, unsupported datasets, and partial results.
- Added `docs/FRED_ADAPTER.md` with API-key, normalization, revision, missing-data, and testing boundaries.

### FRED Adapter Boundaries

- The FRED API key is runtime-only and must never enter the repository, frontend, logs, or failure values.
- FRED `.` values become `MISSING_VALUE` failures and never trusted observations.
- Canonical subject IDs and units come only from explicit bindings.
- CI performs no live FRED requests and requires no credential.
- Cache, retry execution, persistence, scheduling, and production series selection remain separate work.

### FRED Adapter Validation Status

- Python run #3 and Documentation run #47 passed.
- PR #20 merged and Issue #19 closed as completed.
- No live FRED integration is claimed yet.

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
