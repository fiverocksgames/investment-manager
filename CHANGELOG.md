# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Sanitized ECOS transport diagnostics (`timeout`, `dns`, `tls`, `connection`, `transport`) while preserving canonical `TRANSPORT_ERROR` behavior
- Deterministic ECOS tests for timeout, DNS, TLS, and connection-reset transport classification
- Bank of Korea ECOS `StatisticSearch` economic-series adapter with explicit bindings, `Decimal` values, UTC timestamps, deterministic identifiers, and source metadata
- Deterministic ECOS fixture tests for valid, missing, malformed, range, authentication, HTTP, and cycle behavior
- Manual secret-based ECOS Live Smoke workflow using `ECOS_API_KEY` and the common bounded retry executor
- `docs/ECOS_ADAPTER.md` with ECOS normalization, secret handling, failure behavior, and operational boundaries
- Explicit Yahoo default HTTP request headers with a stable project-specific `User-Agent`, JSON `Accept`, and English `Accept-Language`
- Provider-independent bounded retry executor with exponential backoff, jitter, attempt evidence, and deterministic tests
- Yahoo daily market-price and FX-rate adapter with explicit symbol bindings and deterministic fixture tests
- Official FRED Version 1 economic-series adapter and protected live smoke workflow
- Python 3.12 canonical data models, provider contracts, and CI
- React, TypeScript, Vite, Tailwind CSS, PWA, GitHub Pages, Supabase Auth, and Google OAuth baseline

### Changed

- ECOS Live Smoke now emits only sanitized transport-detail categories when canonical transport failures occur.
- Extend the common provider contract to Bank of Korea economic-series observations through explicit ECOS bindings.
- Normalize ECOS annual, quarterly, monthly, and daily period labels to timezone-aware UTC period-start timestamps while preserving the original source period.
- Keep ECOS API credentials runtime-only and route retries through the common executor rather than adapter-specific loops.
- Yahoo default transport builds an explicit GET `Request` while preserving the injected transport contract used by fixture tests.
- Retry only provider results with no trusted observations and exclusively retryable failures; partial and deterministic failures stop immediately.
- Require canonical financial values to use `Decimal` and timezone-aware UTC datetimes.
- Require failed, partial, invalid, missing, and unavailable provider outcomes to remain explicit.

### Fixed

- Improved ECOS transport observability without logging raw exception strings that could disclose endpoint or credential context.
- Corrected retry-exhaustion evidence so it is tied to the configured maximum attempt budget.
- Corrected the Yahoo smoke test so it preserves the canonical `FetchResult` invariant while validating a no-observation outcome.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.
- Corrected Yahoo fixture date ranges and FX metadata after strict range validation exposed inconsistent fixtures.

### Security

- ECOS transport diagnostics classify exception types only; raw exception text, API keys, secret-bearing URLs, raw payloads, and observation values remain excluded.
- ECOS live smoke reads `ECOS_API_KEY` only from GitHub Actions secrets.
- Retry execution does not log raw provider payloads, full request URLs, credentials, or personal investment data.
- FRED credentials remain encrypted GitHub Actions secrets only.

### Validation

- ECOS Live Smoke run `31182329368` succeeded on merged `main` commit `23bd2ef88ce7ab3f3da2f288ad066089c163f2e8`: 99 trusted `bok_base_rate_daily` observations on attempt 1, range `2026-02-09T00:00:00+00:00` through `2026-05-18T00:00:00+00:00`, unit `percent_per_annum`, cycle `D`; `OUT_OF_RANGE` was tolerated as a warning. This is bounded live-success evidence, not an availability guarantee.
- ECOS Live Smoke run `31174803601` failed safely with `MISSING_SECRET` before any provider attempt.
- ECOS Live Smoke run `31180017610` received `ECOS_API_KEY` correctly but exhausted three bounded attempts with `TRANSPORT_ERROR`.
- ECOS transport-diagnostic implementation head `b579523ba5e6989127588b7c5f6197fcd9d85db1`: Python run #46 and Documentation run #96 passed.
- ECOS transport-diagnostic final changelog-evidence head `d9bed23781defaa1b389af93fdcf454e7f5fe058`: Python run #49 and Documentation run #99 passed before PR #39 merged as `23bd2ef88ce7ab3f3da2f288ad066089c163f2e8`.
- ECOS adapter final pre-merge head `674eacc0d6254cc7c94b436bf4d35203e1c8fecb`: Python run #44 and Documentation run #94 passed; PR #37 later merged as `0f3106bb8772317679df52e76717c6e9ddfebe94`.
- Yahoo Live Smoke run `31169043266` succeeded with 10 trusted SPY daily observations on attempt 1.
- Earlier Yahoo runs `31141445027` and `31150601290` safely exposed `HTTP_429`, including bounded retry exhaustion in the latter.
- Protected FRED live connectivity was successfully validated against the official endpoint.
- FRED, Yahoo, and ECOS each now have verified successful live retrieval evidence.

### Known Limitations

- ECOS live success is bounded evidence from a specific run and does not guarantee future provider availability.
- ECOS support is initially limited to `StatisticSearch`, `economic_series`, cycles `A`, `Q`, `M`, and `D`, and a single configured response page per bound series.
- Sanitized transport categories improve diagnosis but do not expose low-level endpoint details by design.
- Yahoo live success is bounded evidence from a specific run and does not guarantee future provider availability.
- Identifier-scoped retry, `Retry-After` handling, fallback providers, cache, immutable snapshot integration, persistence, migration, scheduled ingestion, and dataset versioning remain future work.
- No user-owned database tables, RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
