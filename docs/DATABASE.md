# Database Specification

## Purpose

Define the Supabase PostgreSQL model, ownership rules, audit requirements, and migration discipline for the data platform and later product engines.

## Principles

- PostgreSQL is the system of record for normalized observations, ingestion metadata, derived outputs, preferences, and snapshots.
- Provider payloads do not become application contracts.
- Observation provenance and revisions are preserved.
- Every user-owned row uses default-deny Row Level Security.
- Schema changes require immutable versioned migrations and validation evidence.
- Fixed-precision numeric types are used for money, quantities, rates, and observations.

## Phase 2 Reference Tables

### `data_providers`

Provider identity, adapter version, terms reference, enabled state, and health metadata.

### `assets`

Canonical asset identifier, display name, asset class, instrument type, currency, exchange, timezone, and active dates.

### `asset_aliases`

Provider-specific symbol, canonical asset, effective dates, and alias status. Unique by provider, symbol, and effective range.

### `economic_series`

Canonical series identifier, title, category, frequency, units, seasonal-adjustment status, geography, and active dates.

### `dataset_policies`

Expected cadence, calendar, soft and hard stale thresholds, partial-data policy, cache policy version, and retry policy version.

## Phase 2 Observation Tables

### `market_observations`

Canonical asset, observation time, OHLC values where applicable, adjusted close, volume, currency, provider, source identifier, retrieval time, quality state, and source revision.

### `fx_observations`

Base currency, quote currency, observation time, rate, provider, source identifier, retrieval time, quality state, and source revision.

### `economic_observations`

Canonical series, observation period, value, unit, provider, source identifier, retrieval time, vintage or revision metadata, and quality state.

### `source_snapshots`

Immutable publication unit identifying a coherent successful or partial dataset, cutoff, provider, policy version, row counts, quality summary, and publication time.

## Phase 2 Operational Tables

### `ingestion_runs`

Run identifier, dataset, provider, adapter version, commit SHA, cutoff, start and end time, status, requested and received counts, normalized and rejected counts, warning count, and snapshot identifier.

### `ingestion_failures`

Run identifier, stable category, retryable flag, safe message, provider code where non-sensitive, attempt number, occurrence time, and affected source identifier.

### `cache_entries`

Dataset key, content identity, provider retrieval time, stored time, expiry time, policy version, and status. Sensitive provider responses are not stored unless explicitly approved.

## Keys and Idempotency

- User-owned and run entities use UUID primary keys.
- Reference entities use stable canonical identifiers plus surrogate keys where useful.
- Observation uniqueness includes canonical subject, observation period, provider, source identifier, and revision dimension.
- Reprocessing the same provider payload and revision must not create duplicate trusted observations.
- Corrected provider values create a new revision or update through an auditable rule; history is not silently erased.

## Publication Transactions

A source snapshot is published only after required validation succeeds. Observation writes, run counts, and snapshot publication must be transactional where partial visibility would mislead consumers. Failed runs never point to a successful snapshot.

## Security

Public market and macro observations may eventually be readable through constrained views. Ingestion tables and provider details remain server-controlled. Service-role access is limited to trusted jobs. User portfolios and preferences remain separate and require `auth.uid()`-scoped RLS.

## Migrations

Phase 2 implementation will introduce focused migrations only after this design is approved. Each migration includes Requirement IDs, forward validation, compatibility notes, rollback or corrective guidance, and RLS impact.

## Retention

Observation and revision retention is dataset-specific. Source snapshots and run metadata are retained long enough to reproduce investment-decision inputs. Raw payload retention requires a separate licensing, privacy, storage, and security decision.
