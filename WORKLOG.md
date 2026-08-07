# Worklog

## 2026-08-07 — Yahoo Live Smoke Validation

- Created Issue #30 and branch `agent/yahoo-live-smoke`.
- Added manual `Yahoo Live Smoke` workflow with no secret requirement.
- Added `tools/yahoo_smoke.py` using a bounded 14-day SPY request through the canonical adapter.
- Added deterministic smoke-result tests covering tolerated row warnings, HTTP 429, invalid payloads, and no-observation results.
- Added `docs/YAHOO_LIVE_SMOKE.md` with best-effort endpoint, safe-failure, logging, and operational boundaries.
- Python run #15 failed because the smoke test attempted to construct an invalid completely empty `FetchResult`; the canonical invariant correctly rejected it.
- Updated the test to represent a no-observation result with an explicit `MISSING_VALUE` failure while preserving the canonical model invariant.
- Python run #16 and Documentation run #64 passed on commit `c327b5419674a4f75cc84f0aa616f6b17ef12bda`.
- Manual Yahoo Live Smoke remains pending because the new `workflow_dispatch` workflow is not available for manual dispatch until it exists on the default branch.
- Live connectivity has not yet been claimed.
- Explicit user approval remains required before merge.

## 2026-08-06 — Yahoo Market-Data Adapter

### Adapter Work

- Created Issue #28 and branch `agent/yahoo-market-adapter` from the latest `main`.
- Opened Draft PR #29.
- Added `YahooProvider` and `YahooSymbolBinding` for daily market-price and FX-rate history.
- Normalized adjusted close into canonical observations while preserving open, high, low, close, volume, currency, interval, timezone, and adjustment metadata.
- Added deterministic identifiers, `Decimal` conversion, UTC timestamps, explicit failures, and partial-result behavior.
- Added fixture tests for SPY-style market bars, FX bindings, missing rows, malformed payloads, HTTP retry classification, and mixed outcomes.
- Added `docs/YAHOO_ADAPTER.md` and updated traceability, handoff, and changelog documents.

### Adapter Boundaries

- Daily historical bars only.
- No rendered HTML scraping or third-party Yahoo wrapper.
- No intraday, streaming, options, fundamentals, recommendation, persistence, caching, scheduling, analysis, portfolio, or UI work.
- Live connectivity is not claimed before a separate controlled smoke test.

### Adapter Validation Status

- Python run #10 and Documentation run #58 passed on the initial implementation commit.
- Python run #14 and Documentation run #62 passed after living-document updates.
- PR #29 merged as commit `bc0c706620895063689c96e655317e0060f20ab8` after explicit user approval.
- Issue #28 closed as completed.

## 2026-08-06 — Roadmap and Release History

- Issue #25 and PR #26 established release-oriented `ROADMAP.md`, `RELEASES.md`, and Definition of Done.
- Documentation run #55 passed.
- PR #26 merged as commit `d056baa01c2c94d61754117a7599f1e82534f972` after explicit user approval.

## 2026-08-06 — FRED Smoke Partial-Result Fix

- Investigated live Actions run `31078092784` and confirmed the API key, package installation, network path, and FRED response were working.
- Added a validator that tolerates only `MISSING_VALUE` and `OUT_OF_RANGE` when valid observations exist.
- Python run #7 and Documentation run #52 passed.
- A protected live smoke run succeeded.
- PR #24 merged as commit `26cc2fdd6a2faa5fb542384c15aa72d39c00bbac`.

## 2026-08-06 — Protected FRED Live Smoke Test

- Added a manual `FRED Live Smoke` workflow using repository secret `FRED_API_KEY`.
- Python run #5 and Documentation run #50 passed.
- PR #22 merged as commit `deb62203e473a5c28613020fc0e8607923084133`.

## 2026-08-06 — FRED Economic Series Adapter

- Added the official FRED Version 1 observations adapter and deterministic fixture tests.
- Python run #3 and Documentation run #47 passed.
- PR #20 merged as commit `510e7ad1bb801e4d3e9a220bca1c4d809033f6e2`.

## 2026-08-06 — Canonical Data Model and Provider Abstraction

- Issue #17 and PR #18 added the Python canonical model, provider contracts, unit tests, and Python CI.
- Python run #1 and Documentation run #45 passed.

## 2026-08-06 — Phase 2 Data Platform Design

- Issue #15 and PR #16 defined provider-independent model, freshness, cache, retry, ingestion, failure, and immutable snapshot rules.
- Documentation run #43 passed.

## 2026-08-06 — Project Development Policy v1

- `fiverocksgames/investment-manager` was established as the canonical repository.
- PR #14 merged after Documentation run #41.

## 2026-08-06 — Phase 1 Closure

- React, TypeScript, Vite, Tailwind CSS, PWA baseline, GitHub Pages, Supabase, and Google OAuth were completed.
- Login persistence and sign-out were manually verified.
- PWA offline validation, package lock, user tables, RLS, and cross-user isolation remain pending.
