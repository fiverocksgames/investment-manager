# Operations Specification

## Purpose

Define how Investment Manager is built, deployed, scheduled, monitored, recovered, and handed over between maintainers.

## Environments

Use separate local, preview, and production configurations. Production data and credentials must not be used in local development. Environment-specific values are documented without exposing secrets.

## Deployment

The React PWA is built by GitHub Actions and deployed to GitHub Pages. Build failures block deployment. Rollback uses a previously verified commit or artifact.

## Phase 2 Scheduled Jobs

Python ingestion jobs run through GitHub Actions. Each workflow invocation must specify provider, dataset, cutoff, and adapter version. Scheduled jobs are initially expected to run daily for market and FX data and according to publication cadence for macroeconomic series; exact schedules are approved per dataset policy.

## Concurrency and Idempotency

- Only one active run per provider and dataset is allowed.
- Re-running the same cutoff and source revision must not create duplicate trusted observations.
- A run may resume or restart only through a documented idempotent path.
- Analysis jobs depend on a published source snapshot rather than an in-progress ingestion run.

## Timeouts and Retries

Every provider call and job has an explicit timeout. Retries are bounded, use exponential backoff with jitter, and apply only to retryable categories. Rate-limit responses respect available retry guidance. Deterministic validation, authentication, unsupported-symbol, and schema errors stop immediately.

The common `BoundedRetryExecutor` retries a whole provider request only when there are no trusted observations and every returned failure is marked retryable. Partial results stop immediately because repeating the complete request could repeat successful source work. Identifier-scoped retry remains a later ingestion-orchestration concern.

Retry policy records the maximum attempt count and applied delays. Delay and jitter dependencies are injectable for deterministic tests. Retry exhaustion remains a failed result and never becomes a successful snapshot or connectivity claim.

## Cache Operations

Cache policies are dataset-specific. Cache hits retain source retrieval and expiry metadata. Cache expiry does not automatically trigger stale publication; the dataset policy determines whether stale data can be shown. Cache invalidation occurs on policy change, source revision, identifier correction, or adapter incompatibility.

## Freshness

Each dataset defines expected cadence, market or publication calendar, soft stale threshold, hard stale threshold, partial-data policy, and whether stale reads are allowed. Freshness is calculated during ingestion and again when data is served.

## Observability

Record:

- run identifier
- commit SHA
- workflow run identifier
- provider and adapter version
- dataset and cutoff
- start and end time
- requested, received, normalized, rejected, and published counts
- cache hits and misses
- retry count
- quality and freshness summary
- final status and safe error categories

Logs never contain credentials, tokens, full sensitive payloads, or personal holdings.

## Run States

Canonical ingestion states are `queued`, `running`, `succeeded`, `partial`, `failed`, and `cancelled`. Only `succeeded`, or `partial` where explicitly allowed, may publish a source snapshot.

## Failure Handling

- Provider outages leave prior good data unchanged.
- Failed runs never publish successful snapshots.
- Partial failures are recorded per source identifier.
- Repeated failure opens an operational task or alert rather than retrying indefinitely.
- Required-input failure blocks dependent analysis.
- Prior good data may remain visible only with original timestamp and explicit stale status.

## Manual Recovery

A maintainer may re-run a bounded failed dataset after confirming provider health, credentials, and policy. Manual recovery records the triggering user, reason, cutoff, and resulting workflow run. Data deletion or correction requires a separate reviewed procedure.

## Change Management

Every production-affecting change requires an Issue, Requirement IDs, documentation, tests, a Draft PR, successful CI, and explicit approval. Provider schema changes, workflow permissions, schedules, and database migrations receive focused review.

## Runbooks

Implementation work must add runbooks for provider outage, rate limiting, source schema change, stale data, failed snapshot publication, credential rotation, database recovery, and rollback.

## Service Priorities

Correctness, provenance, and freshness transparency take priority over low latency or high availability. It is preferable to show `insufficient_data` than to publish an unverified current value.
