# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Official FRED Version 1 economic-series observations adapter
- Runtime-only FRED API-key validation and injectable HTTPS transport
- Explicit FRED series-to-canonical-subject bindings
- Deterministic FRED observation identifiers and revision metadata
- Fixture-based FRED request, parsing, missing-value, failure, and partial-result tests
- `docs/FRED_ADAPTER.md` with provider contract and security boundaries
- Python 3.12 package baseline and canonical provider-independent data models
- Provider capability, request, result, and protocol contracts
- Python GitHub Actions workflow for compilation and unit tests
- Phase 2 architecture, database, API, operations, test, and decision design
- Project Development Policy v1 and canonical-repository governance
- React, TypeScript, Vite, Tailwind CSS, PWA, GitHub Pages, Supabase Auth, and Google OAuth baseline

### Changed

- Moved Phase 2 from provider abstraction into the first concrete official-data adapter
- Required FRED missing value `.` to remain an explicit failure instead of a numeric observation
- Required canonical financial values to use `Decimal`
- Required timezone-aware datetimes normalized to UTC at domain boundaries
- Required failed, partial, invalid, and unavailable provider outcomes to remain explicit
- Kept provider payloads and credentials isolated behind adapter contracts
- Required immutable source snapshots and explicit freshness metadata
- Standardized development as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close

### Validation

- Documentation run #12 passed project-bootstrap checks
- Frontend run #7 and Documentation run #26 passed before PR #4 merge
- Frontend run #15 and Documentation run #33 passed before PR #6 merge
- Frontend run #18 passed before PR #8 merge
- Project Policy Documentation run #41 passed before PR #14 merge
- Phase 2 design Documentation run #43 passed before PR #16 merge
- Python run #1 and Documentation run #45 passed before PR #18 merge
- Python and Documentation CI for the FRED adapter are pending
- GitHub Pages deployment, Google OAuth callback, session persistence, and sign-out were manually verified

### Known Limitations

- FRED live credentials and network integration have not been configured or validated
- No production FRED series catalog has been approved
- No Yahoo Finance, ECOS, or FX adapter is implemented
- No cache executor, retry executor, persistence, migration, or scheduled ingestion exists
- No user-owned database tables, RLS policies, or cross-user isolation tests exist
- Frontend CI still uses `npm install` because `package-lock.json` is not committed
- Browser-level PWA installation and offline behavior remain unverified
- Portfolio, analysis, and recommendation capabilities are not implemented
