# ECOS Adapter

## Purpose

The ECOS adapter retrieves Bank of Korea Economic Statistics System (ECOS) `StatisticSearch` JSON data and normalizes it into provider-independent canonical economic observations.

ECOS requires an API key. The key is runtime configuration only and must never be committed, logged, embedded in fixtures, or included in PR evidence.

## Binding Contract

`EcosSeriesBinding` explicitly maps a project source identifier to:

- ECOS statistic code
- item code 1 and optional item codes 2-4
- cycle
- canonical subject UUID
- canonical unit

The adapter does not infer canonical identity from provider labels.

## Supported Scope

Initial cycle support is:

- `A` annual
- `Q` quarterly
- `M` monthly
- `D` daily

Canonical timestamps represent the start of the labeled ECOS period in UTC. This is a normalization convention, not a claim that ECOS published the value at midnight UTC.

The initial adapter supports only the common `economic_series` capability and the ECOS `StatisticSearch` service.

## Normalization

- `DATA_VALUE` becomes canonical `Decimal`.
- `TIME` becomes a timezone-aware UTC timestamp according to the binding cycle.
- Canonical `unit` comes from the explicit binding.
- ECOS `UNIT_NAME` is preserved as source metadata for audit and mismatch review.
- ECOS statistic/item codes, names, cycle, and source period are preserved in provider metadata.
- Observation UUIDs are deterministic from provider identifiers, cycle, and source period.

## Failure Behavior

The adapter keeps failures explicit:

- unknown binding -> `UNKNOWN_BINDING`
- unsupported dataset -> `UNSUPPORTED_DATASET`
- HTTP 401/403 -> `AUTH_ERROR`, non-retryable
- HTTP 429 and 5xx -> retryable HTTP failure
- transport/timeout -> `TRANSPORT_ERROR`, retryable
- malformed service/schema -> `INVALID_PAYLOAD`, non-retryable
- missing source value -> `MISSING_VALUE`
- malformed row/time/value -> `INVALID_OBSERVATION`
- normalized timestamp outside request bounds -> `OUT_OF_RANGE`

The adapter itself does not retry. Retry orchestration belongs to the common `BoundedRetryExecutor`.

## Live Validation

`.github/workflows/ecos-smoke.yml` is a manually triggered protected smoke workflow. It reads `ECOS_API_KEY` from GitHub Actions secrets and requests a bounded recent window for Bank of Korea base rate series `722Y001`, item `0101000`, daily cycle.

The smoke log prints only provider-independent summary evidence. It must not print the key, the secret-bearing request URL, raw payload, or observation values.

Live connectivity must not be claimed until an actual workflow run succeeds after the workflow exists on `main`.

## Boundaries

This adapter does not implement persistence, cache, scheduling, dataset versioning, fallback providers, analysis, portfolio logic, recommendations, or UI behavior.
