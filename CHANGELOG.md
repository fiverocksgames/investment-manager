# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Python 3.12 package baseline in `pyproject.toml`
- Canonical provider-independent data models in `investment_manager/data/models.py`
- Provider capability, request, result, and protocol contracts in `investment_manager/data/providers.py`
- Deterministic standard-library unit tests for model and provider boundaries
- Python GitHub Actions workflow for installation, compilation, and unit tests
- `docs/DATA_MODEL.md` and Phase 2 architecture, database, API, operations, test, and decision design
- Project Development Policy v1 and canonical-repository governance
- React, TypeScript, Vite, Tailwind CSS, PWA, GitHub Pages, Supabase Auth, and Google OAuth baseline

### Changed

- Moved Phase 2 from design-only into initial implementation
- Required canonical financial values to use `Decimal`
- Required timezone-aware datetimes normalized to UTC at domain boundaries
- Required failed, partial, invalid, and unavailable provider outcomes to remain explicit
- Kept provider payloads isolated behind adapter contracts
- Required immutable source snapshots and explicit freshness metadata
- Standardized development as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close

### Validation

- Documentation run #12 passed project-bootstrap checks
- Frontend run #7 and Documentation run #26 passed before PR #4 merge
- Frontend run #15 and Documentation run #33 passed before PR #6 merge
- Frontend run #18 passed before PR #8 merge
- Project Policy Documentation run #41 passed before PR #14 merge
- Phase 2 design Documentation run #43 passed before PR #16 merge
- Python and Documentation CI for Issue #17 are pending
- GitHub Pages deployment, Google OAuth callback, session persistence, and sign-out were manually verified

### Known Limitations

- No Yahoo Finance, FRED, ECOS, or FX adapter is implemented
- No live network calls, credentials, cache executor, retry executor, persistence, migration, or scheduled ingestion exists
- Provider access methods, terms, identifiers, and rate limits require implementation-time verification
- No user-owned database tables, RLS policies, or cross-user isolation tests exist
- Frontend CI still uses `npm install` because `package-lock.json` is not committed
- Browser-level PWA installation and offline behavior remain unverified
- Portfolio, analysis, and recommendation capabilities are not implemented
