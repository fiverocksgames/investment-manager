# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog, and the project will use semantic versioning once releasable software exists.

## [Unreleased]

### Added

- `docs/DATA_MODEL.md` with provider-independent assets, aliases, series, observations, quality states, freshness states, dataset policies, cache policies, retry policies, ingestion runs, failures, and source snapshots
- Internal provider adapter contract for Yahoo Finance, FRED, ECOS, and approved FX sources
- Immutable source-snapshot publication model
- Versioned freshness, cache, retry, and partial-data policies
- Phase 2 database, API, operations, and test design
- Decision records DEC-009 through DEC-011
- Phase 2 traceability for `REQ-DATA-*`, `REQ-PROVIDER-*`, and `REQ-OPS-002`
- `PROJECT_POLICY.md` as the durable project development-policy document
- Canonical-repository governance and explicit Draft PR, CI, approval, merge, and Issue-close controls
- React, TypeScript, Vite, Tailwind CSS, PWA, GitHub Pages, Supabase Auth, and Google OAuth baseline

### Changed

- Moved the project into Phase 2 Data Platform design
- Defined provider payloads as adapter-internal and canonical observations as downstream contracts
- Required source, observation time, retrieval time, revision, quality, cutoff, and freshness metadata for investment-relevant data
- Required failed runs to preserve prior good data without presenting it as current
- Required analysis to reference immutable source snapshots
- Aligned architecture, data sources, database, API, operations, testing, decisions, feature matrix, worklog, and handoff documents
- Defined `fiverocksgames/investment-manager` as the canonical development repository
- Standardized the workflow as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close
- Clarified that repository documentation, not conversation history, is the single source of truth

### Validation

- Documentation run #12 passed required-document, Markdown lint, and offline link checks
- Frontend run #7 and Documentation run #26 passed before PR #4 merge
- Frontend run #15 and Documentation run #33 passed before PR #6 merge
- Frontend run #18 passed before PR #8 merge
- Project Policy v1 Documentation run #41 passed before PR #14 merge
- GitHub Pages deployment, Google OAuth callback, session persistence, and sign-out were manually verified
- Phase 2 design Documentation CI is pending

### Known Limitations

- Phase 2 provider adapters, Python domain models, scheduled workflows, and database migrations are not implemented
- Current provider access methods, terms, identifiers, and rate limits require implementation-time verification
- No user-owned database tables or Row Level Security policies exist
- Cross-user data isolation has not been tested
- `package-lock.json` is not committed, so frontend CI uses `npm install` rather than `npm ci`
- Browser-level PWA installation and offline behavior still require verification
- Portfolio, analysis, and recommendation capabilities are not implemented
