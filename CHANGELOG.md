# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Bank of Korea ECOS `StatisticSearch` economic-series adapter with explicit bindings, `Decimal` values, UTC timestamps, deterministic identifiers, and source metadata
- Deterministic ECOS fixture tests for valid, missing, malformed, range, authentication, HTTP, and cycle behavior
- Manual secret-based ECOS Live Smoke workflow using `ECOS_API_KEY` and the common bounded retry executor
- `docs/ECOS_ADAPTER.md` with ECOS normalization, secret handling, failure behavior, and operational boundaries
- Explicit Yahoo default HTTP request headers with a stable project-specific `User-Agent`, JSON `Accept`, and English `Accept-Language`
- Deterministic network-free Yahoo transport request-construction test
- `docs/YAHOO_TRANSPORT.md` with transport and operational boundaries
- Provider-independent bounded retry executor with exponential backoff, jitter, attempt evidence, and deterministic tests
- Yahoo Live Smoke integration with bounded retry and safe retry-exhaustion reporting
- Manual Yahoo Live Smoke workflow for a bounded recent SPY request without secrets
- Yahoo daily market-price and FX-rate adapter with explicit symbol bindings and deterministic fixture tests
- Official FRED Version 1 economic-series adapter and protected live smoke workflow
- Python 3.12 canonical data models, provider contracts, and CI
- React, TypeScript, Vite, Tailwind CSS, PWA, GitHub Pages, Supabase Auth, and Google OAuth baseline

### Changed

- Extend the common provider contract to Bank of Korea economic-series observations through explicit ECOS bindings.
- Normalize ECOS annual, quarterly, monthly, and daily period labels to timezone-aware UTC period-start timestamps while preserving the original source period.
- Keep ECOS API credentials runtime-only and route retries through the common executor rather than adapter-specific loops.
- Yahoo default transport builds an explicit GET `Request` while preserving the injected transport contract used by fixture tests.
- Retry only provider results with no trusted observations and exclusively retryable failures; partial and deterministic failures stop immediately.
- Treat Yahoo as a best-effort public chart endpoint requiring controlled live validation.
- Require canonical financial values to use `Decimal` and timezone-aware UTC datetimes.
- Require failed, partial, invalid, missing, and unavailable provider outcomes to remain explicit.
- Standardize development as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close.

### Fixed

- Corrected retry-exhaustion evidence so it is tied to the configured maximum attempt budget.
- Corrected the Yahoo smoke test so it preserves the canonical `FetchResult` invariant while validating a no-observation outcome.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.
- Corrected Yahoo fixture date ranges and FX metadata after strict range validation exposed inconsistent fixtures.

### Security

- ECOS live smoke reads `ECOS_API_KEY` only from GitHub Actions secrets and does not log the key, secret-bearing URL, raw payload, or observation values.
- Yahoo transport hardening does not add cookies, Yahoo credentials, crumb tokens, authenticated sessions, proxying, IP rotation, CAPTCHA bypass, or HTML scraping.
- Retry execution does not log raw provider payloads, full request URLs, credentials, or personal investment data.
- FRED credentials remain encrypted GitHub Actions secrets only.

### Validation

- ECOS initial implementation head `3b39f64343bab411bb1f8c6ba8fa1170670d022b`: Python run #34 and Documentation run #84 passed.
- ECOS documentation-complete head `349c12d1671dea4a5504ca82f10e4a10a624bca0`: Python run #40 and Documentation run #90 passed; fresh CI is required after final evidence-document updates.
- ECOS live connectivity is not yet claimed because the manual workflow has not yet run from merged `main` with `ECOS_API_KEY` configured.
- Yahoo Live Smoke run `31169043266` succeeded on merged header-hardening commit `18dd594a93ca45f966b79a3b612808751c99c112`, returning 10 trusted SPY daily observations on attempt 1.
- Earlier Yahoo runs `31141445027` and `31150601290` safely exposed `HTTP_429`, including bounded retry exhaustion in the latter.
- Yahoo header-hardening Python run #32 and Documentation run #82 passed before PR #35 merged.
- Bounded retry executor Python run #26 and Documentation run #74 passed before PR #33 merged.
- Protected FRED live connectivity was successfully validated against the official endpoint.
- Prior frontend, documentation, Python, authentication, and deployment validations remain recorded in merged PR history.

### Known Limitations

- ECOS support is initially limited to `StatisticSearch`, `economic_series`, cycles `A`, `Q`, `M`, and `D`, and a single configured response page per bound series.
- ECOS live connectivity remains unverified until an actual post-merge smoke run succeeds.
- Yahoo live success is bounded evidence from a specific run and does not guarantee future provider availability.
- Identifier-scoped retry, `Retry-After` handling, fallback providers, cache, immutable snapshot integration, persistence, migration, scheduled ingestion, and dataset versioning remain future work.
- No user-owned database tables, RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
