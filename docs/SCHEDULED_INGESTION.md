# Scheduled Ingestion and Operational Status

## Purpose

Scheduled ingestion composes canonical fetch, cache/retry, immutable snapshot, persistence, and terminal operational evidence into one explicit run. It does not make provider data fresher, more complete, or more trustworthy than the underlying canonical result.

## Job Boundary

Each `IngestionJob` explicitly identifies:

- provider
- canonical `FetchRequest`
- `DatasetPolicy`
- UTC-aware snapshot cutoff
- whether partial publication is allowed

No local timezone is inferred by the orchestration layer. Scheduler definitions must use explicit UTC semantics.

## Execution Semantics

1. Start an ingestion run with a unique run ID and UTC-aware start time.
2. Execute the configured fetch boundary. The boundary may compose bounded retry and cache behavior.
3. Preserve canonical observations and provider failure evidence.
4. A fully failed fetch publishes nothing.
5. A partial fetch publishes nothing unless the job explicitly allows partial publication.
6. Eligible observations are passed to `SourceSnapshotPublisher` using the explicit cutoff.
7. Only observations selected by the immutable snapshot are passed to `SnapshotRepository`.
8. Snapshot persistence must succeed before accepted records are reported.
9. Terminal status is `succeeded`, `partial`, or `failed` with explicit counts and failure evidence.
10. Terminal operational evidence is persisted separately through `IngestionStatusRepository`.

## Attempt and Cache Evidence

`IngestionFetchExecution` records the number of actual provider attempts independently from canonical run state. Bounded retry reports its consumed attempt count to the orchestration layer. A future true cache hit may record zero provider calls while the canonical `IngestionRun.attempt` contract remains at least one.

Cache/retry execution metadata does not rewrite observation IDs, retrieval timestamps, source metadata, quality, or freshness.

## Partial Results

Partial results remain visible as `partial` even when publication is explicitly allowed. Allowing publication never upgrades the provider outcome to success. If partial publication is denied, no snapshot or persistence result is produced.

## Failure and Secret Boundary

Publication and persistence failures are fail-closed. Existing previously published snapshots are not modified.

Catch-all orchestration failures persist only a sanitized exception type, for example `ingestion execution failed: RuntimeError`. Raw exception text is intentionally excluded because it may contain database hosts, connection strings, credentials, provider URLs, payload fragments, or other sensitive information.

Logs and durable status must never contain secrets, raw provider payloads, database connection strings, or personal investment information.

## Durable Operational Evidence

Migration `202608080003_ingestion_operational_status.sql` defines server-managed tables:

- `ingestion_runs`
- `ingestion_failures`

`IngestionStatusRepository` persists one terminal run and its ordered failures atomically. Identical replay is idempotent. Reusing the same run ID with different immutable content fails closed and rolls back.

The run record includes provider, dataset, UTC start/end times, final status, canonical attempt count, actual provider-attempt count, record counts, cache-hit evidence, and optional snapshot ID. Failure rows contain only sanitized code/message/retryability/time/reference evidence.

RLS is enabled with no client-facing policy. These tables are server-managed in this milestone.

## First Production Schedule

The first source-controlled production workflow is `.github/workflows/scheduled-yahoo-ingestion.yml`.

- Provider/dataset: Yahoo `SPY` daily market prices
- Manual trigger: `workflow_dispatch`
- Schedule: `45 23 * * 1-5`
- Time basis: UTC
- Branch guard: `refs/heads/main` only
- Concurrency: one non-cancelled scheduled Yahoo ingestion run at a time
- Runtime timeout: 10 minutes
- Provider retry budget: 3 attempts
- Request window: previous 10 days through execution time to tolerate weekends and market holidays

The workflow installs the optional PostgreSQL runtime extra and reads the database connection only from the GitHub repository secret `SUPABASE_DB_URL`.

For GitHub-hosted runners, the secret must contain a GitHub-reachable PostgreSQL connection string. A Supabase pooler connection may be required when the direct database endpoint is not reachable from the runner network. The actual value must never be committed or printed.

## Validation State

Source-controlled implementation and deterministic tests are not equivalent to production-live validation.

Production scheduling is considered live-validated only after all of the following are evidenced:

1. PR containing the workflow and migration is merged to `main` after explicit approval.
2. The operational-status migration is actually applied to the target Supabase project.
3. The GitHub repository secret `SUPABASE_DB_URL` is configured.
4. A real `Scheduled Yahoo Ingestion` workflow run on `main` succeeds.
5. The matching `ingestion_runs` row and, when applicable, failure/snapshot linkage are verified without exposing secrets or raw financial payloads.

Until those steps complete, documentation must say the production scheduler is implemented/source-controlled but not live-validated.

## Known Atomicity Boundary

Snapshot persistence and operational-status persistence are separate transactions. If snapshot persistence succeeds and subsequent durable status persistence fails, the workflow fails visibly but the already committed snapshot remains. The next milestone may introduce a stronger cross-record transaction or reconciliation mechanism if operational requirements justify it; this implementation does not pretend the two transactions are atomic together.

## Deferred Work

- additional scheduled providers/datasets
- alert/Telegram routing
- distributed scheduler or queue infrastructure
- provider fallback
- distributed cache
- dataset/snapshot versioning
- UI operational dashboard
