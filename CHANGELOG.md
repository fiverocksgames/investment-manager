# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Release-oriented project roadmap and milestone status
- Curated `RELEASES.md` product history
- Project Definition of Done covering Issue, design, implementation, tests, documentation, CI, live validation where applicable, review, explicit approval, merge, and living-document updates
- Official FRED Version 1 economic-series observations adapter
- Runtime-only FRED API-key validation and injectable HTTPS transport
- Explicit FRED series-to-canonical-subject bindings
- Deterministic FRED observation identifiers and revision metadata
- Fixture-based FRED request, parsing, missing-value, failure, and partial-result tests
- Protected manual FRED live smoke workflow
- Python 3.12 package baseline and canonical provider-independent data models
- Provider capability, request, result, and protocol contracts
- Python GitHub Actions workflow for compilation and unit tests
- Phase 2 architecture, database, API, operations, test, and decision design
- Project Development Policy v1 and canonical-repository governance
- React, TypeScript, Vite, Tailwind CSS, PWA, GitHub Pages, Supabase Auth, and Google OAuth baseline

### Changed

- Recorded Release 0.1 as the application foundation and Release 0.2 as the active data-platform release.
- Marked FRED adapter and protected live connectivity validation as complete.
- Required expected `DGS10` missing-value and date-boundary conditions to remain warnings only when valid observations exist.
- Required all authentication, HTTP, transport, payload, binding, parsing, and empty-result failures to remain fatal.
- Required FRED missing value `.` to remain an explicit failure instead of a numeric observation.
- Required canonical financial values to use `Decimal`.
- Required timezone-aware datetimes normalized to UTC at domain boundaries.
- Required failed, partial, invalid, and unavailable provider outcomes to remain explicit.
- Kept provider payloads and credentials isolated behind adapter contracts.
- Required immutable source snapshots and explicit freshness metadata.
- Standardized development as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close.

### Fixed

- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.
- Corrected stale living-document status that still described FRED work as unmerged or unvalidated.

### Security

- FRED API credentials are stored only as encrypted GitHub Actions secrets.
- Secret values, raw secret-bearing URLs, and live payloads are excluded from logs and artifacts.

### Validation

- Documentation run #12 passed project-bootstrap checks.
- Frontend run #7 and Documentation run #26 passed before PR #4 merge.
- Frontend run #15 and Documentation run #33 passed before PR #6 merge.
- Frontend run #18 passed before PR #8 merge.
- Project Policy Documentation run #41 passed before PR #14 merge.
- Phase 2 design Documentation run #43 passed before PR #16 merge.
- Python run #1 and Documentation run #45 passed before PR #18 merge.
- Python run #3 and Documentation run #47 passed before PR #20 merge.
- Python run #5 and Documentation run #50 passed before PR #22 merge.
- Python run #7 and Documentation run #52 passed before PR #24 merge.
- Protected FRED live connectivity was successfully validated against the official endpoint.
- GitHub Pages deployment, Google OAuth callback, session persistence, and sign-out were manually verified.

### Known Limitations

- No production FRED series catalog has been approved.
- No Yahoo Finance, ECOS, or FX adapter is implemented.
- No cache executor, retry executor, persistence, migration, or scheduled ingestion exists.
- No user-owned database tables, RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
