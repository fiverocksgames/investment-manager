# FRED Adapter

## Purpose

`FredProvider` is the first executable external-data adapter in Phase 2. It implements the canonical `DataProvider` boundary for official FRED economic-series observations.

## Official Contract

The adapter targets the FRED Version 1 `fred/series/observations` endpoint and requests JSON with:

- `series_id`
- runtime-injected `api_key`
- `file_type=json`
- `observation_start`
- `observation_end`
- `sort_order=asc`

The API key is required by FRED and must be supplied only to trusted Python jobs. It must never be committed, logged, returned in failures, or exposed to the frontend.

## Binding Model

`FredSeriesBinding` maps a provider series ID to:

- a canonical `subject_id`
- a canonical unit

The adapter rejects unknown bindings instead of inventing canonical identities or units.

## Normalization

- Numeric values are parsed as `Decimal`.
- FRED observation dates become midnight UTC timestamps.
- Retrieval time comes from an injected UTC-aware clock.
- FRED real-time start and end values are preserved as revision metadata.
- Different real-time start and end values mark the observation as revised.
- Observation identifiers are deterministic for the provider series, observation date, and revision period.

## Missing and Invalid Data

FRED uses `.` for a missing observation value. The adapter records `MISSING_VALUE` and does not create an `Observation`.

Malformed rows, invalid dates, non-decimal values, observations outside the requested period, unknown bindings, unsupported datasets, invalid payloads, and transport errors remain explicit `IngestionFailure` values.

Mixed success and failure returns a partial `FetchResult`; failed records never become trusted observations.

## Transport and Testing

The default transport uses Python's standard-library HTTPS client against the fixed official endpoint. Transport and clock dependencies are injectable.

CI uses deterministic fixture payloads and never calls FRED or requires an API key. Live integration, credentials, caching, retries, persistence, and scheduling require separate Issues and controls.

## Requirement IDs

- `REQ-PROVIDER-001`
- `REQ-PROVIDER-002`
- `REQ-MKT-001`
- `REQ-MKT-002`
