# AI Handoff

## Current State

Phase 1 application infrastructure is complete with residual PWA and data-isolation validation work. Phase 2 includes the canonical Python data model, provider contract, FRED adapter with verified live connectivity, and the merged Yahoo daily market-data adapter and live-smoke workflow. The first Yahoo live run reached the provider but failed with `HTTP_429`, so live data retrieval success is still unverified. A provider-independent bounded retry executor is now in validation.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/bounded-retry-executor`
- Issue: #32 — `feat: add bounded retry executor and apply it to Yahoo smoke`
- Draft PR: #33 — `feat: add bounded retry executor and apply it to Yahoo smoke`

## Implemented on the Active Branch

- `investment_manager/data/retry.py` with `RetryPolicy`, `RetryExecution`, and `BoundedRetryExecutor`.
- Whole-request retry only when there are no trusted observations and all failures are retryable.
- Immediate stop for partial results and deterministic non-retryable failures.
- Bounded exponential backoff with injected jitter and sleep dependencies.
- `tests/test_retry_executor.py` with deterministic recovery, exhaustion, non-retryable, partial, success, and invalid-policy coverage.
- Yahoo Live Smoke integration with maximum three attempts and safe attempt/exhaustion logging.
- Updated retry and Yahoo operational documentation and living project records.

## Validation Status

- Previous Yahoo Live Smoke run `31141445027` on `main` commit `048f1026b64596e44f2caa8ba5160fa3e1426b21` failed safely with `HTTP_429` on the actual provider call.
- Python run #22 passed on implementation head `bfdfc4cc005565647beeeb754bb104438eaf0ec5`.
- Documentation run #70 passed on the same head.
- Living-document evidence updates after that commit require fresh Python and Documentation CI before Ready for Review.
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
- Bounded retries may recover transient failures but do not guarantee provider availability.
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

## Exact Next Recommended Task

Confirm fresh Python and Documentation CI on the latest PR #33 head after evidence updates. If both pass, mark PR #33 Ready for Review. Do not merge without explicit user approval. After merge, manually run Yahoo Live Smoke again and record whether bounded retries recover the transient `HTTP_429` or exhaust safely.
