# AI Handoff

## Current State

Phase 1 application infrastructure is complete with residual PWA and data-isolation validation work. Phase 2 includes the canonical Python data model, provider contract, FRED adapter with verified live connectivity, merged Yahoo daily market-data and live-smoke support, and a merged provider-independent bounded retry executor. Yahoo Live Smoke has twice reached the public endpoint from GitHub-hosted runners but has not yet returned trusted observations: run `31141445027` failed with `HTTP_429`, and run `31150601290` exhausted three bounded retries with `HTTP_429`. Yahoo HTTP header hardening is now in validation.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/yahoo-header-hardening`
- Issue: #34 — `feat: harden Yahoo HTTP request headers`
- Draft PR: #35 — `feat: harden Yahoo HTTP request headers`

## Implemented on the Active Branch

- Yahoo default transport builds an explicit GET `urllib.request.Request`.
- Default headers are a stable project-specific `User-Agent`, `Accept: application/json`, and `Accept-Language: en-US,en;q=0.9`.
- Injected transport signature remains unchanged for deterministic provider fixtures.
- Network-free default-transport test verifies headers, GET method, and timeout.
- Added `docs/YAHOO_TRANSPORT.md` and updated Yahoo live-smoke evidence.
- No Yahoo account, API key, cookies, crumb token, authenticated session, proxy, IP rotation, CAPTCHA bypass, or HTML scraping.

## Validation Status

- Previous Yahoo Live Smoke run `31141445027` failed safely with `HTTP_429` on the live provider call.
- Bounded retry PR #33 merged as `db76e2199639b075101c9c7d08e9266c1b5c8116` after Python run #26 and Documentation run #74 passed.
- Post-merge Yahoo Live Smoke run `31150601290` made three attempts and failed safely with `HTTP_429`; `retry_exhausted=true`.
- Yahoo header-hardening Python run #28 and Documentation run #78 passed on `e61674e1d98c3034f14a4a643ae1bedbb92aff22`.
- Fresh CI is required on the final documentation-evidence head before Ready for Review.
- Do not claim Yahoo live retrieval success unless a later actual smoke run returns canonical observations.

## Verified Completed Work

- PR #16: Phase 2 Data Platform design
- PR #18: canonical data model and provider abstraction
- PR #20: FRED economic-series adapter
- PR #22: protected FRED live smoke workflow
- PR #24: corrected expected FRED partial-result handling
- PR #26: release-oriented roadmap and release history
- PR #29: Yahoo daily market-data adapter
- PR #31: Yahoo live-smoke workflow, merged as `048f1026b64596e44f2caa8ba5160fa3e1426b21`
- PR #33: bounded retry executor, merged as `db76e2199639b075101c9c7d08e9266c1b5c8116`
- Live FRED connectivity validated with repository secret `FRED_API_KEY`

## Retry Rules

- Adapters classify failures; the common executor decides whether to retry.
- Retryable does not mean infinite retry: every execution has a hard attempt bound.
- Partial results are not automatically retried because whole-request repetition can duplicate successful source work.
- Authentication, validation, schema, binding, and other deterministic failures must stop immediately when classified non-retryable.
- Retry evidence includes attempt count and delays without exposing provider payloads or sensitive URLs.

## Yahoo Rules

- Yahoo is a best-effort public chart endpoint, not a guaranteed official production API.
- Financial values use `Decimal`; timestamps are normalized to UTC.
- Missing or malformed rows never become trusted observations.
- `HTTP_429` is an observed live failure mode on GitHub-hosted runners.
- Minimal explicit request headers are permitted, but cookies, browser-session emulation, proxying, and bypass techniques are outside scope.
- Bounded retries and request headers may improve transient access but do not guarantee provider availability.
- Fallback provider strategy remains future work.

## Known Limitations

- Yahoo live data retrieval has not yet succeeded in the recorded smoke workflow.
- Identifier-scoped retries, `Retry-After` metadata handling, cache, fallback provider, persistence, migration, and scheduled ingestion remain future work.
- No ECOS adapter, analysis, portfolio, recommendation, or backtest logic exists.
- PWA install/offline validation, user-owned tables, RLS, and cross-user isolation remain pending.
- Frontend CI still lacks a committed package lockfile.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit secrets, tokens, raw live payloads, or personal portfolio data.
3. Preserve Requirement IDs and update traceability documents.
4. Do not claim live-provider validation without actual run evidence.
5. Substantial pull requests begin as Draft.
6. Never merge without explicit user approval.

## Process Note

A placeholder `docs/YAHOO_TRANSPORT.md` was accidentally committed directly to `main` while starting Issue #34 and immediately removed in commit `36c5d9c2cb11216d3a3d8319d3093ba0b308fee0`. The actual feature work is isolated to Issue #34 and `agent/yahoo-header-hardening`.

## Exact Next Recommended Task

Confirm fresh Python and Documentation CI on the final PR #35 head after evidence updates. If both pass, mark PR #35 Ready for Review. Do not merge without explicit user approval. After merge, manually run Yahoo Live Smoke and record whether the explicit headers allow trusted observations or whether `HTTP_429` persists.
