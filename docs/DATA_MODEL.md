# Data Model

## Purpose

Define the provider-independent domain model for Phase 2 Data Platform. This document is the contract between provider adapters, normalization, persistence, operations, APIs, and later analysis components.

## Design Principles

- Provider payloads never become public domain contracts.
- Observation time, retrieval time, source identity, and quality state are mandatory.
- Missing or stale data is explicit and never silently promoted to current data.
- Raw payload retention is optional and governed by licensing, privacy, and storage policy.
- Canonical identifiers are stable even when provider symbols change.
- Data writes are idempotent for the same canonical key, source, observation time, and revision.
- Downstream analysis consumes only normalized and validated records.
- FX direction is explicit; base/quote semantics are never inferred from ticker text.
- Downstream calculations reference explicit immutable source snapshots and logical dataset versions rather than implicit latest state.

## Canonical Entities

### Asset

Represents an investable instrument or market reference.

Required fields include stable asset identity, canonical symbol, display name, asset type, market, currency, timezone, status, and lifecycle timestamps.

### AssetAlias

Maps provider-specific identifiers to an Asset. Uniqueness must prevent ambiguous active aliases for the same provider symbol.

### EconomicSeries

Represents a macroeconomic or financial time series with stable identity, provider code, display metadata, frequency, unit, seasonal adjustment, publication-zone metadata, revision policy, and status.

### FxPair

Represents an ordered canonical currency pair.

Required fields:

- `pair_id`: stable UUID.
- `base_currency`: three-letter uppercase currency code for the currency being priced.
- `quote_currency`: three-letter uppercase currency code used to express the price.

Canonical FX values are always quote-currency units per one base-currency unit. The canonical unit is `<QUOTE>_per_<BASE>`, for example `KRW_per_USD` for USD/KRW.

Source direction is represented separately from canonical direction. A source may be accepted only when its two configured currencies exactly match the canonical pair in either direct or reversed order. Reversed source rates are normalized with a deterministic fixed-precision `Decimal` reciprocal. Ambiguous or unrelated rates are rejected.

See [`FX_NORMALIZATION.md`](FX_NORMALIZATION.md).

### Provider

Defines a data source boundary with provider identity, provider type, access method, terms reference, timezone/rate-limit metadata, health status, and enabled state.

The initial provider set is Yahoo Finance, FRED, ECOS, and an approved FX source or adapter.

### Observation

Canonical representation of a normalized value.

Required fields include observation identity, subject type/id, metric, observation time, fixed-precision value, unit/currency where applicable, provider identity, retrieval time, revision/vintage metadata, quality, freshness, ingestion run, and schema version.

FX observations use `subject_id` for the canonical `FxPair`, `metric=rate`, and a directional unit such as `KRW_per_USD`.

### DataQualityState

Allowed values include `valid`, `partial`, `estimated`, `revised`, `invalid`, and `unavailable`. Invalid or unavailable records are not eligible for trusted downstream calculations.

### FreshnessState

Allowed values represent current/fresh, aging/stale, expired, and unknown states according to the implemented canonical model and dataset policy. Freshness is evaluated from observation/retrieval metadata and cadence rules; retrieval time alone cannot make an old observation current.

### DatasetPolicy

Defines dataset/provider scope, cadence, freshness thresholds, retry/cache policy references, analysis requirement, and enabled state.

### CachePolicy

Defines TTL, stale-serving policy, refresh strategy, key version, and storage bounds. Cached data must retain original provenance and cannot be rewritten as newly retrieved observations.

### RetryPolicy

Defines maximum attempts, delays, backoff, retryable categories, and jitter. Authentication, schema, validation, and permission failures are not blindly retried.

### IngestionRun

Represents one bounded retrieval and normalization attempt with run/dataset/provider identity, requested range, timestamps, status, counts, cutoff, commit/adapter/schema versions, and warning/error evidence.

### IngestionFailure

Records stable error category, retryability, safe message, optional provider status/reference, and occurrence time without secrets or sensitive payloads.

### SourceSnapshot

Records the exact immutable source set used by a downstream calculation.

Implemented canonical fields include:

- `snapshot_id`: deterministic UUIDv5 identity.
- `dataset`: normalized logical dataset identifier.
- `provider`: one explicit provider boundary.
- `cutoff_at`: timezone-aware UTC data cutoff.
- `published_at`: explicit UTC publication timestamp; never earlier than cutoff.
- `observation_ids`: non-empty unique deterministic ordering of eligible canonical observations.
- `checksum`: lowercase SHA-256 content identity.

`SourceSnapshotPublisher` derives the checksum from stable canonical observation and provenance content, including observation identity, subject/kind, timestamp, exact `Decimal` string value, unit, quality/freshness, source identity, retrieval time, revision, and sorted source attributes. Input iteration order must not change checksum or snapshot ID.

The snapshot ID is deterministic from dataset, provider, cutoff, and checksum. `published_at` is operational publication metadata and is not part of content identity.

Publication is fail-closed: provider mismatches, duplicate observation IDs, disallowed partial quality, invalid timing, or an empty eligible set do not produce a snapshot. Observations after the cutoff are excluded rather than rewritten. Publication never upgrades quality/freshness or changes provider provenance.

See [`SOURCE_SNAPSHOTS.md`](SOURCE_SNAPSHOTS.md).

### DatasetVersion

Records one immutable logical-dataset version assembled from one or more already-published `SourceSnapshot` values.

Implemented fields include:

- `version_id`: deterministic UUIDv5 identity.
- `dataset`: one normalized logical dataset identifier.
- `as_of`: timezone-aware UTC point-in-time boundary.
- `created_at`: UTC operational creation time; never earlier than `as_of` or any member snapshot publication.
- `snapshot_ids`: non-empty unique deterministic ordering of member source snapshots.
- `checksum`: lowercase SHA-256 identity over dataset, `as_of`, and stable member snapshot metadata.

All members must belong to the same logical dataset. A member cutoff may not exceed `as_of`. Different snapshots competing for the same provider/cutoff boundary are rejected rather than silently selected. Caller iteration order does not affect checksum, membership order, or version ID.

`created_at` and member `published_at` remain operational evidence and are excluded from content identity. The persistence layer verifies every referenced source snapshot's immutable persisted dataset/provider/cutoff/publication/checksum evidence before writing the version and ordered membership transactionally.

See [`DATASET_VERSIONING.md`](DATASET_VERSIONING.md).

## Provider Interface Contract

Every provider adapter must describe capabilities, resolve identifiers, fetch bounded observations, preserve provider metadata, normalize canonical observations, classify failures, and report retry hints when available. Adapters must not perform investment analysis, portfolio logic, or UI formatting.

## Normalization Rules

- Convert timestamps to UTC for persistence while preserving source timezone metadata.
- Preserve the original observation period for daily, weekly, monthly, quarterly, and annual data.
- Use canonical ISO currency and unit identifiers.
- Reject non-finite numeric values and malformed timestamps.
- Resolve symbols through active aliases valid for the observation date.
- Do not forward-fill missing observations during ingestion.
- Corporate-action and adjusted-price policies must be versioned and explicit.
- Revisions create a new revision or vintage record rather than silently overwriting history where the source supports vintages.
- FX rates must preserve explicit source base/quote metadata and normalize into one ordered canonical `FxPair` direction.
- FX reciprocal conversion uses `Decimal` only with fixed precision and documented rounding; zero/negative or unrelated rates are rejected.
- Source snapshot publication consumes normalized canonical observations only and applies an explicit cutoff without changing source observations.
- Dataset-version publication consumes immutable source snapshots only and does not copy or rewrite observation/source-snapshot content.

## Idempotency and Uniqueness

A normalized observation is uniquely identified by canonical subject, metric, observation time/period, provider, revision/vintage identity, and schema version where interpretation changed.

Repeated ingestion of the same source data must not create duplicate trusted observations. Repeated publication of the same eligible source content at the same dataset/provider/cutoff produces the same checksum and snapshot identity. Repeated dataset-version publication for the same dataset/as-of/member content produces the same checksum and version identity.

## Fail-Safe Rules

- Provider failure never changes a prior valid observation's retrieval timestamp.
- Partial runs are visible as partial and cannot be reported as complete.
- Required datasets block dependent analysis when invalid, expired, or unavailable.
- Optional datasets may degrade outputs only when the limitation is surfaced.
- Last known good data remains queryable with its original timestamps and stale or expired status.
- Conflicting providers are not silently averaged or merged.
- Ambiguous FX direction is insufficient data, not a guessed conversion.
- Snapshot publication failure produces no new trusted snapshot and does not mutate a prior good snapshot.
- Dataset-version publication/persistence failure produces no trusted version and never overwrites prior immutable versions or memberships.

## Phase 2 Implementation Sequence

1. Canonical types and validation schemas.
2. Provider interface and shared error model.
3. Yahoo Finance adapter.
4. FRED adapter.
5. ECOS adapter.
6. Canonical FX normalization.
7. Immutable source-snapshot publication.
8. Cache services.
9. Persistence and idempotent ingestion integration.
10. Scheduled integration and operational reporting.
11. Dataset and snapshot versioning.

## Deferred Decisions

- Final secondary FX provider selection.
- Raw payload retention periods.
- Provider-specific rate limits and credentials.
- Corporate-action reconciliation across providers.
- FX fixing-time reconciliation, triangulation, spread handling, and fallback priority.
- Cross-dataset analysis-input manifest and required/optional dataset policy.
- Dataset-version retention/deletion and mutable aliases such as `latest`.

These require separate Issues and decision records before implementation.
