# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Provider-independent bounded retry executor with exponential backoff, jitter, attempt evidence, and deterministic tests
- Yahoo Live Smoke integration with bounded retry and safe retry-exhaustion reporting
- Manual Yahoo Live Smoke workflow for a bounded recent SPY request without secrets
- Deterministic Yahoo smoke-result tests for tolerated warnings, rate limiting, payload failures, and no-observation results
- `docs/YAHOO_LIVE_SMOKE.md` with best-effort endpoint and operational boundaries
- Yahoo daily market-price and FX-rate adapter with explicit symbol bindings
- Adjusted-close canonical observations with OHLCV and adjustment metadata
- Deterministic Yahoo fixture tests for valid, missing, malformed, partial, HTTP, market, and FX cases
- `docs/YAHOO_ADAPTER.md` with normalization and operational boundaries
- Release-oriented project roadmap and curated `RELEASES.md`
- Official FRED Version 1 economic-series adapter and protected live smoke workflow
- Python 3.12 canonical data models, provider contracts, and CI
- React, TypeScript, Vite, Tailwind CSS, PWA, GitHub Pages, Supabase Auth, and Google OAuth baseline

### Changed

- Retry only provider results with no trusted observations and exclusively retryable failures; partial and deterministic failures stop immediately.
- Treat Yahoo as a best-effort public chart endpoint requiring controlled live validation.
- Restrict Yahoo smoke logs to non-sensitive summary metadata, classified failure codes, attempt count, and retry-exhaustion state.
- Include the Yahoo smoke workflow in Python CI path filtering.
- Extended the common provider contract from macro data into daily market and FX observations.
- Required explicit provider-symbol bindings rather than inferred canonical identity.
- Required canonical financial values to use `Decimal` and timezone-aware UTC datetimes.
- Required failed, partial, invalid, missing, and unavailable provider outcomes to remain explicit.
- Standardized development as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close.

### Fixed

- Corrected retry-exhaustion evidence so it is tied to the configured maximum attempt budget.
- Corrected the Yahoo smoke test so it preserves the canonical `FetchResult` invariant while validating a no-observation outcome.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.
- Corrected stale living-document status for completed FRED work.
- Corrected Yahoo fixture date ranges and FX metadata after strict range validation exposed inconsistent fixtures.

### Security

- Retry execution does not log raw provider payloads, full request URLs, credentials, or personal investment data.
- Yahoo live smoke requires no credential and excludes raw payloads, full URLs, and observation values from logs.
- FRED credentials remain encrypted GitHub Actions secrets only.
- Yahoo adapter requires no committed credential and does not scrape rendered HTML.
- Secret values, raw secret-bearing URLs, and live payloads are excluded from logs and artifacts.

### Validation

- Bounded retry executor Python run #22 and Documentation run #70 passed on implementation head `bfdfc4cc005565647beeeb754bb104438eaf0ec5`; fresh CI is required after evidence-document updates.
- Yahoo Live Smoke run `31141445027` reached the public endpoint from GitHub Actions and failed safely with `HTTP_429`; this is not live-retrieval success.
- Yahoo live smoke Python run #20 and Documentation run #68 passed before PR #31 merged.
- Yahoo adapter Python run #14 and Documentation run #62 passed before PR #29 merged.
- Protected FRED live connectivity was successfully validated against the official endpoint.
- Prior frontend, documentation, Python, authentication, and deployment validations remain recorded in merged PR history.

### Known Limitations

- Yahoo live data retrieval has not yet succeeded in recorded GitHub-hosted smoke validation.
- Bounded retry cannot guarantee recovery from provider or shared-runner rate limiting.
- Identifier-scoped retry, `Retry-After` handling, fallback providers, ECOS, cache, persistence, migration, and scheduled ingestion remain future work.
- No user-owned database tables, RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
