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

## Canonical Entities

### Asset

Represents an investable instrument or market reference.

Required fields:

- `asset_id`: stable UUID.
- `canonical_symbol`: project-controlled identifier.
- `display_name`: user-facing name.
- `asset_type`: ETF, index, bond, commodity, cryptocurrency, FX pair, or other approved type.
- `market`: canonical exchange or market identifier.
- `currency`: ISO 4217 code where applicable.
- `timezone`: IANA timezone for market observations.
- `status`: active, inactive, or unsupported.
- `created_at`, `updated_at`.

### AssetAlias

Maps provider-specific identifiers to an Asset.

Required fields:

- `asset_id`.
- `provider_id`.
- `provider_symbol`.
- `valid_from`, `valid_to`.
- `metadata`: non-contract provider notes.

Uniqueness must prevent ambiguous active aliases for the same provider symbol.

### EconomicSeries

Represents a macroeconomic or financial time series.

Required fields:

- `series_id`: stable project identifier.
- `provider_id`.
- `provider_series_code`.
- `display_name`.
- `frequency`.
- `unit`.
- `seasonal_adjustment`.
- `timezone` or publication-zone metadata.
- `revision_policy`.
- `status`.

### Provider

Defines a data source boundary.

Required fields:

- `provider_id`.
- `name`.
- `provider_type`: market, macro, FX, portfolio, or reference.
- `access_method`.
- `terms_reference`.
- `default_timezone`.
- `default_rate_limit`.
- `health_status`.
- `enabled`.

The initial provider set is Yahoo Finance, FRED, ECOS, and an approved FX source or adapter.

### Observation

Canonical representation of a normalized value.

Required fields:

- `observation_id`.
- `subject_type`: asset, economic_series, or fx_pair.
- `subject_id`.
- `metric`: close, adjusted_close, volume, rate, index_value, macro_value, or another approved metric.
- `observation_time`.
- `value` using fixed-precision numeric storage.
- `unit`.
- `currency` when relevant.
- `provider_id`.
- `retrieved_at`.
- `revision_id` or vintage metadata when supported.
- `quality_state`.
- `freshness_state`.
- `ingestion_run_id`.
- `schema_version`.

Optional market fields may include open, high, low, close, adjusted close, and volume in a typed market-price record derived from the canonical observation contract.

### DataQualityState

Allowed values:

- `valid`.
- `partial`.
- `estimated`.
- `revised`.
- `invalid`.
- `unavailable`.

Invalid or unavailable records are not eligible for trusted downstream calculations.

### FreshnessState

Allowed values:

- `current`: within the approved freshness threshold.
- `stale`: beyond the threshold but last known good data remains available.
- `expired`: too old for decision-support use.
- `unknown`: cadence or observation timing cannot be established.

Freshness is evaluated from dataset-specific cadence rules, market calendars, observation time, and retrieval time. Retrieval time alone cannot make an old observation current.

### DatasetPolicy

Defines operational expectations for a logical dataset.

Required fields:

- `dataset_id`.
- `provider_id`.
- `subject_scope`.
- `expected_cadence`.
- `fresh_after` duration.
- `stale_after` duration.
- `expire_after` duration.
- `retry_policy_id`.
- `cache_policy_id`.
- `required_for_analysis`.
- `enabled`.

### CachePolicy

Required fields:

- `cache_policy_id`.
- `ttl`.
- `serve_stale_for` duration.
- `refresh_strategy`.
- `cache_key_version`.
- `max_entries` or storage limit where applicable.

Stale cache entries may be displayed only with explicit stale metadata. They must never be rewritten as newly retrieved observations.

### RetryPolicy

Required fields:

- `retry_policy_id`.
- `max_attempts`.
- `initial_delay`.
- `backoff_multiplier`.
- `max_delay`.
- `retryable_error_categories`.
- `jitter_enabled`.

Authentication failures, schema mismatches, validation failures, and explicit permission errors are not automatically retryable.

### IngestionRun

Represents one bounded retrieval and normalization attempt.

Required fields:

- `ingestion_run_id`.
- `dataset_id`.
- `provider_id`.
- `requested_from`, `requested_to`.
- `started_at`, `completed_at`.
- `status`: queued, running, succeeded, partial, failed, or cancelled.
- `attempt_count`.
- `records_received`.
- `records_valid`.
- `records_rejected`.
- `data_cutoff`.
- `commit_sha`.
- `adapter_version`.
- `schema_version`.
- `warning_count`.
- `error_count`.

### IngestionFailure

Required fields:

- `failure_id`.
- `ingestion_run_id`.
- `error_category`.
- `retryable`.
- `safe_message`.
- `provider_status_code` when safe to store.
- `subject_reference` when a failure is record-specific.
- `occurred_at`.

Sensitive request content, credentials, and raw personal portfolio values must not be stored in failure messages.

### SourceSnapshot

Records the exact source set used by a downstream calculation.

Required fields:

- `source_snapshot_id`.
- `created_at`.
- `data_cutoff`.
- `observation_ids` or immutable query criteria.
- `quality_summary`.
- `freshness_summary`.
- `schema_version`.

Analysis and recommendation records must reference a SourceSnapshot rather than relying on an implicit latest state.

## Provider Interface Contract

Every provider adapter must expose equivalent logical operations even when implementation details differ:

- Describe provider capabilities and supported datasets.
- Resolve canonical subjects to provider identifiers.
- Fetch a bounded period or latest eligible observation.
- Return provider response metadata without leaking it into domain contracts.
- Parse and normalize into canonical observations.
- Classify provider and record-level failures.
- Report rate-limit and retry hints when available.

Adapters must not perform investment analysis, portfolio logic, or UI formatting.

## Normalization Rules

- Convert timestamps to UTC for persistence while preserving source timezone metadata.
- Preserve the original observation period for daily, weekly, monthly, quarterly, and annual data.
- Use canonical ISO currency and unit identifiers.
- Reject non-finite numeric values and malformed timestamps.
- Resolve symbols through active aliases valid for the observation date.
- Do not forward-fill missing observations during ingestion.
- Corporate-action and adjusted-price policies must be versioned and explicit.
- Revisions create a new revision or vintage record rather than silently overwriting history where the source supports vintages.

## Idempotency and Uniqueness

A normalized observation is uniquely identified by:

- Canonical subject.
- Metric.
- Observation time or period.
- Provider.
- Revision or vintage identity.
- Schema version where interpretation changed.

Repeated ingestion of the same source data must not create duplicate trusted observations.

## Fail-Safe Rules

- Provider failure never changes a prior valid observation's retrieval timestamp.
- Partial runs are visible as partial and cannot be reported as complete.
- Required datasets block dependent analysis when invalid, expired, or unavailable.
- Optional datasets may degrade outputs only when the limitation is surfaced.
- Last known good data remains queryable with its original timestamps and stale or expired status.
- Conflicting providers are not silently averaged or merged.

## Phase 2 Implementation Sequence

1. Canonical types and validation schemas.
2. Provider interface and shared error model.
3. Yahoo Finance adapter.
4. FRED adapter.
5. ECOS adapter.
6. FX adapter.
7. Persistence and idempotency.
8. Cache and retry services.
9. Scheduled integration and operational reporting.

## Deferred Decisions

- Final FX provider selection.
- Raw payload retention periods.
- Exact Supabase migration layout.
- Provider-specific rate limits and credentials.
- Corporate-action reconciliation across providers.

These require separate Issues and decision records before implementation.
