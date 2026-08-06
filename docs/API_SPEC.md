# API Specification

## Purpose

Define stable boundaries between the React client, Supabase services, scheduled Python jobs, and external data providers.

## API Principles

- Public contracts expose canonical domain models, never provider payloads.
- Investment-relevant responses include source, observation time, retrieval time, cutoff, quality, and freshness metadata.
- Write operations are authenticated, authorized, idempotent where practical, and auditable.
- Errors use stable machine-readable codes and safe human-readable messages.
- No interface may place or simulate a brokerage order in MVP.

## Internal Provider Interface

Each Phase 2 provider adapter supports a logical contract equivalent to:

```text
identify() -> ProviderDescriptor
validate_request(request) -> ValidationResult
fetch(request) -> ProviderBatch
normalize(batch, context) -> NormalizedBatch
classify_error(error) -> ProviderFailure
```

A `NormalizedBatch` contains canonical observations, rejected records, warnings, source metadata, adapter version, and content identity. Adapters do not publish directly to the UI or analysis engine.

## Canonical Read Models

### Asset

Includes canonical identifier, name, asset class, currency, exchange, timezone, active state, and approved provider aliases.

### Observation

Includes canonical subject, observation period, value fields, unit, currency where applicable, provider, source identifier, retrieval time, revision, quality state, and freshness state.

### Source Snapshot

Includes snapshot identifier, dataset, provider, cutoff, policy version, publication time, row counts, completeness, quality summary, and source list.

### Ingestion Status

Includes run identifier, provider, dataset, adapter version, commit SHA, cutoff, start and end time, state, counts, warnings, and safe failure summaries.

## Response Envelope

Read responses use:

```text
{
  data,
  meta: {
    schema_version,
    generated_at,
    data_cutoff,
    source_snapshot_id,
    sources,
    quality,
    freshness
  },
  errors
}
```

`meta` must not imply current data when the underlying snapshot is stale, partial, or unavailable.

## Logical API Areas

### Instruments and Series

- list approved assets and aliases
- list approved economic series
- expose provider-independent identifiers and metadata

### Market, Macro, and FX Data

- read normalized history within bounded date ranges
- read the latest approved observation or snapshot
- expose source, revision, quality, and freshness
- reject unsupported symbols and unbounded queries

### Operations

- read ingestion health and source status appropriate to the caller
- read the most recent successful and failed run per dataset
- expose stale and partial states without sensitive provider details

### Analysis, Portfolio, and Recommendations

Future contracts consume canonical source snapshots and preserve the snapshot identifier and cutoff used. The client cannot submit arbitrary executable formulas.

## Error Model

Stable categories include:

- `AUTH_REQUIRED`
- `FORBIDDEN`
- `VALIDATION_FAILED`
- `UNSUPPORTED_ASSET`
- `SOURCE_UNAVAILABLE`
- `SOURCE_SCHEMA_CHANGED`
- `STALE_DATA`
- `PARTIAL_DATA`
- `INSUFFICIENT_DATA`
- `RATE_LIMITED`
- `RETRY_EXHAUSTED`
- `INTERNAL_ERROR`

Provider credentials, raw responses, stack traces, and private operational detail are never returned to clients.

## Pagination and Bounds

Historical queries require explicit date bounds and maximum row limits. Pagination order must be deterministic. Server-side or job-side protection prevents accidental full-history retrieval from free providers.

## Versioning

Breaking changes require a documented version transition. Database-generated APIs are wrapped or constrained so internal table changes do not silently alter public contracts.

## Validation

Contract tests cover canonical schemas, unsupported identifiers, pagination, freshness metadata, revisions, duplicate handling, partial provider failures, stale snapshots, idempotency, RLS isolation when user data is introduced, and backward compatibility.
