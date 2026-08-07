# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Transactional `SnapshotRepository`, `PersistenceResult`, and `PersistenceError` for immutable canonical observation/snapshot storage
- Initial Supabase/PostgreSQL migration for `data_observations`, `source_snapshots`, and ordered `source_snapshot_observations`
- Deterministic fake-DB persistence tests for atomic write, idempotent replay, immutable conflicts, rollback, exact membership, Decimal values, UTC timestamps, and source metadata
- `docs/PERSISTENCE.md` with transaction, immutability, RLS, secrets, and remote-migration evidence boundaries
- Provider-independent immutable source snapshot publication with `SnapshotPublicationPolicy`, `SnapshotPublicationError`, and `SourceSnapshotPublisher`
- Deterministic SHA-256 snapshot content checksum and UUIDv5 snapshot identity derived from dataset/provider/cutoff/content
- Network-free source snapshot tests for ordering, cutoff filtering, duplicate IDs, provider mismatch, partial policy, empty eligibility, publication timing, and UTC normalization
- `docs/SOURCE_SNAPSHOTS.md` with publication, identity, failure, and persistence boundaries
- Provider-independent canonical FX normalization with explicit `FxPair`, `FxNormalizationBinding`, `FxNormalizationError`, and `FxNormalizer`
- Directional FX units such as `KRW_per_USD`, deterministic direct/inverse normalization, and provider-provenance preservation
- Sanitized ECOS transport diagnostics and deterministic ECOS transport tests
- Bank of Korea ECOS `StatisticSearch` economic-series adapter and protected live smoke workflow
- Explicit Yahoo default HTTP request headers and provider-independent bounded retry executor
- Yahoo daily market-price/FX adapter and official FRED economic-series adapter

### Changed

- Canonical persistence uses PostgreSQL `numeric` for financial values, `timestamptz` for canonical times, UUID identities, and `jsonb` for provider source attributes.
- Immutable persistence uses insert-if-absent plus persisted-content verification: identical replay is idempotent while conflicting same-ID content fails closed.
- Observation rows, snapshot row, and exact ordered snapshot memberships now share one transaction boundary in the persistence repository.
- The initial data-platform migration enables RLS while deliberately defining no client-facing policies; the tables remain server-managed and browser-denied by default.
- Source snapshot publication requires explicit dataset/provider/cutoff boundaries and deterministically orders eligible observations before identity generation.
- Observations after a snapshot cutoff are excluded without rewriting source timestamps, freshness, quality, or provenance.
- `PARTIAL` quality is rejected from snapshots by default and requires an explicit publication policy to allow it.
- FX normalization requires explicit base/quote source direction; ticker text is never used to guess rate direction.
- Reverse FX direction uses a fixed 34-digit `Decimal` reciprocal with `ROUND_HALF_EVEN`; direct direction preserves the source `Decimal` exactly.
- Retry only provider results with no trusted observations and exclusively retryable failures; deterministic snapshot/persistence identity failures are not provider-retry candidates.

### Fixed

- Prevented immutable observation/snapshot identities from being silently overwritten during persistence replay.
- Removed ambiguity from FX canonical units by defining ordered base/quote semantics rather than storing a quote currency label alone.
- Improved ECOS transport observability without logging raw exception strings that could disclose endpoint or credential context.
- Corrected retry-exhaustion evidence so it is tied to the configured maximum attempt budget.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.

### Security

- Data-platform persistence tables have RLS enabled with no browser/client policies in this milestone.
- Database URLs, passwords, service-role credentials, and other database secrets remain runtime-only and are excluded from code, fixtures, logs, and migration files.
- Snapshot identity excludes credentials, raw provider requests, raw payloads, and personal portfolio information.
- FX normalization makes no external calls and does not expose provider credentials or raw payloads.
- ECOS transport diagnostics classify exception types only; raw exception text, API keys, secret-bearing URLs, raw payloads, and observation values remain excluded.
- FRED and ECOS credentials remain encrypted GitHub Actions secrets only.

### Validation

- Persistence initial implementation head `42d2b8414a54dc75930bad3dd233d636c6ce4f5c`: Python run #78 and Documentation run #130 passed.
- The committed persistence migration has not yet been applied to a remote Supabase project; no remote-deployment success is claimed.
- Immutable snapshot final evidence head `541c15d4008e096f600dd1822cd5a14807fec9be`: Python run #76 and Documentation run #128 passed before PR #45 merged as `878f0bb69cf0df70de12898b42ec4f8e25786320`.
- FX final head `61715f6eee0dd763fdb55d4c4ab1fbdf44780046`: Python run #63 and Documentation run #115 passed before PR #43 merged as `da322d96ef4905712b511139e5bbb1ea9da1b575`.
- ECOS Live Smoke run `31182329368` succeeded with 99 trusted observations on attempt 1; Yahoo Live Smoke run `31169043266` succeeded with 10 trusted SPY observations on attempt 1; protected FRED live connectivity is verified.

### Known Limitations

- The persistence migration is source-controlled but not yet remotely applied or live-validated against Supabase.
- No mandatory PostgreSQL driver dependency or protected database connectivity workflow exists yet.
- Ingestion-run persistence, cache execution, scheduled ingestion, and dataset/snapshot versioning remain future work.
- Snapshot publication/persistence does not perform provider fallback or cross-provider merging.
- FX normalization does not implement cross-provider fallback, averaging, triangulation, fixing-time reconciliation, or bid/ask spread handling.
- ECOS and Yahoo live success are bounded evidence from specific runs and do not guarantee future provider availability.
- No user-owned portfolio tables, user RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
