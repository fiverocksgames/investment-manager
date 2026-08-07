# Data Sources

## Purpose

Document approved free data providers, the fields consumed, known limitations, attribution, freshness expectations, and failure behavior.

## Provider Principles

- Use only sources whose access method and terms are compatible with the project.
- Preserve provider, source identifier, observation time, retrieval time, frequency, unit, timezone, and revision metadata.
- Normalize provider symbols through canonical asset and economic-series identifiers.
- Never represent delayed, revised, estimated, or cached data as real-time or final.
- Provider availability is not guaranteed; missing data must fail safely.
- Provider payloads are never exposed as public application contracts.

## Provider Contract

Each adapter must implement the provider-independent contract defined in [`DATA_MODEL.md`](DATA_MODEL.md):

- identify provider and dataset
- validate request bounds
- retrieve observations
- map provider errors into stable categories
- normalize identifiers, timestamps, units, and currencies
- return source metadata and quality flags
- never write directly to analysis or UI models

## Yahoo Finance

Intended use: historical and latest available prices for approved Korean and US ETFs, benchmark indices, gold proxies, Bitcoin, and suitable exchange-rate series.

Required fields include provider symbol, observation timestamp, OHLC values where available, adjusted close policy, volume, currency, exchange timezone, retrieval time, and quality state.

Risks include unofficial access patterns, symbol changes, delayed data, incomplete corporate-action adjustments, provider schema changes, and rate limiting. The adapter uses deterministic fixtures, explicit request headers, schema validation, and the common bounded retry executor in live smoke validation.

Yahoo Live Smoke run `31169043266` succeeded on merged commit `18dd594a93ca45f966b79a3b612808751c99c112`, returning 10 trusted SPY daily observations on attempt 1. This is evidence that the bounded request succeeded for that run; it is not an availability or schema-stability guarantee.

## FRED

Intended use: US macroeconomic and financial series such as policy rates, inflation, employment, yields, liquidity, and stress indicators.

Required metadata includes series ID, title, units, frequency, seasonal-adjustment status, observation date, retrieval date, and vintage or revision information when available. Revised values must not overwrite audit history silently.

FRED uses its official API with `FRED_API_KEY` stored only as a runtime GitHub Actions secret for protected live smoke validation.

## ECOS

Intended use: Bank of Korea statistics relevant to Korean investors, including policy rates, exchange rates, monetary aggregates, prices, and growth indicators.

The initial adapter uses the ECOS Open API `StatisticSearch` JSON service and requires `ECOS_API_KEY`. The key is runtime-only configuration and must not be committed, logged, embedded in fixtures, or included in secret-bearing URLs in evidence.

Explicit `EcosSeriesBinding` entries preserve:

- project source identifier
- statistic code
- item codes 1-4 when applicable
- cycle
- canonical subject identity
- canonical unit

Source metadata preserves ECOS statistic/item codes and names, cycle, original source period, and `UNIT_NAME`. Canonical values use `Decimal`. Initial cycle support is annual (`A`), quarterly (`Q`), monthly (`M`), and daily (`D`). ECOS period labels are normalized to the start of the labeled period in UTC; that timestamp is not represented as the publication timestamp.

The initial implementation requests one configured response page per bound series. Pagination orchestration, other ECOS services, additional cycle formats, and revision-specific semantics remain future work.

A manual ECOS Live Smoke workflow uses the common bounded retry executor and representative Bank of Korea base-rate series `722Y001`, item `0101000`, daily cycle. Live connectivity must not be recorded until an actual workflow run succeeds on `main` with `ECOS_API_KEY` configured.

## FX Sources

FX ingestion must use explicit base and quote currencies and a documented fixing or observation convention. Yahoo Finance or ECOS may be used only after identifier, timestamp, and rate-direction validation. A separate provider may be approved through a decision record.

## Google Sheets

Google Sheets is a user-controlled portfolio input, not a market-data provider or application database. It requires explicit schema, least-privilege access, row validation, import versioning, and read-only behavior unless separately approved.

## Data Quality States

Canonical quality states are:

- `valid`
- `stale`
- `partial`
- `revised`
- `estimated`
- `invalid`
- `unavailable`

Quality state propagates into source snapshots, analysis, portfolio valuation, and recommendations.

## Freshness Policy

Every dataset defines:

- expected cadence
- publication or market-calendar behavior
- soft stale threshold
- hard stale threshold
- whether stale reads are allowed
- whether partial publication is allowed

Freshness is calculated from observation and retrieval metadata, not from the time the UI reads the record.

## Cache Policy

Caching reduces provider calls but does not erase provenance. Cache entries include dataset key, source retrieval time, expiry time, policy version, and content identity. Expired entries may only be served with explicit stale metadata when policy allows it.

## Retry Policy

Retries are bounded and apply only to retryable failures such as temporary network errors, rate limits, and selected server failures. Authentication, validation, unsupported-symbol, and deterministic parsing errors are not retried blindly. Backoff includes jitter and respects provider limits.

The common executor retries a complete request only when no trusted observations were produced and all failures are retryable. Partial results stop immediately to avoid repeating already successful source work. Identifier-scoped retries and provider-specific `Retry-After` metadata handling remain future orchestration work.

## Fallback Policy

Fallback sources require an accepted decision record, unit and timestamp comparison, tolerance tests, and explicit source disclosure. The system must not silently combine providers. When no approved source is trustworthy, return `insufficient_data` and retain the last known good snapshot with its original timestamp.

## Provider Review Checklist

Before implementation, verify current access method, terms, authentication, rate limits, fields, units, timezone, revisions, calendars, data-quality checks, failure modes, attribution, cache limits, retention, and removal strategy.
