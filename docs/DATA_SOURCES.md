# Data Sources

## Purpose

Document approved data providers, the fields consumed, known limitations, freshness expectations, and failure behavior.

## Provider Principles

- Use only sources whose access method and terms are compatible with the project.
- Preserve provider, source identifier, observation time, retrieval time, frequency, unit, timezone, and revision metadata.
- Normalize provider symbols through canonical asset, economic-series, and FX-pair identifiers.
- Never represent delayed, revised, estimated, cached, or ambiguous data as current trusted data.
- Provider payloads are never exposed as public application contracts.

## Provider Contract

Each adapter must implement the provider-independent contract defined in [`DATA_MODEL.md`](DATA_MODEL.md): validate request bounds, retrieve observations, classify failures, normalize timestamps and numeric values, preserve provenance, and never write directly to analysis or UI models.

## Yahoo Finance

Intended use: historical and latest available prices for approved ETFs, benchmark indices, gold proxies, Bitcoin, and suitable exchange-rate series.

Required metadata includes provider symbol, observation timestamp, OHLC values where available, adjusted-close policy, volume, currency, exchange timezone, retrieval time, and quality state.

Risks include unofficial access patterns, symbol changes, delayed data, incomplete corporate-action adjustments, provider schema changes, and rate limiting. Deterministic fixtures and controlled live smoke validation remain required.

Yahoo Live Smoke run `31169043266` succeeded on merged commit `18dd594a93ca45f966b79a3b612808751c99c112`, returning 10 trusted SPY daily observations on attempt 1. This is bounded evidence, not an availability guarantee.

For FX, Yahoo ticker text is not parsed to infer direction. The representative `KRW=X` source convention is explicitly configured as base `USD`, quote `KRW`, consistent with Yahoo Finance displaying the instrument as `USD/KRW`. Canonical normalization is handled separately from provider retrieval.

## FRED

Intended use: US macroeconomic and financial series such as policy rates, inflation, employment, yields, liquidity, and stress indicators.

FRED uses its official API with `FRED_API_KEY` stored only as a runtime GitHub Actions secret for protected live smoke validation. Revised values must not overwrite audit history silently.

## ECOS

Intended use: Bank of Korea statistics relevant to Korean investors, including policy rates, exchange rates, monetary aggregates, prices, and growth indicators.

The adapter uses the ECOS Open API `StatisticSearch` JSON service and requires runtime-only `ECOS_API_KEY`. Explicit bindings preserve statistic/item identifiers, cycle, canonical subject identity, unit, source period, and source metadata. Initial cycle support is annual (`A`), quarterly (`Q`), monthly (`M`), and daily (`D`).

ECOS Live Smoke run `31182329368` succeeded on merged `main` commit `23bd2ef88ce7ab3f3da2f288ad066089c163f2e8` with 99 trusted observations on attempt 1. This is bounded live-success evidence, not a permanent availability guarantee.

## FX Sources and Direction

FX ingestion must use an explicit ordered currency pair. The canonical convention is:

- base currency: currency being priced
- quote currency: currency used to express the price
- canonical value: quote currency units per one base currency unit
- canonical unit: `<QUOTE>_per_<BASE>`

`FxPair` and `FxNormalizationBinding` define this contract. Source conventions are configured explicitly and never guessed from provider symbols.

If source direction matches the canonical pair, the source `Decimal` value is preserved exactly. If the source direction is exactly reversed, normalization uses a fixed 34-digit `Decimal` reciprocal with `ROUND_HALF_EVEN`. Zero, negative, unrelated, or ambiguous rates are rejected.

No provider fallback, averaging, or triangulation is allowed without a separately approved decision record. Future ECOS or FRED FX bindings must document their rate direction before use.

See [`FX_NORMALIZATION.md`](FX_NORMALIZATION.md).

## Google Sheets

Google Sheets is a user-controlled portfolio input, not a market-data provider or application database. It requires explicit schema, least-privilege access, row validation, import versioning, and read-only behavior unless separately approved.

## Data Quality and Freshness

Canonical quality/freshness states propagate into source snapshots and downstream analysis. Freshness is calculated from observation and retrieval metadata plus dataset-specific cadence and calendar rules, not from UI read time.

## Cache and Retry Policy

Caching must retain original source retrieval and provenance metadata. Retries are bounded and apply only to retryable failures. The common executor retries a whole request only when no trusted observations exist and all failures are retryable; partial results stop immediately.

## Fallback Policy

Fallback sources require an accepted decision record, unit and timestamp comparison, tolerance tests, and explicit source disclosure. The system must not silently combine providers. When no approved source is trustworthy, return `insufficient_data` and retain the last known good snapshot with its original timestamp.

## Provider Review Checklist

Before implementation, verify access method, terms, authentication, rate limits, fields, units, timezone, revisions, calendars, rate direction where applicable, data-quality checks, failure modes, cache limits, retention, and removal strategy.
