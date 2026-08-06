# Yahoo Market-Data Adapter

## Purpose

The Yahoo adapter provides bounded historical daily market and FX observations through the provider-independent data contract. It is intended for ETF, equity, crypto, and exchange-rate symbols that are available through Yahoo's chart response.

## Supported Scope

- Daily historical bars only
- Market-price datasets
- FX-rate datasets
- Explicit symbol-to-subject bindings
- Open, high, low, close, adjusted close, and volume preservation
- Partial results when some symbols succeed and others fail

The canonical observation value is adjusted close when present. Other bar fields remain source metadata so downstream analysis can use them without changing the canonical observation contract.

## Binding Contract

Each supported symbol must have a `YahooSymbolBinding` containing:

- provider symbol;
- canonical subject ID;
- observation kind;
- canonical unit;
- expected dataset capability.

Unknown symbols or dataset-kind mismatches fail explicitly. The adapter never infers canonical identity from a provider symbol.

## Normalization Rules

- Numeric values are converted with `Decimal` from textual JSON representations.
- Provider timestamps become timezone-aware UTC datetimes.
- Observation identifiers are deterministic for provider, symbol, timestamp, and adjusted value.
- Retrieval time, currency, exchange timezone, interval, OHLCV values, and adjustment information remain in provider metadata.
- Missing, malformed, or non-finite rows never become trusted observations.
- Rows outside the requested interval are reported as explicit failures.

## Failure Classification

The adapter distinguishes:

- `UNSUPPORTED_DATASET`;
- `UNKNOWN_BINDING`;
- `DATASET_MISMATCH`;
- `HTTP_<status>`;
- `TRANSPORT_ERROR`;
- `INVALID_PAYLOAD`;
- `INVALID_OBSERVATION`;
- `MISSING_VALUE`;
- `OUT_OF_RANGE`.

Rate-limit and server-side HTTP failures are retryable. Binding, payload, parsing, and data-quality failures are not automatically retryable.

## Testing

CI uses deterministic fixtures and performs no live Yahoo requests. Tests cover:

- successful daily-bar normalization;
- OHLCV and adjustment metadata;
- missing rows;
- malformed payloads;
- HTTP retry classification;
- market and FX dataset enforcement;
- mixed successful and failed symbols.

## Operational Boundaries

- No `yfinance` dependency is used.
- No rendered HTML is scraped.
- No intraday, streaming, options, fundamentals, or recommendation data is included.
- No production availability is claimed until a separately controlled live smoke test succeeds.
- Cache, retry execution, persistence, scheduling, analysis, portfolio logic, and UI integration remain separate work.
