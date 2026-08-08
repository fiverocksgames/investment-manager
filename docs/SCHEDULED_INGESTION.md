# Scheduled Ingestion and Operational Status

## Purpose

Scheduled ingestion composes existing canonical fetch, cache/retry, immutable snapshot, and persistence boundaries into one explicit operational run. It does not make provider data fresher, more complete, or more trustworthy than the underlying canonical result.

## Job Boundary

Each `IngestionJob` explicitly identifies:

- provider
- canonical `FetchRequest`
- `DatasetPolicy`
- UTC-aware snapshot cutoff
- whether partial publication is allowed

No local timezone is inferred by the orchestration layer. A scheduler is responsible for choosing a timezone-aware execution instant and constructing the job.

## Execution Semantics

1. Start an ingestion run with a unique run ID and UTC-aware start time.
2. Execute the configured fetch boundary. The boundary may internally compose cache and bounded retry.
3. Preserve the returned canonical observations and provider failure evidence.
4. A fully failed fetch publishes nothing.
5. A partial fetch publishes nothing unless the job explicitly allows partial publication.
6. Eligible observations are passed to `SourceSnapshotPublisher` using the explicit cutoff.
7. Only the exact observations selected by the immutable snapshot are passed to `SnapshotRepository`.
8. Persistence must succeed before the run can claim accepted records or expose a persisted snapshot result.
9. Terminal status is `succeeded`, `partial`, or `failed` with explicit counts and failures.

## Partial Results

Partial results remain visible as `partial` even when publication is explicitly allowed. Allowing publication does not upgrade the provider outcome to success. If partial publication is denied, no snapshot or persistence result is produced.

## Failure Boundary

Publication and persistence failures are fail-closed. They produce a failed operational run and do not claim successful persistence. Existing previously published snapshots are not modified.

The orchestration layer does not implement stale-on-error, provider fallback, or retry policy itself. Those remain explicit lower-level execution policies.

## Operational Evidence

`IngestionExecution` exposes:

- terminal canonical `IngestionRun`
- explicit `IngestionFailure` values
- snapshot only when publication succeeded
- persistence result only when persistence succeeded
- cache-hit execution evidence without rewriting provider provenance

Status messages must not contain secrets, raw provider payloads, database credentials, or personal investment information.

## Scheduling

This milestone defines the scheduler-facing job contract, not a distributed scheduling service. GitHub Actions cron, Supabase Cron, or another scheduler can later invoke the same job contract. Schedule definitions must use explicit timezone semantics and must not assume host-local time.

## Deferred Work

- production scheduler/queue deployment
- durable ingestion-run persistence
- alert routing
- provider fallback
- distributed cache
- dataset/snapshot versioning
- UI operational dashboard
