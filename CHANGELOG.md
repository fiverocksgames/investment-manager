# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Provider-independent immutable source snapshot publication with `SnapshotPublicationPolicy`, `SnapshotPublicationError`, and `SourceSnapshotPublisher`
- Deterministic SHA-256 snapshot content checksum and UUIDv5 snapshot identity derived from dataset/provider/cutoff/content
- Network-free source snapshot tests for ordering, cutoff filtering, duplicate IDs, provider mismatch, partial policy, empty eligibility, publication timing, and UTC normalization
- `docs/SOURCE_SNAPSHOTS.md` with publication, identity, failure, and deferred persistence boundaries
- Provider-independent canonical FX normalization with explicit `FxPair`, `FxNormalizationBinding`, `FxNormalizationError`, and `FxNormalizer`
- Directional FX units such as `KRW_per_USD`, deterministic direct/inverse normalization, and provider-provenance preservation
- Sanitized ECOS transport diagnostics and deterministic ECOS transport tests
- Bank of Korea ECOS `StatisticSearch` economic-series adapter and protected live smoke workflow
- Explicit Yahoo default HTTP request headers and provider-independent bounded retry executor
- Yahoo daily market-price/FX adapter and official FRED economic-series adapter

### Changed

- Source snapshot publication now requires explicit dataset/provider/cutoff boundaries and deterministically orders eligible observations before identity generation.
- Observations after a snapshot cutoff are excluded without rewriting source timestamps, freshness, quality, or provenance.
- `PARTIAL` quality is rejected from snapshots by default and requires an explicit publication policy to allow it.
- FX normalization requires explicit base/quote source direction; ticker text is never used to guess rate direction.
- Reverse FX direction uses a fixed 34-digit `Decimal` reciprocal with `ROUND_HALF_EVEN`; direct direction preserves the source `Decimal` exactly.
- Retry only provider results with no trusted observations and exclusively retryable failures; deterministic snapshot validation failures are not retry candidates.

### Fixed

- Removed ambiguity from FX canonical units by defining ordered base/quote semantics rather than storing a quote currency label alone.
- Improved ECOS transport observability without logging raw exception strings that could disclose endpoint or credential context.
- Corrected retry-exhaustion evidence so it is tied to the configured maximum attempt budget.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.

### Security

- Snapshot identity excludes credentials, raw provider requests, raw payloads, and personal portfolio information.
- FX normalization makes no external calls and does not expose provider credentials or raw payloads.
- ECOS transport diagnostics classify exception types only; raw exception text, API keys, secret-bearing URLs, raw payloads, and observation values remain excluded.
- FRED and ECOS credentials remain encrypted GitHub Actions secrets only.

### Validation

- Immutable snapshot initial implementation head `e1e6e44fe5e31ae4b6325362782c09c78f94fe7c`: Python run #65 and Documentation run #117 passed.
- Immutable snapshot documentation-complete head `9c9ad4f7e7350fed1bfb68f270e536b94662606e`: Python run #73 and Documentation run #125 passed. PR #45 remains subject to the normal latest-head CI gate after any final evidence-only updates.
- FX final head `61715f6eee0dd763fdb55d4c4ab1fbdf44780046`: Python run #63 and Documentation run #115 passed before PR #43 merged as `da322d96ef4905712b511139e5bbb1ea9da1b575`.
- ECOS Live Smoke run `31182329368` succeeded with 99 trusted observations on attempt 1; Yahoo Live Smoke run `31169043266` succeeded with 10 trusted SPY observations on attempt 1; protected FRED live connectivity is verified.

### Known Limitations

- Source snapshot publication is currently in-memory only; Supabase/database persistence, transactional idempotency, and snapshot query APIs remain future work.
- Snapshot publication does not perform provider fallback, cross-provider merging, cache integration, or scheduling.
- FX normalization does not implement cross-provider fallback, averaging, triangulation, fixing-time reconciliation, bid/ask spread handling, or persistence.
- ECOS and Yahoo live success are bounded evidence from specific runs and do not guarantee future provider availability.
- Identifier-scoped retry, `Retry-After` handling, cache, persistence/migration, scheduled ingestion, and dataset versioning remain future work.
- No user-owned database tables, RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
