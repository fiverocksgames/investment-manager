# Worklog

## 2026-08-07 — Canonical FX Normalization

- Created Issue #42 and branch `agent/fx-normalization`; opened Draft PR #43.
- Added provider-independent `FxPair`, `FxNormalizationBinding`, `FxNormalizationError`, and `FxNormalizer`.
- Canonical FX values are explicitly quote currency per one base currency with units such as `KRW_per_USD`.
- Direct direction preserves the exact source `Decimal`; reversed direction uses a fixed 34-digit Decimal reciprocal with `ROUND_HALF_EVEN`.
- Invalid codes, identical currencies, unrelated source pairs, zero/negative rates, non-FX observations, and subject mismatches are rejected rather than guessed.
- Provider/source identity, retrieval time, revision, quality/freshness, and source metadata are preserved; normalized IDs are deterministic.
- Added deterministic network-free tests including Yahoo `KRW=X`, whose source direction is explicitly configured as USD/KRW rather than inferred from ticker syntax.
- Added `docs/FX_NORMALIZATION.md` and updated data model, data-source, test-plan, traceability, and handoff documentation.
- Initial implementation head `044e350e9c028eb25944463328a69905c3b1ec73`: Documentation run #103 passed and Python run #51 test job passed.
- Fresh CI is required after final living-document updates before Ready for Review. Explicit user approval remains required before merge.

## 2026-08-07 — ECOS Live Success Evidence

- PR #39 merged as commit `23bd2ef88ce7ab3f3da2f288ad066089c163f2e8`; Issue #38 closed.
- ECOS Live Smoke run `31182329368` succeeded on merged `main` commit `23bd2ef88ce7ab3f3da2f288ad066089c163f2e8`.
- The run used GitHub Actions secret `ECOS_API_KEY` without exposing the key.
- `provider=ecos`, `source_identifier=bok_base_rate_daily`, `attempt_count=1`, `observation_count=99`.
- Observed range in the returned trusted observations was `2026-02-09T00:00:00+00:00` through `2026-05-18T00:00:00+00:00`, canonical unit `percent_per_annum`, cycle `D`.
- `OUT_OF_RANGE` appeared only as a tolerated warning and did not prevent successful live validation.
- This is bounded evidence that ECOS live retrieval succeeded for this run; it is not a guarantee of permanent provider availability.
- FRED, Yahoo, and ECOS now each have verified successful live retrieval evidence.

## 2026-08-07 — ECOS Transport Diagnostics

- PR #37 merged as commit `0f3106bb8772317679df52e76717c6e9ddfebe94` after explicit user approval; Issue #36 closed.
- ECOS Live Smoke run `31174803601` failed safely with `MISSING_SECRET` before any provider attempt because `ECOS_API_KEY` was not configured.
- After `ECOS_API_KEY` was configured, run `31180017610` reached the live-call path but exhausted three bounded attempts with canonical `TRANSPORT_ERROR`.
- Created Issue #38 and branch `agent/ecos-transport-diagnostics` to improve safe transport observability.
- Kept canonical failure code and retry semantics unchanged while adding sanitized categories: `timeout`, `dns`, `tls`, `connection`, and fallback `transport`.
- Sanitized diagnostics use exception types only; raw exception text, secret-bearing URLs, API keys, payloads, and observation values are excluded.
- Added deterministic network-free tests for timeout, DNS, TLS, and connection-reset classification.
- Updated ECOS smoke output to include sanitized `transport_details` only when available.
- Updated `docs/ECOS_ADAPTER.md` with the two observed live-smoke failures and diagnostic boundaries.
- Draft PR #39 opened; implementation/documentation head `b579523ba5e6989127588b7c5f6197fcd9d85db1` passed Python run #46 and Documentation run #96.
- Final changelog-evidence head `d9bed23781defaa1b389af93fdcf454e7f5fe058` passed Python run #49 and Documentation run #99 before merge.

## 2026-08-07 — ECOS Economic-Series Adapter

- Yahoo Live Smoke run `31169043266` succeeded on merged header-hardening commit `18dd594a93ca45f966b79a3b612808751c99c112`, returning 10 trusted SPY daily observations on attempt 1. This is bounded live-success evidence, not an availability guarantee.
- Created Issue #36 and branch `agent/ecos-adapter`.
- Opened Draft PR #37.
- Added `EcosProvider` and `EcosSeriesBinding` for Bank of Korea ECOS `StatisticSearch` economic-series data.
- Added explicit statistic/item/cycle bindings, canonical `Decimal` values, UTC-aware period-start timestamps, deterministic UUIDs, source metadata, explicit partial results, and failure classification.
- Initial cycle support is annual (`A`), quarterly (`Q`), monthly (`M`), and daily (`D`).
- Added deterministic fixture tests for valid observations, missing values, malformed periods, unknown bindings, authentication failures, retryable server failures, malformed payloads, out-of-range rows, and quarterly normalization.
- Added manual `.github/workflows/ecos-smoke.yml` and `tools/ecos_smoke.py` using GitHub Actions secret `ECOS_API_KEY` and the common bounded retry executor.
- Added `docs/ECOS_ADAPTER.md`, updated `docs/DATA_SOURCES.md`, `docs/TEST_PLAN.md`, traceability, handoff, changelog, and Python CI path filtering.
- Initial implementation head `3b39f64343bab411bb1f8c6ba8fa1170670d022b`: Python run #34 and Documentation run #84 passed.
- Documentation-complete head `349c12d1671dea4a5504ca82f10e4a10a624bca0`: Python run #40 and Documentation run #90 passed.
- Final evidence head `674eacc0d6254cc7c94b436bf4d35203e1c8fecb`: Python run #44 and Documentation run #94 passed before merge.

## 2026-08-07 — Yahoo HTTP Header Hardening

- Earlier Yahoo Live Smoke runs `31141445027` and `31150601290` exposed `HTTP_429`; the latter exhausted three bounded retries safely.
- Issue #34 and PR #35 added a stable project-specific `User-Agent`, JSON `Accept`, English `Accept-Language`, deterministic transport tests, and `docs/YAHOO_TRANSPORT.md`.
- Python run #32 and Documentation run #82 passed on the final PR head.
- PR #35 merged as commit `18dd594a93ca45f966b79a3b612808751c99c112` after explicit user approval; Issue #34 closed.
- Post-merge Yahoo Live Smoke run `31169043266` succeeded on attempt 1 with 10 trusted SPY daily observations.

## 2026-08-07 — Bounded Retry Executor

- Issue #32 and PR #33 added provider-independent `RetryPolicy`, `RetryExecution`, and `BoundedRetryExecutor`.
- Whole-request retry occurs only when no trusted observations exist and all failures are retryable; partial and deterministic failures stop immediately.
- Python run #26 and Documentation run #74 passed.
- PR #33 merged as commit `db76e2199639b075101c9c7d08e9266c1b5c8116` after explicit user approval; Issue #32 closed.

## 2026-08-07 — Yahoo Live Smoke Validation

- Issue #30 and PR #31 added manual Yahoo Live Smoke validation with bounded recent SPY requests and safe summary-only logging.
- Python run #20 and Documentation run #68 passed.
- PR #31 merged as commit `048f1026b64596e44f2caa8ba5160fa3e1426b21`; Issue #30 closed.

## 2026-08-06 — Yahoo Market-Data Adapter

- Issue #28 and PR #29 added daily market-price and FX-rate normalization through explicit Yahoo bindings.
- Adjusted close becomes canonical value; OHLCV and provider metadata are preserved.
- Python run #14 and Documentation run #62 passed before merge.
- PR #29 merged as `bc0c706620895063689c96e655317e0060f20ab8`; Issue #28 closed.

## 2026-08-06 — Roadmap and Release History

- Issue #25 and PR #26 established release-oriented `ROADMAP.md`, `RELEASES.md`, and Definition of Done.
- Documentation run #55 passed; PR #26 merged as `d056baa01c2c94d61754117a7599f1e82534f972`.

## 2026-08-06 — FRED Data Platform Work

- PR #20 added the official FRED economic-series adapter and deterministic fixtures; Python run #3 and Documentation run #47 passed.
- PR #22 added protected FRED Live Smoke using `FRED_API_KEY`; Python run #5 and Documentation run #50 passed.
- PR #24 corrected expected weekend/holiday partial-result handling; Python run #7 and Documentation run #52 passed and protected live smoke succeeded.

## 2026-08-06 — Canonical Data Platform and Governance

- PR #16 defined Phase 2 provider-independent design; Documentation run #43 passed.
- PR #18 added canonical data models and provider contracts; Python run #1 and Documentation run #45 passed.
- PR #14 established Project Development Policy v1 after Documentation run #41.

## 2026-08-06 — Phase 1 Closure

- React, TypeScript, Vite, Tailwind CSS, PWA baseline, GitHub Pages, Supabase, and Google OAuth were completed.
- Login persistence and sign-out were manually verified.
- PWA offline validation, package lock, user tables, RLS, and cross-user isolation remain pending.
