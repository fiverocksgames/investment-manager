# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Yahoo daily market-price and FX-rate adapter with explicit symbol bindings
- Adjusted-close canonical observations with OHLCV and adjustment metadata
- Deterministic Yahoo fixture tests for valid, missing, malformed, partial, HTTP, market, and FX cases
- `docs/YAHOO_ADAPTER.md` with normalization and operational boundaries
- Release-oriented project roadmap and curated `RELEASES.md`
- Official FRED Version 1 economic-series adapter and protected live smoke workflow
- Python 3.12 canonical data models, provider contracts, and CI
- React, TypeScript, Vite, Tailwind CSS, PWA, GitHub Pages, Supabase Auth, and Google OAuth baseline

### Changed

- Extended the common provider contract from macro data into daily market and FX observations.
- Required explicit provider-symbol bindings rather than inferred canonical identity.
- Required canonical financial values to use `Decimal` and timezone-aware UTC datetimes.
- Required failed, partial, invalid, missing, and unavailable provider outcomes to remain explicit.
- Standardized development as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close.

### Fixed

- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.
- Corrected stale living-document status for completed FRED work.

### Security

- FRED credentials remain encrypted GitHub Actions secrets only.
- Yahoo adapter requires no committed credential and does not scrape rendered HTML.
- Secret values, raw secret-bearing URLs, and live payloads are excluded from logs and artifacts.

### Validation

- Yahoo Python and Documentation CI are pending.
- Protected FRED live connectivity was successfully validated against the official endpoint.
- Prior frontend, documentation, Python, authentication, and deployment validations remain recorded in merged PR history.

### Known Limitations

- Yahoo live connectivity and production availability have not been validated.
- No ECOS adapter, cache executor, retry executor, persistence, migration, or scheduled ingestion exists.
- No user-owned database tables, RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
