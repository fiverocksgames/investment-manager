# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Provider-independent `CacheExecutor` and `CacheExecution` for process-local successful-result reuse without rewriting canonical provenance
- Deterministic cache tests for miss/hit, exact expiry, provider/request isolation, partial/failed non-caching, stale-on-error exclusion, UTC validation, and provenance preservation
- `docs/CACHE_EXECUTOR.md` with cache-key, TTL, freshness, failure, and deferred distributed-cache boundaries
- Transactional `SnapshotRepository`, `PersistenceResult`, and `PersistenceError` for immutable canonical observation/snapshot storage
- Initial Supabase/PostgreSQL migration for `data_observations`, `source_snapshots`, and ordered `source_snapshot_observations`
- Additive covering-index migration for `source_snapshot_observations.observation_id`
- Deterministic fake-DB persistence tests for atomic write, idempotent replay, immutable conflicts, rollback, exact membership, Decimal values, UTC timestamps, and source metadata
- `docs/PERSISTENCE.md` with transaction, immutability, RLS, secrets, remote migration, smoke, and advisor-evidence boundaries
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

- Cache reuse is bounded by `DatasetPolicy.cache_ttl`; cache timing metadata remains separate from canonical source freshness and provider provenance.
- Only fully successful `FetchResult` values are cached. Partial/failed results and expired stale-on-error fallback are excluded from the current cache contract.
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

- Added a covering index for `source_snapshot_observations.observation_id`; remote Supabase advisor no longer reports the prior `unindexed_foreign_keys` finding.
- Prevented immutable observation/snapshot identities from being silently overwritten during persistence replay.
- Removed ambiguity from FX canonical units by defining ordered base/quote semantics rather than storing a quote currency label alone.
- Improved ECOS transport observability without logging raw exception strings that could disclose endpoint or credential context.
- Corrected retry-exhaustion evidence so it is tied to the configured maximum attempt budget.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.

### Security

- Cache execution stores no new credentials or raw provider payloads and does not mutate provider/source metadata.
- Data-platform persistence tables have RLS enabled with no browser/client policies in this milestone.
- Database URLs, passwords, service-role credentials, and other database secrets remain runtime-only and are excluded from code, fixtures, logs, and migration files.
- Snapshot identity excludes credentials, raw provider requests, raw payloads, and personal portfolio information.
- FX normalization makes no external calls and does not expose provider credentials or raw payloads.
- ECOS transport diagnostics classify exception types only; raw exception text, API keys, secret-bearing URLs, raw payloads, and observation values remain excluded.
- FRED and ECOS credentials remain encrypted GitHub Actions secrets only.

### Validation

- Cache initial implementation/documentation head `b825dcc4bf2c391becfc700de466b8902f9c7b93`: Python run #87 and Documentation run #146 passed.
- Persistence initial implementation head `42d2b8414a54dc75930bad3dd233d636c6ce4f5c`: Python run #78 and Documentation run #130 passed.
- Persistence final evidence head `e88e59e8c5b86d439bfa7521d8f4e00a36c7314f`: Python run #85 and Documentation run #137 passed before PR #47 merged as `b68388ffbe3b16e00fa51d224f02564ab6bf3c62`.
- Initial persistence migration was applied to Supabase project `xztjjgzpryrfcppqkbdo`; remote schema inspection verified tables, constraints, types, and RLS state.
- Bounded remote persistence smoke inserted temporary observation/snapshot/membership rows, verified idempotent replay and `numeric` value `123.45`, confirmed conflicting same-ID rejection, and cleaned all smoke rows.
- PR #51 merged as `46b209f7c824c3a439ecb26a2fd20559ad8462f9`; its follow-up covering-index migration was applied remotely and the prior `unindexed_foreign_keys` advisor finding is no longer present.
- Supabase migration history currently contains two versions named `snapshot_observation_fk_index`. The migration is idempotent and schema state is correct; the duplicate history entry is documented as an operational-history limitation.
- Immutable snapshot final evidence head `541c15d4008e096f600dd1822cd5a14807fec9be`: Python run #76 and Documentation run #128 passed before PR #45 merged as `878f0bb69cf0df70de12898b42ec4f8e25786320`.
- FX final head `61715f6eee0dd763fdb55d4c4ab1fbdf44780046`: Python run #63 and Documentation run #115 passed before PR #43 merged as `da322d96ef4905712b511139e5bbb1ea9da1b575`.
- ECOS Live Smoke run `31182329368` succeeded with 99 trusted observations on attempt 1; Yahoo Live Smoke run `31169043266` succeeded with 10 trusted SPY observations on attempt 1; protected FRED live connectivity is verified.

### Known Limitations

- Cache execution is process-local only; no Redis/distributed backend, persistent cache, background refresh, stale-on-error, provider fallback, or scheduler integration exists yet.
- No mandatory PostgreSQL driver dependency or protected live Python `SnapshotRepository` connectivity workflow exists yet.
- Supabase migration history contains a duplicate-name `snapshot_observation_fk_index` entry from repeated idempotent execution; no automatic history repair is implemented.
- RLS-without-policy advisor INFO notices are intentional for the server-managed deny-by-default persistence tables.
- Supabase Auth leaked-password protection remains disabled and requires a separate authentication/security decision.
- Ingestion-run persistence, scheduled ingestion, and dataset/snapshot versioning remain future work.
- Snapshot publication/persistence does not perform provider fallback or cross-provider merging.
- FX normalization does not implement cross-provider fallback, averaging, triangulation, fixing-time reconciliation, or bid/ask spread handling.
- ECOS and Yahoo live success are bounded evidence from specific runs and do not guarantee future provider availability.
- No user-owned portfolio tables, user RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
