# AI Handoff

## Current State

Phase 1 application infrastructure is complete with residual PWA and data-isolation validation work. Phase 2 includes the canonical Python data model, provider contract, FRED adapter with verified live connectivity, and the merged Yahoo daily market-data adapter. A controlled Yahoo live smoke validation is now in progress.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/yahoo-live-smoke`
- Issue: #30 — `feat: add Yahoo live smoke validation`
- Draft PR: #31 — `feat: add Yahoo live smoke validation`

## Implemented on the Active Branch

- `.github/workflows/yahoo-smoke.yml` with manual `workflow_dispatch` and no secret requirement.
- `tools/yahoo_smoke.py` with a bounded recent SPY request through `YahooProvider`.
- Safe result validation requiring at least one observation and rejecting 429, transport, payload, schema, no-observation, and unexpected failures.
- Summary-only logs without raw payloads, full URLs, credentials, or observation values.
- `tests/test_yahoo_smoke.py` with deterministic validation tests and no live network dependency.
- `docs/YAHOO_LIVE_SMOKE.md` with best-effort endpoint, validation, logging, and operational boundaries.
- Python CI path filters include the Yahoo smoke workflow.

## Validation Status

- Python run #15 failed because a test attempted to construct a completely empty `FetchResult`, which the canonical model intentionally rejects.
- The test was corrected to represent a no-observation result with an explicit `MISSING_VALUE` failure.
- Python run #16 passed on commit `c327b5419674a4f75cc84f0aa616f6b17ef12bda`.
- Documentation run #64 passed on the same commit.
- Manual Yahoo Live Smoke remains pending because a newly added `workflow_dispatch` workflow cannot be manually dispatched until the workflow exists on the default branch.
- Do not claim Yahoo live connectivity until an actual successful workflow run is recorded.

## Verified Completed Work

- PR #16: Phase 2 Data Platform design
- PR #18: canonical data model and provider abstraction
- PR #20: FRED economic-series adapter
- PR #22: protected FRED live smoke workflow
- PR #24: corrected expected FRED partial-result handling
- PR #26: release-oriented roadmap and release history
- PR #29: Yahoo daily market-data adapter, merged as `bc0c706620895063689c96e655317e0060f20ab8`
- Live FRED connectivity validated with repository secret `FRED_API_KEY`

## Yahoo Rules

- Yahoo is a best-effort public chart endpoint, not a guaranteed official production API.
- Canonical identity comes only from explicit `YahooSymbolBinding` entries.
- Financial values use `Decimal`; timestamps are normalized to UTC.
- Missing or malformed rows never become trusted observations.
- Controlled live validation proves only the bounded call that actually ran.
- Fallback provider strategy remains future work.

## Known Limitations

- Yahoo live connectivity has not yet been validated by the new workflow.
- The manual workflow must first exist on `main` before it can be dispatched through GitHub Actions.
- No ECOS adapter, cache executor, retry executor, persistence, migration, scheduled ingestion, analysis, portfolio, recommendation, or backtest logic exists.
- PWA install/offline validation, user-owned tables, RLS, and cross-user isolation remain pending.
- Frontend CI still lacks a committed package lockfile.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit secrets, tokens, raw live payloads, or personal portfolio data.
3. Preserve Requirement IDs and update traceability documents.
4. Do not claim live-provider validation without actual run evidence.
5. Substantial pull requests begin as Draft.
6. Never merge without explicit user approval.

## Exact Next Recommended Task

Confirm fresh Python and Documentation CI after the living-document updates. If both pass, mark PR #31 Ready for Review. Do not merge without explicit user approval. After merge, manually dispatch `Yahoo Live Smoke`, record the actual result, and if needed follow with a small evidence-only documentation PR.
