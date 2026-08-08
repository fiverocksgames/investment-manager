# Test Plan

## Purpose

Define validation for documentation, frontend, data ingestion, normalization, immutable source snapshots, persistence, cache execution, scheduled ingestion, durable operational status, analysis, portfolio calculations, authentication, database policies, and deployment.

## Test Levels

### Documentation

Validate required files, Requirement ID references, internal links, decision records, Markdown rendering, and consistency among specifications, feature matrix, worklog, and handoff.

### Unit Tests

Cover canonical model validation, symbol/series/FX normalization, timestamp conversion, unit and currency mapping, quality classification, freshness thresholds, retry behavior, deterministic snapshot identity, persistence idempotency, cache behavior, scheduled-ingestion orchestration, durable status persistence, and safe error mapping.

### Provider Contract Tests

Each adapter uses recorded or synthetic fixtures to verify request bounds, schema parsing, missing fields, provider error mapping, rate limits, timezone/calendar behavior, revisions where supported, unsupported identifiers, and normalization into canonical batches. Routine CI must not depend on live provider availability.

ECOS fixture coverage additionally verifies explicit statistic/item/cycle bindings, authentication failure classification, supported `TIME` normalization, source-unit preservation, missing-value handling, and rejection of out-of-range or malformed periods. Fixtures never contain a real `ECOS_API_KEY`.

### FX Normalization Tests

FX normalization is deterministic and network-free. Required scenarios include canonical base/quote validation, direct and inverse Decimal normalization, directional units, rejection of invalid rates/non-FX inputs/mismatched subjects/unrelated pairs, deterministic IDs, provenance preservation, and explicit Yahoo `KRW=X` USD/KRW fixture convention. No test may infer FX direction from a ticker string.

### Source Snapshot Publication Tests

Snapshot publication is deterministic and network-free. Required scenarios include same logical eligible observations in different input orders yielding the same checksum/snapshot ID, explicit UTC cutoff filtering, duplicate observation-ID rejection, provider mismatch rejection, partial-quality policy, empty eligible set rejection, publication timestamp validation, UTC normalization, and provenance/freshness preservation.

### Persistence Tests

Persistence tests use an injected deterministic fake DB rather than a remote Supabase project. Required scenarios include:

- snapshot, observations, and ordered memberships committed as one transaction;
- input observations must exactly match snapshot membership before a DB connection is opened;
- identical replay produces no duplicate rows and remains successful;
- existing observation identity with conflicting immutable content fails closed;
- existing snapshot membership conflict fails closed;
- any conflict or write failure rolls back the transaction;
- `Decimal` values remain Decimal-safe at the Python persistence boundary;
- UTC-aware timestamps are preserved;
- source metadata is serialized deterministically as JSON.

The committed PostgreSQL migration is reviewed as code but routine CI does not claim that it has been executed against a remote Supabase project. Remote migration application, schema inspection, and protected connectivity require separate protected evidence.

### Durable Operational Status Tests

`IngestionStatusRepository` uses an injected deterministic fake DB in routine CI. Required scenarios include:

- terminal ingestion run and ordered failures commit atomically within the status transaction;
- identical run/failure replay is idempotent;
- same run ID with conflicting immutable content fails closed and rolls back;
- non-terminal runs are rejected before a connection is opened;
- every persisted failure references the exact run ID;
- persisted failure count exactly matches the terminal execution;
- actual provider-attempt count is preserved separately from cache-hit evidence;
- catch-all orchestration failure messages exclude raw exception strings and secret-like database URLs.

The operational-status migration is source-controlled schema intent until separately applied and inspected on the remote Supabase project.

### Cache Executor Tests

The cache executor is deterministic and network-free through stub providers. Required scenarios include:

- initial miss followed by a hit within `DatasetPolicy.cache_ttl`;
- exact TTL expiry triggering a provider call and successful replacement;
- provider and full-request cache-key isolation;
- partial results never cached;
- failed results never cached;
- expired success never returned as an implicit stale-on-error fallback;
- dataset policy/request mismatch rejected before provider execution;
- timezone-aware cache execution timestamps required;
- provider/result identity mismatch rejected;
- cache hits preserve canonical observation IDs, `retrieved_at`, freshness, quality, values, and source metadata exactly.

Cache timing metadata is validated separately from canonical source freshness. A cache hit must never be treated as evidence that source data was retrieved more recently.

### Retry Executor Tests

The common retry executor uses injected sleepers and jitter sources so unit tests do not wait or depend on randomness. Required scenarios include direct success, retryable recovery, retry exhaustion, non-retryable stop, partial-result stop, and invalid policy bounds.

### Scheduled Workflow Tests

Routine CI validates the production workflow statically without using real credentials or provider/database network calls. Required checks include:

- `workflow_dispatch` exists;
- cron is explicit UTC (`45 23 * * 1-5` for the initial Yahoo SPY job);
- production job is guarded to `refs/heads/main`;
- `SUPABASE_DB_URL` is referenced only through GitHub Actions secrets;
- missing protected secret fails visibly;
- scheduled command invokes the reviewed Python module;
- no literal PostgreSQL connection string is committed in the workflow;
- PostgreSQL driver is an optional runtime dependency rather than a hidden global dependency.

### Integration Tests

Verify provider fixture through normalization, cache/retry execution, source-snapshot publication, persistence, ingestion-run counts, durable failure recording, and attempt evidence. Failed or disallowed partial runs must not publish trusted snapshots, and cache reuse must not rewrite canonical provenance/freshness.

### End-to-End Tests

After merge and protected configuration, verify manually dispatched production ingestion produces a real workflow result, normalized persisted data, immutable source snapshot, and matching durable `ingestion_runs` evidence. No test places an order.

Production-live acceptance requires a real run from `main`; deterministic PR CI cannot substitute for this evidence.

## Required Phase 2 Scenarios

- duplicate provider records and repeated idempotent ingestion
- revised macro observations and corrected market observations
- missing timestamps, units, currencies, and identifiers
- explicit FX direction and inverse normalization
- deterministic source snapshot content identity
- cutoff exclusion and disallowed partial snapshot publication
- immutable same-ID persistence conflict
- transactional snapshot persistence rollback
- durable ingestion-run identical replay and conflicting identity rollback
- sanitized catch-all operational failure with no connection-string leakage
- provider-attempt count propagation through bounded retry
- scheduled workflow missing-secret failure
- market holidays and publication delays
- stale and hard-expired datasets
- allowed and disallowed partial datasets
- cache hit, miss, exact expiry, request/provider isolation, and invalidation
- partial/failed non-caching and no implicit stale-on-error fallback
- transient timeout and bounded retry success/exhaustion
- rate limiting
- authentication and validation failures that must not retry
- provider schema change
- prior good snapshot preserved after failure

## Golden Fixtures

Fixtures include known source payloads, canonical expected records, rejected rows, warnings, quality states, and content identities. Fixtures are versioned with adapter behavior and contain no secrets or personal data.

## Database Validation

The Phase 2 persistence migrations use PostgreSQL `numeric` for canonical financial values, `timestamptz` for canonical times, UUID primary/foreign keys, ordered snapshot membership, uniqueness constraints, and RLS enabled with no client-facing policies. Operational-status tables additionally persist sanitized terminal run/failure evidence and optional snapshot linkage. Remote database validation must verify those constraints after protected migration execution. User-owned table RLS tests remain separately required before portfolio data is exposed.

## Numeric Validation

Financial calculations use documented formulas, golden fixtures, expected results, and explicit tolerances. Phase 2 observations use `Decimal`; FX reciprocal normalization uses a fixed 34-digit Decimal context with `ROUND_HALF_EVEN` and never binary floating point.

## CI Gates

The Phase 2 pipeline progressively includes Python compilation/unit tests, provider contract tests, persistence tests, cache tests, scheduled-ingestion/status tests, documentation checks, secret scanning, protected migration validation, and frontend verification as applicable.

## Live Smoke and Production Tests

Live provider tests are manually triggered, rate-limited, and do not replace deterministic fixtures. FRED and ECOS live workflows require API keys stored only in GitHub Actions secrets; Yahoo provider live smoke requires no provider secret. Logs expose only bounded summary evidence and classified safe failures.

FRED, Yahoo, and ECOS each have at least one verified successful live retrieval run. Those runs are bounded provider evidence and do not prove the new scheduled persistence workflow.

The production Yahoo scheduled-ingestion workflow additionally requires the protected `SUPABASE_DB_URL` secret and remotely applied operational-status migration. A real workflow success plus matching durable database evidence is required before production scheduling is called live-validated.

## Test Evidence

Every PR lists exact automated checks/results, skipped areas, and known limitations. Failed required checks prevent completion unless an explicit risk acceptance is recorded.

## Release Acceptance

Before Phase 2 is complete, provider adapters and canonical normalization must pass contract tests, stale/failure states must remain observable, duplicate writes must be prevented, cache reuse must preserve provenance/freshness without hiding failed refreshes, deterministic source snapshots must make downstream input sets reproducible, persisted immutable identities must be conflict-safe, scheduled workflows must fail safely, durable run evidence must be sanitized and idempotent, and failed providers/persistence attempts must not silently produce trusted current snapshots.
