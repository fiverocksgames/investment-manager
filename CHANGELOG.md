# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

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

- Treat Yahoo as a best-effort public chart endpoint requiring controlled live validation.
- Restrict Yahoo smoke logs to non-sensitive summary metadata and classified failure codes.
- Include the Yahoo smoke workflow in Python CI path filtering.
- Extended the common provider contract from macro data into daily market and FX observations.
- Required explicit provider-symbol bindings rather than inferred canonical identity.
- Required canonical financial values to use `Decimal` and timezone-aware UTC datetimes.
- Required failed, partial, invalid, missing, and unavailable provider outcomes to remain explicit.
- Standardized development as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close.

### Fixed

- Corrected the Yahoo smoke test so it preserves the canonical `FetchResult` invariant while validating a no-observation outcome.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.
- Corrected stale living-document status for completed FRED work.
- Corrected Yahoo fixture date ranges and FX metadata after strict range validation exposed inconsistent fixtures.

### Security

- Yahoo live smoke requires no credential and excludes raw payloads, full URLs, and observation values from logs.
- FRED credentials remain encrypted GitHub Actions secrets only.
- Yahoo adapter requires no committed credential and does not scrape rendered HTML.
- Secret values, raw secret-bearing URLs, and live payloads are excluded from logs and artifacts.

### Validation

- Yahoo live smoke Python run #16 and Documentation run #64 passed on commit `c327b5419674a4f75cc84f0aa616f6b17ef12bda` after fixing the invalid empty-result test from Python run #15.
- Manual Yahoo live validation remains pending until the new workflow exists on the default branch and can be dispatched.
- Yahoo adapter Python run #14 and Documentation run #62 passed before PR #29 merged.
- Protected FRED live connectivity was successfully validated against the official endpoint.
- Prior frontend, documentation, Python, authentication, and deployment validations remain recorded in merged PR history.

### Known Limitations

- Yahoo live connectivity and production availability have not yet been validated by the new workflow.
- Yahoo endpoint and schema stability are not guaranteed; fallback provider strategy remains future work.
- No ECOS adapter, cache executor, retry executor, persistence, migration, or scheduled ingestion exists.
- No user-owned database tables, RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
