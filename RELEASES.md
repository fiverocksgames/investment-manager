# Release History

This document provides a curated product-level history. `CHANGELOG.md` remains the detailed record of notable changes, while this file summarizes release intent and verified capabilities.

## Unreleased — Release 0.2 Data Platform

### Added

- Provider-independent canonical data models
- Provider capability, request, result, and protocol contracts
- Python 3.12 package and CI baseline
- Official FRED Version 1 economic-series adapter
- Protected repository-secret handling for `FRED_API_KEY`
- Manual live FRED smoke workflow
- Deterministic fixture-based provider tests

### Changed

- Provider failures, partial results, missing values, and stale states remain explicit instead of silently becoming trusted observations.
- Canonical financial values use `Decimal` and timezone-aware UTC datetimes.
- Live smoke validation tolerates only expected `DGS10` missing-value and date-boundary warnings when valid observations are present.

### Fixed

- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and timestamp-boundary normalization.

### Security

- FRED credentials exist only as encrypted GitHub Actions secrets.
- Credentials, raw secret-bearing URLs, and live payloads are excluded from logs and artifacts.

### Validation

- FRED adapter Python and Documentation CI passed.
- Protected FRED live connectivity was successfully validated against the official endpoint.

### Remaining Before 0.2 Completion

- Yahoo market-data adapter
- ECOS adapter
- FX normalization
- Cache and bounded retry executors
- Immutable snapshot integration
- Scheduled ingestion and operational status reporting
- Dataset and snapshot versioning

## Release 0.1 — Application Foundation

### Added

- React, TypeScript, Vite, and Tailwind CSS frontend baseline
- PWA manifest and service-worker baseline
- GitHub Pages deployment
- Supabase integration
- Google OAuth authentication
- Session persistence and sign-out behavior
- Repository governance, documentation CI, Issue templates, and pull-request process

### Security

- Public frontend configuration is separated from privileged credentials.
- Secrets are excluded from the repository and frontend bundles.

### Validation

- GitHub Pages deployment succeeded.
- Google OAuth callback, session persistence, and sign-out were manually verified.

### Known Limitations

- Browser-level PWA installation and offline behavior remain unverified.
- User-owned tables, RLS policies, and cross-user isolation tests remain pending.
- The frontend dependency lockfile is not yet committed.

## Planned Releases

### Release 0.3 — Portfolio Engine

Google Sheets import, holdings normalization, portfolio snapshots, allocation comparison, and explainable rebalancing suggestions.

### Release 0.4 — Strategy and Analysis Engine

Daily and weekly indicators, RSI, MACD, momentum, volatility, market regimes, and conservative allocation logic.

### Release 0.5 — Backtest and Reporting

Backtesting, benchmark comparison, risk reporting, scheduled summaries, and Telegram notifications.

### Release 1.0 — Stable Investment Manager

Stable provider contracts, reproducible portfolio and strategy outputs, documented operations, and decision support without automated trade execution.
