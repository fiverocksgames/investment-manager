# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Deterministic `DatasetVersion`, `DatasetVersionPublisher`, and `DatasetVersionRepository` for one logical dataset over exact immutable source-snapshot membership
- Additive Supabase migration `202608080005_dataset_versioning.sql` for server-managed `dataset_versions` and ordered `dataset_version_snapshots` with RLS enabled and no client-facing policies
- Deterministic dataset-version tests for caller-order independence, UTC boundaries, duplicate/conflict/look-ahead rejection, idempotent replay, immutable persisted-snapshot verification, and transactional rollback
- `docs/DATASET_VERSIONING.md` documenting identity, point-in-time, persistence, and cross-dataset scope boundaries
- Production-scheduling baseline with `.github/workflows/scheduled-yahoo-ingestion.yml`, manual dispatch, weekday UTC cron, `main`-only execution guard, concurrency control, and protected `SUPABASE_DB_URL` secret injection
- Yahoo SPY scheduled-ingestion entrypoint that composes bounded retry, immutable source snapshots, snapshot persistence, and durable operational status persistence
- `IngestionFetchExecution` for explicit provider-attempt evidence without rewriting canonical provider data
- `IngestionStatusRepository`, `OperationalStatusResult`, and `OperationalStatusError` for atomic/idempotent terminal run and ordered failure evidence
- Additive Supabase migration `202608080003_ingestion_operational_status.sql` for server-managed `ingestion_runs` and `ingestion_failures` tables with RLS enabled and no client-facing policies
- Additive Supabase migration `202608080004_ingestion_snapshot_fk_index.sql` covering `ingestion_runs(snapshot_id)`
- Optional `postgres` runtime dependency using psycopg 3 for protected scheduled-job database connectivity
- Deterministic tests for durable run/failure persistence, identical replay, conflicting run rollback, non-terminal rejection, provider-attempt propagation, sanitized secret-like exceptions, database-failure categorization, and scheduled-workflow boundaries
- Provider-independent `IngestionJob`, `IngestionExecution`, and `IngestionOrchestrator` for fail-closed scheduled-ingestion orchestration
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

- Logical dataset versions canonically order member source snapshots by provider/cutoff/UUID and derive SHA-256 + UUIDv5 identity from dataset, `as_of`, and stable snapshot identity/content metadata; operational creation/publication times do not rewrite content identity.
- Dataset-version publication enforces point-in-time boundaries: source cutoff cannot exceed version `as_of`, and source publication cannot occur after version creation.
- Dataset-version persistence now verifies the already-persisted source snapshot's `published_at` along with dataset/provider/cutoff/checksum before a version can reference it.
- Scheduled-ingestion catch-all errors now preserve only the exception type; raw exception strings are excluded from durable operational evidence to avoid leaking connection strings, credentials, URLs, or payload fragments.
- Scheduled Yahoo database-connectivity failures now emit a secret-safe category without printing the raw DSN or exception text.
- Bounded retry attempt counts are propagated separately as actual provider-attempt evidence; a future cache hit may represent zero provider calls while the canonical run attempt contract remains valid.
- Production scheduling is explicitly evidence-gated: committed workflow code is not considered live until the remote migration, GitHub secret, real workflow execution, and durable run row are verified.
- Scheduled Yahoo ingestion initially targets SPY with a bounded 10-day daily window and three provider attempts; no provider fallback or silent stale fallback is enabled.
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

- Removed a duplicate parallel dataset-version implementation/migration/test set from the active branch and retained one canonical `investment_manager/data/versioning.py` path.
- Corrected the dataset-version test suite to use the repository's `unittest discover` CI contract rather than adding an undeclared `pytest` dependency.
- Closed a point-in-time persistence gap by rejecting source-snapshot objects whose persisted `published_at` differs from the immutable database row.
- Added a covering index for `ingestion_runs.snapshot_id`; remote Supabase advisor no longer reports its prior `unindexed_foreign_keys` finding.
- Prevented raw catch-all exception text from becoming durable ingestion failure messages.
- Closed obsolete post-cache reconciliation PR #60 without merge and Issue #59 as superseded by the newer scheduled-ingestion work, preventing stale living documents from regressing `main`.
- Added a covering index for `source_snapshot_observations.observation_id`; remote Supabase advisor no longer reports the prior `unindexed_foreign_keys` finding.
- Prevented immutable observation/snapshot identities from being silently overwritten during persistence replay.
- Removed ambiguity from FX canonical units by defining ordered base/quote semantics rather than storing a quote currency label alone.
- Improved ECOS transport observability without logging raw exception strings that could disclose endpoint or credential context.
- Corrected retry-exhaustion evidence so it is tied to the configured maximum attempt budget.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.

### Security

- Dataset-version tables are server-managed with RLS enabled and no browser/client policies; version identity excludes credentials, raw provider payloads, and personal portfolio data.
- Scheduled ingestion reads PostgreSQL connectivity only from the GitHub Actions `SUPABASE_DB_URL` repository secret, rejects a missing secret, and does not print its value.
- Scheduled-job console output is limited to safe operational identifiers, status, counts, attempt count, and snapshot ID; financial observation values are not logged.
- Durable catch-all failures record exception type only rather than raw exception text.
- `ingestion_runs` and `ingestion_failures` have RLS enabled with no browser/client policies in this milestone.
- Cache execution stores no new credentials or raw provider payloads and does not mutate provider/source metadata.
- Data-platform persistence tables have RLS enabled with no browser/client policies in this milestone.
- Database URLs, passwords, service-role credentials, and other database secrets remain runtime-only and are excluded from code, fixtures, logs, and migration files.
- Snapshot identity excludes credentials, raw provider requests, raw payloads, and personal portfolio information.
- FX normalization makes no external calls and does not expose provider credentials or raw payloads.
- ECOS transport diagnostics classify exception types only; raw exception text, API keys, secret-bearing URLs, raw payloads, and observation values remain excluded.
- FRED and ECOS credentials remain encrypted GitHub Actions secrets only.

### Validation

- Dataset-versioning latest implementation/test head `10ee278428b9536f3cd7d6cc05830da3a7708e9f`: Python run #128 and Documentation run #188 passed. Earlier Python run #127 failed only because the first test revision imported unavailable `pytest`; it was converted to `unittest` and revalidated.
- First verified production scheduled-ingestion success: GitHub Actions run `31257977677` on `main` commit `ad762ed10eebe3b50ef3924e4fd6978a826ab680` completed successfully with `provider=yahoo`, `dataset=market_prices`, `status=succeeded`, `provider_attempts=1`, `records_received=8`, `records_accepted=8`, `run_id=5346037b-2772-4c22-8e04-4d59fad0daf7`, and `snapshot_id=725526a7-a925-54ff-a070-dcc2b92b96fd`.
- Remote Supabase verification confirmed the exact durable `ingestion_runs` row, linked Yahoo snapshot, 8 snapshot-membership rows, and zero `ingestion_failures` rows for that run. This is bounded success evidence, not a future availability guarantee.
- Earlier production runs `31256711191`, `31257558763`, and `31257858229` failed safely before durable run persistence while the protected database connection configuration was being corrected; those failures remain part of operational history.
- PR #68 merged as `ad762ed10eebe3b50ef3924e4fd6978a826ab680`; its `ingestion_runs(snapshot_id)` covering-index migration was applied remotely and the prior FK advisor finding is resolved.
- Production-scheduling initial implementation/test head `e66e7e97b8b7171479a88f7180cf4602ca387fab`: Python run #101 passed.
- Scheduled-ingestion orchestration final head `0e27782c9a794040a8f51346d459ab3b5e1b6435`: Python run #99 and Documentation run #159 passed before PR #62 merged as `6d2805f2c66fb91e61f87e4264c382c1d94895ad`.
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

- Dataset-version migration `202608080005_dataset_versioning.sql` is committed but not remotely applied or validated; deployment must wait for explicit PR merge approval.
- A `DatasetVersion` covers exactly one logical dataset. Cross-dataset analysis-input manifests, provider fallback/reconciliation, retention/deletion, and point-in-time backtest policy remain separate work.
- Snapshot persistence and durable ingestion-status persistence are separate transactions; a snapshot may commit even if subsequent status persistence fails, in which case the workflow fails visibly and reconciliation may be required.
- Production scheduled ingestion is currently verified only for the bounded Yahoo SPY run above; one successful run does not guarantee future provider, database, or GitHub-hosted runner availability.
- Only Yahoo SPY is wired into the initial production schedule; FRED, ECOS, FX and additional market symbols remain manual/live-smoke or unscheduled paths.
- Cache execution is process-local only; no Redis/distributed backend, persistent cache, background refresh, stale-on-error, or provider fallback exists yet.
- Supabase migration history contains a duplicate-name `snapshot_observation_fk_index` entry from repeated idempotent execution; no automatic history repair is implemented.
- RLS-without-policy advisor INFO notices are intentional for the server-managed deny-by-default persistence tables.
- Supabase Auth leaked-password protection remains disabled and requires a separate authentication/security decision.
- Snapshot publication/persistence does not perform provider fallback or cross-provider merging.
- FX normalization does not implement cross-provider fallback, averaging, triangulation, fixing-time reconciliation, or bid/ask spread handling.
- ECOS and Yahoo live success are bounded evidence from specific runs and do not guarantee future provider availability.
- No user-owned portfolio tables, user RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
