# Operations Specification

## Purpose

Define how Investment Manager is built, deployed, scheduled, monitored, recovered, and handed over between maintainers.

## Environments

Use separate local, preview, and production configurations. Production data and credentials must not be used in local development. Environment-specific values are documented without exposing secrets.

## Deployment

The React PWA is built by GitHub Actions and deployed to GitHub Pages. Build failures block deployment. Rollback uses a previously verified commit or artifact.

## Phase 2 Scheduled Jobs

Python ingestion jobs run through GitHub Actions. Every production workflow uses explicit UTC scheduling, protected runtime credentials, bounded execution time, and non-overlapping concurrency policy.

The first source-controlled production schedule is Yahoo `SPY` daily ingestion:

- workflow: `.github/workflows/scheduled-yahoo-ingestion.yml`
- cron: `45 23 * * 1-5` (UTC)
- manual trigger: `workflow_dispatch`
- branch guard: `main` only
- timeout: 10 minutes
- database credential source: GitHub repository secret `SUPABASE_DB_URL`

A committed workflow is not live-success evidence. Production success requires the corresponding remote database migration, configured secret, a real successful workflow run, and verified durable run evidence.

## Concurrency and Idempotency

- Only one active scheduled Yahoo run is allowed by the workflow concurrency group.
- Re-running the same immutable observation/snapshot content must not create duplicates.
- Durable ingestion operational records use immutable run identity; identical replay is idempotent and conflicting content fails closed.
- Dataset-version replay for the same dataset/as-of/member content is idempotent and cannot overwrite conflicting immutable content.
- A run may resume or restart only through a documented idempotent path.
- Analysis jobs depend on explicit published snapshot/dataset-version identity rather than an in-progress ingestion run or mutable latest state.

## Source Snapshot Publication

Normalized observations are published through `SourceSnapshotPublisher` before downstream analysis may use them as a reproducible source set.

- A snapshot has one explicit dataset, one provider, and one UTC cutoff.
- Observations after the cutoff are excluded; their timestamps and provenance are never rewritten.
- Duplicate observation IDs and provider mismatches fail closed.
- `PARTIAL` quality is rejected by default and requires explicit dataset-policy opt-in.
- Eligible observations are deterministically ordered before checksum generation.
- Snapshot checksum is SHA-256 over stable canonical content and source provenance.
- Snapshot UUID is deterministic from dataset, provider, cutoff, and checksum.
- Empty eligible sets never publish.
- Publication timing is explicit and cannot precede the cutoff.
- Publication validation errors are deterministic policy failures and are not provider-retry candidates.

## Persistence and Transactional Publication

`SnapshotRepository` persists the exact canonical observations, immutable source snapshot, and ordered membership in one database transaction.

- Input observation IDs must exactly match the snapshot before opening a database connection.
- Canonical financial values are persisted as PostgreSQL `numeric`; canonical times use `timestamptz`; source metadata uses `jsonb`.
- Insert-if-absent semantics are followed by persisted-content verification.
- Replaying identical immutable content is idempotent and creates no duplicates.
- Reusing an observation, snapshot, or membership identity for different immutable content fails closed.
- Any SQL, validation, or identity conflict rolls back the complete transaction.
- RLS is enabled on the Phase 2 persistence tables, with no client-facing policies in this milestone.
- Database URLs, passwords, service-role credentials, and other secrets are runtime-only and must never be logged or committed.

Remote migration execution, schema inspection, and protected connectivity are evidence separate from committed migration files.

## Dataset Version Publication and Persistence

`DatasetVersionPublisher` creates one reproducible identity for one logical dataset over one or more already-immutable source snapshots.

- Version `as_of` and `created_at` are explicit timezone-aware UTC values.
- All member source snapshots must belong to the same logical dataset.
- Member cutoffs may not exceed version `as_of`.
- Member publication times may not exceed version `created_at`.
- Caller order is ignored; canonical order is provider, cutoff, then snapshot UUID.
- Duplicate snapshot IDs and different snapshots competing for the same provider/cutoff boundary fail closed.
- Version checksum uses stable dataset/as-of/member snapshot identity and checksum metadata only.
- UUIDv5 version identity is deterministic from dataset, `as_of`, and checksum.
- `created_at` remains operational evidence and is not part of content identity.

`DatasetVersionRepository` references source snapshots already persisted in `source_snapshots`. It verifies their immutable dataset/provider/cutoff/publication/checksum content before inserting a version. `dataset_versions` and ordered `dataset_version_snapshots` membership commit in one transaction. Identical replay is accepted; version-content or membership conflicts roll back and are never overwritten.

The migration `202608080005_dataset_versioning.sql` is committed schema intent only until the PR is explicitly approved/merged and the migration is separately applied and inspected remotely. Do not claim remote deployment before that evidence exists.

The versioning tables are server-managed with RLS enabled and no browser/client policies. A cross-dataset analysis-input manifest is not part of this layer.

## Durable Ingestion Status

Migration `202608080003_ingestion_operational_status.sql` adds server-managed `ingestion_runs` and `ingestion_failures` tables. `IngestionStatusRepository` persists terminal run evidence atomically within that status transaction.

Durable run evidence includes provider, dataset, UTC start/end times, final status, canonical attempt count, actual provider-attempt count, received/accepted counts, cache-hit evidence, and optional snapshot ID. Ordered failure evidence contains only sanitized code/message/retryability/time/provider-reference fields.

Raw exception strings are not accepted as catch-all operational messages because they may contain connection strings, credentials, hosts, URLs, or payload fragments. Catch-all orchestration failures record the exception type only.

Snapshot persistence and durable run-status persistence are currently separate transactions. If the snapshot commit succeeds but status persistence subsequently fails, the workflow must fail visibly; the already committed immutable snapshot is not rolled back or falsely marked as absent. Reconciliation/stronger cross-record atomicity remains a separate design decision.

## Timeouts and Retries

Every provider call and job has an explicit timeout. Retries are bounded, use exponential backoff with jitter, and apply only to retryable categories. Rate-limit responses respect available retry guidance. Deterministic validation, authentication, unsupported-symbol, and schema errors stop immediately.

The common `BoundedRetryExecutor` retries a whole provider request only when there are no trusted observations and every returned failure is marked retryable. Partial results stop immediately because repeating the complete request could repeat successful source work.

Retry policy records the maximum attempt count and applied delays. The scheduled ingestion layer preserves the actual provider-attempt count as separate operational evidence. Retry exhaustion remains a failed result and never becomes a successful snapshot or connectivity claim.

Persistence identity conflicts and deterministic snapshot/dataset-version publication failures are not provider-retry candidates. A transient database transport retry policy requires a separate orchestration decision and must not blindly replay an ambiguous commit outcome.

## Cache Operations

Cache policies are dataset-specific. Cache hits retain source retrieval and expiry metadata. Cache expiry does not automatically trigger stale publication; the dataset policy determines whether stale data can be shown. Cache invalidation occurs on policy change, source revision, identifier correction, or adapter incompatibility.

## Freshness

Each dataset defines expected cadence, market or publication calendar, soft stale threshold, hard stale threshold, partial-data policy, and whether stale reads are allowed. Freshness is calculated during ingestion and again when data is served.

## Observability

Record where available:

- run identifier
- workflow run identifier and commit SHA in GitHub Actions evidence
- provider and dataset
- cutoff / dataset-version `as_of`
- start and end time
- received and accepted counts
- source snapshot identifier when publication succeeds
- dataset version identifier when version publication succeeds
- cache-hit status
- actual provider-attempt count
- final status and safe failure categories

Logs never contain credentials, tokens, database connection strings, full sensitive payloads, or personal holdings. Scheduled job console output is intentionally restricted to safe operational identifiers/counts/status and never prints financial observation values.

## Run States

Canonical ingestion model supports pending/running/succeeded/partial/failed states. Durable scheduled-ingestion storage records terminal `succeeded`, `partial`, or `failed` states only. Only `succeeded`, or `partial` where explicitly allowed, may publish a source snapshot.

## Failure Handling

- Missing `SUPABASE_DB_URL` fails the workflow before runtime installation/execution.
- Provider outages leave prior good data unchanged.
- Failed runs never publish successful snapshots.
- Partial failures are recorded and do not silently become successful runs.
- Snapshot validation failure publishes nothing and leaves prior good snapshots unchanged.
- Snapshot persistence failure must not be reported as published.
- Dataset-version validation/persistence failure produces no trusted version and leaves prior versions unchanged.
- Durable status persistence failure makes the workflow fail visibly.
- Repeated failure opens an operational task or alert rather than retrying indefinitely.
- Prior good data may remain visible only with original timestamp and explicit stale status.

## Manual Recovery

A maintainer may manually dispatch the production ingestion workflow from `main` after confirming provider health, the required migration, and protected database connectivity. Manual recovery must preserve the same fail-closed and durable-status rules as scheduled execution.

Database migration recovery or data correction requires a separately reviewed procedure. Never paste a database URL or credential into an Issue, PR, workflow input, command output, or log.

## Change Management

Every production-affecting change requires an Issue, Requirement IDs, documentation, tests, a Draft PR, successful CI, and explicit approval. Provider schema changes, workflow permissions, schedules, and database migrations receive focused review.

## Service Priorities

Correctness, provenance, and freshness transparency take priority over low latency or high availability. It is preferable to show insufficient or stale data explicitly than to publish an unverified current value or ambiguous dataset version.
