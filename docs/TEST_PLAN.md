# Test Plan

## Purpose

Define validation for documentation, frontend, data ingestion, analysis, portfolio calculations, authentication, database policies, and deployment.

## Test Levels

### Documentation

Validate required files, Requirement ID references, internal links, decision records, Markdown rendering, and consistency among specifications, feature matrix, worklog, and handoff.

### Unit Tests

Cover canonical model validation, symbol and series normalization, timestamp conversion, unit and currency mapping, quality classification, freshness thresholds, cache expiry, retry classification, retry bounds, backoff, jitter, idempotency keys, and safe error mapping.

### Provider Contract Tests

Each adapter uses recorded or synthetic fixtures to verify:

- request bounds
- expected schema parsing
- missing and renamed fields
- provider error mapping
- rate-limit handling
- timezone and calendar behavior
- revisions and corrections where supported
- unsupported identifiers
- normalization into canonical batches

Routine CI must not depend on live provider availability.

ECOS fixture coverage additionally verifies explicit statistic/item/cycle bindings, authentication failure classification, ECOS `TIME` normalization for supported cycles, source-unit preservation, missing-value handling, and rejection of out-of-range or malformed periods. Fixtures never contain a real `ECOS_API_KEY`.

### Retry Executor Tests

The common retry executor uses injected sleepers and jitter sources so unit tests do not wait or depend on randomness. Required scenarios include:

- direct success without retry
- retryable failure followed by recovery
- retry exhaustion at the configured bound
- non-retryable failure stopping immediately
- partial results stopping immediately
- invalid retry-policy bounds

Whole-request retry is intentionally not used for partial results until identifier-scoped ingestion orchestration exists.

### Integration Tests

Verify provider fixture through normalization, persistence, ingestion-run counts, source-snapshot publication, cache behavior, and failure recording. Tests confirm failed or disallowed partial runs do not publish trusted snapshots.

### End-to-End Tests

After implementation, verify scheduled or manually dispatched ingestion produces observable run status and normalized data with source and freshness metadata. No test places an order.

## Required Phase 2 Scenarios

- duplicate provider records
- repeated idempotent ingestion
- revised macro observations
- corrected market observations
- missing timestamps, units, currencies, and identifiers
- daylight-saving and exchange-timezone boundaries
- market holidays and publication delays
- stale and hard-expired datasets
- allowed and disallowed partial datasets
- cache hit, miss, expiry, and invalidation
- transient timeout and bounded retry success
- retry exhaustion
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

Financial calculations use documented formulas, golden fixtures, expected results, and explicit tolerances. Phase 2 observations use decimal-safe representations and do not rely on exact binary floating-point equality.

## CI Gates

The Phase 2 implementation pipeline will progressively add Python formatting, linting, type checking, unit tests, provider contract tests, migration validation, documentation checks, secret scanning, and frontend build verification.

## Live Smoke Tests

Live provider tests are optional, manually triggered, rate-limited, and non-blocking unless specifically designated for release validation. They verify current access and schema without replacing deterministic fixture tests. Retry exhaustion is recorded as a live failure, not converted into a success claim.

FRED and ECOS live smoke workflows require provider API keys stored only as GitHub Actions secrets. Yahoo live smoke requires no secret. Live logs expose only bounded summary evidence and classified failure codes; secret-bearing URLs, raw payloads, credentials, and observation values are excluded.

ECOS live success requires at least one trusted canonical observation from the representative bound series and no fatal failure after bounded retry. The workflow may tolerate only explicitly documented row-level warnings when trusted observations exist.

## Test Evidence

Every PR lists exact automated checks, commands or workflow runs, results, skipped areas, and known limitations. Failed required checks prevent completion unless an explicit risk acceptance is recorded.

## Release Acceptance

Before Phase 2 implementation is complete, all provider adapters must pass contract tests, normalized schemas must be consistent, stale and failure states must be observable, duplicate writes must be prevented, and a failed provider must not silently produce a trusted current snapshot.
