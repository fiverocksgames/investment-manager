# Test Plan

## Purpose

Define validation for documentation, frontend, data ingestion, normalization, immutable source snapshots, analysis, portfolio calculations, authentication, database policies, and deployment.

## Test Levels

### Documentation

Validate required files, Requirement ID references, internal links, decision records, Markdown rendering, and consistency among specifications, feature matrix, worklog, and handoff.

### Unit Tests

Cover canonical model validation, symbol/series/FX normalization, timestamp conversion, unit and currency mapping, quality classification, freshness thresholds, retry behavior, deterministic snapshot identity, idempotency keys, and safe error mapping.

### Provider Contract Tests

Each adapter uses recorded or synthetic fixtures to verify request bounds, schema parsing, missing fields, provider error mapping, rate limits, timezone/calendar behavior, revisions where supported, unsupported identifiers, and normalization into canonical batches. Routine CI must not depend on live provider availability.

ECOS fixture coverage additionally verifies explicit statistic/item/cycle bindings, authentication failure classification, supported `TIME` normalization, source-unit preservation, missing-value handling, and rejection of out-of-range or malformed periods. Fixtures never contain a real `ECOS_API_KEY`.

### FX Normalization Tests

FX normalization is deterministic and network-free. Required scenarios include canonical base/quote validation, direct and inverse Decimal normalization, directional units, rejection of invalid rates/non-FX inputs/mismatched subjects/unrelated pairs, deterministic IDs, provenance preservation, and explicit Yahoo `KRW=X` USD/KRW fixture convention. No test may infer FX direction from a ticker string.

### Source Snapshot Publication Tests

Snapshot publication is deterministic and network-free. Required scenarios include:

- same logical eligible observations in different input orders yielding the same checksum and snapshot ID
- explicit UTC cutoff filtering
- duplicate observation-ID rejection
- provider-boundary mismatch rejection
- `PARTIAL` quality rejection by default
- explicit allow-partial policy without quality/freshness promotion
- empty eligible set rejection
- publication timestamp validation
- timezone-aware input normalization to UTC
- provenance/freshness preservation on source observations

Database transaction behavior is deferred until persistence is implemented.

### Retry Executor Tests

The common retry executor uses injected sleepers and jitter sources so unit tests do not wait or depend on randomness. Required scenarios include direct success, retryable recovery, retry exhaustion, non-retryable stop, partial-result stop, and invalid policy bounds.

### Integration Tests

Verify provider fixture through normalization, persistence, ingestion-run counts, source-snapshot publication, cache behavior, and failure recording. Failed or disallowed partial runs must not publish trusted snapshots.

### End-to-End Tests

After implementation, verify scheduled or manually dispatched ingestion produces observable run status and normalized data with source and freshness metadata. No test places an order.

## Required Phase 2 Scenarios

- duplicate provider records and repeated idempotent ingestion
- revised macro observations and corrected market observations
- missing timestamps, units, currencies, and identifiers
- explicit FX direction and inverse normalization
- deterministic source snapshot content identity
- cutoff exclusion and disallowed partial snapshot publication
- market holidays and publication delays
- stale and hard-expired datasets
- allowed and disallowed partial datasets
- cache hit, miss, expiry, and invalidation
- transient timeout and bounded retry success/exhaustion
- rate limiting
- authentication and validation failures that must not retry
- provider schema change
- snapshot transaction failure
- prior good snapshot preserved after failure

## Golden Fixtures

Fixtures include known source payloads, canonical expected records, rejected rows, warnings, quality states, and content identities. Fixtures are versioned with adapter behavior and contain no secrets or personal data.

## Database Validation

Migration tests verify table constraints, numeric precision, uniqueness dimensions, foreign keys, transactional snapshot publication, and server-only access to ingestion metadata. RLS tests are required before any user-owned table is exposed.

## Numeric Validation

Financial calculations use documented formulas, golden fixtures, expected results, and explicit tolerances. Phase 2 observations use `Decimal`; FX reciprocal normalization uses a fixed 34-digit Decimal context with `ROUND_HALF_EVEN` and never binary floating point.

## CI Gates

The Phase 2 pipeline progressively includes Python compilation/unit tests, provider contract tests, documentation checks, secret scanning, migration validation, and frontend verification as applicable.

## Live Smoke Tests

Live provider tests are manually triggered, rate-limited, and do not replace deterministic fixtures. FRED and ECOS live workflows require API keys stored only in GitHub Actions secrets; Yahoo live smoke requires no secret. Logs expose only bounded summary evidence and classified safe failures.

FRED, Yahoo, and ECOS each have at least one verified successful live retrieval run. Those runs are bounded evidence and do not guarantee permanent provider availability.

FX normalization and source snapshot publication have no live network dependency; live source validation remains provider-specific.

## Test Evidence

Every PR lists exact automated checks/results, skipped areas, and known limitations. Failed required checks prevent completion unless an explicit risk acceptance is recorded.

## Release Acceptance

Before Phase 2 is complete, provider adapters and canonical normalization must pass contract tests, stale/failure states must remain observable, duplicate writes must be prevented, deterministic source snapshots must make downstream input sets reproducible, and failed providers must not silently produce trusted current snapshots.
