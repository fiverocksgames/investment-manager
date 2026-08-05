# API Specification

## Purpose

Define stable boundaries between the React client, Supabase services, scheduled Python jobs, and external data providers.

## API Principles

- APIs expose normalized domain models, not provider-specific payloads.
- All responses include version and freshness metadata when data affects investment decisions.
- Write operations are authenticated, authorized, idempotent where practical, and auditable.
- Errors use stable machine-readable codes plus safe human-readable messages.
- No endpoint may place or simulate a brokerage order in MVP.

## Logical API Areas

### Session and profile

- Read the authenticated profile and preferences.
- Update reporting currency, timezone, and display settings.
- Read and approve the current investment-policy version.

### Instruments and data

- List supported instruments and metadata.
- Read price history, latest normalized prices, FX rates, and economic series.
- Return source, observation time, retrieval time, adjustment policy, and staleness state.

### Analysis

- Request or read an analysis run for a defined cutoff and model version.
- Read market regime, indicator evidence, candidate scores, limitations, and data-quality flags.
- The client must not submit arbitrary executable formulas.

### Portfolio

- Register portfolio-source metadata and initiate a permitted import.
- Read normalized holdings, valuation, exposures, snapshots, and import errors.
- Create a rebalance analysis from an approved target allocation and policy version.
- Record user acknowledgement without producing execution instructions.

### Operations

- Read ingestion and analysis job health appropriate to the caller.
- Administrative job triggers, when introduced, require privileged server-side authorization and audit logs.

## Response Envelope

Domain responses should include `data`, `meta`, and `errors`. `meta` may contain schema version, model version, policy version, data cutoff, generated time, source list, and staleness indicators.

## Error Model

Example categories: `AUTH_REQUIRED`, `FORBIDDEN`, `VALIDATION_FAILED`, `SOURCE_UNAVAILABLE`, `STALE_DATA`, `INSUFFICIENT_DATA`, `RATE_LIMITED`, and `INTERNAL_ERROR`. Sensitive implementation detail must not be returned to clients.

## Versioning

Breaking contract changes require a documented version transition. Database-generated APIs must be wrapped or constrained so internal schema changes do not silently become public contracts.

## Validation

Contract tests must cover authentication, RLS isolation, schema validation, idempotency, pagination, freshness metadata, unsupported assets, partial provider failures, and backward compatibility.
