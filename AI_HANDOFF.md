# AI Handoff

## Current State

Phase 1 application infrastructure is complete with residual PWA and data-isolation validation work. Phase 2 includes the canonical Python data model, provider contract, FRED adapter with verified live connectivity, and a Yahoo daily market-data adapter that has passed fixture-based Python and Documentation CI in PR #29.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/yahoo-market-adapter`
- Issue: #28 — `feat: implement Yahoo market-data adapter`
- PR: #29 — `feat: implement Yahoo market-data adapter`

## Implemented on the Active Branch

- `investment_manager/data/yahoo.py` with explicit symbol bindings and daily chart normalization.
- Market-price and FX-rate dataset support.
- Adjusted close as the canonical value with OHLCV and adjustment metadata preserved.
- Deterministic observation IDs, `Decimal` values, and UTC timestamps.
- Explicit binding, dataset, HTTP, transport, payload, missing-value, parsing, and range failures.
- Partial results when some symbols succeed and others fail.
- `tests/test_yahoo_provider.py` with deterministic fixtures and no live network dependency.
- `docs/YAHOO_ADAPTER.md` with contract, normalization, failure, test, and operational boundaries.

## Validation Evidence

- Python run #10 passed for commit `3444d9381c8924902414742fdeb6c1c5772db08b`.
- Documentation run #58 passed for commit `3444d9381c8924902414742fdeb6c1c5772db08b`.
- Any documentation commit after that SHA requires fresh Python and Documentation CI before PR #29 is marked Ready for Review.

## Verified Completed Work

- PR #16: Phase 2 Data Platform design
- PR #18: canonical data model and provider abstraction
- PR #20: FRED economic-series adapter
- PR #22: protected FRED live smoke workflow
- PR #24: corrected expected partial-result handling
- PR #26: release-oriented roadmap and release history
- Live FRED connectivity validated with repository secret `FRED_API_KEY`

## Yahoo Rules

- Canonical identity comes only from explicit `YahooSymbolBinding` entries.
- The adapter uses daily historical chart payloads only.
- No rendered HTML scraping or third-party Yahoo wrapper is used.
- Financial values use `Decimal`; timestamps are normalized to UTC.
- Missing or malformed rows never become trusted observations.
- No stable production availability is claimed without a separate controlled live smoke test.

## Known Limitations

- Yahoo live connectivity and production availability have not been validated.
- No ECOS adapter, cache executor, retry executor, persistence, migration, scheduled ingestion, analysis, portfolio, recommendation, or backtest logic exists.
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

Confirm fresh Python and Documentation CI on the latest PR #29 head, then mark PR #29 Ready for Review if both pass. Keep the PR unmerged until explicit user approval. After merge, create a separately scoped protected Yahoo live smoke test before claiming production connectivity.
