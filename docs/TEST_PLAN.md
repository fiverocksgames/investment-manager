# Test Plan

## Purpose

Define validation for documentation, frontend, data ingestion, normalization, immutable source snapshots, persistence, cache execution, analysis, portfolio calculations, authentication, database policies, and deployment.

## Test Levels

### Documentation

Validate required files, Requirement ID references, internal links, decision records, Markdown rendering, and consistency among specifications, feature matrix, worklog, and handoff.

### Unit Tests

Cover canonical model validation, symbol/series/FX normalization, timestamp conversion, unit and currency mapping, quality classification, freshness thresholds, retry behavior, deterministic snapshot identity, persistence idempotency, cache behavior, and safe error mapping.

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

The committed PostgreSQL migration is reviewed as code but routine CI does not claim that it has been executed against a remote Supabase project. Remote migration application, schema inspection, and service-role connectivity require separate protected evidence.

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

### Integration Tests

Verify provider fixture through normalization, cache execution, source-snapshot publication, persistence, ingestion-run counts, and failure recording. Failed or disallowed partial runs must not publish trusted snapshots, and cache reuse must not rewrite canonical provenance/freshness.

### End-to-End Tests

After implementation, verify scheduled or manually dispatched ingestion produces observable run status and normalized persisted data with source and freshness metadata. No test places an order.

## Required Phase 2 Scenarios

- duplicate provider records and repeated idempotent ingestion
- revised macro observations and corrected market observations
- missing timestamps, units, currencies, and identifiers
- explicit FX direction and inverse normalization
- deterministic source snapshot content identity
- cutoff exclusion and disallowed partial snapshot publication
- immutable same-ID persistence conflict
- transactional snapshot persistence rollback
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

The Phase 2 persistence migration uses PostgreSQL `numeric` for canonical financial values, `timestamptz` for canonical times, UUID primary/foreign keys, ordered snapshot membership, uniqueness constraints, and RLS enabled with no client-facing policies. Remote database validation must verify those constraints after protected migration execution. User-owned table RLS tests remain separately required before portfolio data is exposed.

## Numeric Validation

Financial calculations use documented formulas, golden fixtures, expected results, and explicit tolerances. Phase 2 observations use `Decimal`; FX reciprocal normalization uses a fixed 34-digit Decimal context with `ROUND_HALF_EVEN` and never binary floating point.

## CI Gates

The Phase 2 pipeline progressively includes Python compilation/unit tests, provider contract tests, persistence tests, cache tests, documentation checks, secret scanning, protected migration validation, and frontend verification as applicable.

## Live Smoke Tests

Live provider tests are manually triggered, rate-limited, and do not replace deterministic fixtures. FRED and ECOS live workflows require API keys stored only in GitHub Actions secrets; Yahoo live smoke requires no secret. Logs expose only bounded summary evidence and classified safe failures.

FRED, Yahoo, and ECOS each have at least one verified successful live retrieval run. Those runs are bounded evidence and do not guarantee permanent provider availability.

FX normalization, source snapshot publication, fake-DB persistence, and cache-executor tests have no live network dependency. Remote Supabase migration/application validation is a separate protected operational check, not a provider smoke test.

## Test Evidence

Every PR lists exact automated checks/results, skipped areas, and known limitations. Failed required checks prevent completion unless an explicit risk acceptance is recorded.

## Release Acceptance

Before Phase 2 is complete, provider adapters and canonical normalization must pass contract tests, stale/failure states must remain observable, duplicate writes must be prevented, cache reuse must preserve provenance/freshness without hiding failed refreshes, deterministic source snapshots must make downstream input sets reproducible, persisted immutable identities must be conflict-safe, and failed providers/persistence attempts must not silently produce trusted current snapshots.
