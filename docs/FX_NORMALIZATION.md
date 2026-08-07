# FX Normalization

## Purpose

Define a provider-independent contract for converting trusted FX observations into an explicit canonical base/quote direction without guessing provider conventions.

## Canonical Direction

`FxPair` identifies one ordered currency pair:

- `base_currency`: currency being priced
- `quote_currency`: currency used to express the price
- canonical value: units of quote currency per one unit of base currency
- canonical unit: `<QUOTE>_per_<BASE>`

Example: canonical `USD/KRW` is represented as base `USD`, quote `KRW`, unit `KRW_per_USD`.

Yahoo Finance labels `KRW=X` as `USD/KRW`; the project therefore treats that specific binding as source base `USD` and source quote `KRW`. This convention is explicit configuration, not inferred from the ticker text.

## Normalization Binding

`FxNormalizationBinding` connects one source convention to one canonical `FxPair`.

The source currencies must be exactly the same two currencies as the canonical pair. A third currency or ambiguous direction is rejected.

Two transformations are allowed:

1. `identity`: source base/quote matches canonical base/quote; preserve the source `Decimal` exactly.
2. `reciprocal`: source base/quote is exactly reversed; compute `1 / source_rate` using a fixed 34-digit Decimal context and `ROUND_HALF_EVEN`.

No binary floating-point calculation is permitted.

## Validation

Normalization rejects:

- non-`FX_RATE` observations
- observation subjects that do not match the configured canonical pair
- zero or negative rates
- invalid currency codes
- identical base and quote currencies
- source currencies unrelated to the canonical pair

The normalizer raises `FxNormalizationError` with a stable code for observation-level failures that callers may classify without parsing exception text.

## Provenance

The normalized observation preserves:

- provider
- provider source identifier
- source retrieval time
- source revision
- quality state
- freshness state
- original provider metadata

It additionally records canonical base/quote, source base/quote, whether identity or reciprocal transformation was applied, and the original source unit.

Normalized observation identifiers are deterministic from canonical pair identity, provider, source identifier, observation time, and source revision.

## Provider Boundaries

Provider adapters remain responsible for retrieving and validating provider payloads. FX normalization does not call external providers and does not silently select or combine providers.

A provider-specific FX symbol may only enter this layer after its direction has been separately verified and configured. Future FRED or ECOS FX bindings must document the same direction semantics before use.

## Initial Scope

- provider-independent normalization only
- canonical currency-pair identity and directional units
- direct and reciprocal transformations
- deterministic network-free tests
- representative Yahoo `KRW=X` integration fixture

Not included:

- cross-provider fallback or averaging
- fixing-time reconciliation
- triangulation through a third currency
- spread/bid/ask normalization
- persistence or snapshot publication
- cache or scheduled ingestion
- portfolio valuation or analysis
