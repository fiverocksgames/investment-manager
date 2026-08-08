# Analysis Specification

## Purpose

Define the deterministic analysis engine used to summarize market conditions and rank ETF candidates. The engine supports human investment decisions; it does not place trades.

## Requirements

- `REQ-MKT-001`: Ingest normalized daily price data for supported ETFs and reference indices.
- `REQ-SIG-001`: Calculate indicators only in the analysis engine.
- `REQ-SIG-002`: Produce reproducible market-regime and candidate scores from versioned inputs and parameters.
- `REQ-SIG-003`: Explain each score using observable factors and disclose missing or stale data.
- `REQ-BKT-001`: Preserve sufficient historical inputs for future backtesting without implementing backtesting in MVP.

## Versioned Analysis Inputs

A future analysis run must consume an immutable `AnalysisInputManifest` rather than independently selecting mutable/latest datasets at calculation time. The manifest binds exactly one already-published `DatasetVersion` per required logical dataset, uses deterministic canonical ordering and content identity, and enforces a declared point-in-time `as_of` boundary.

The manifest is an input-identity boundary only. Analysis parameters, model version, asset-universe version, and output identity remain separate versioned concerns and must be explicit before regime or candidate-score results are considered reproducible under `REQ-SIG-002`.

See `ANALYSIS_INPUT_MANIFESTS.md` for the manifest contract.

## Supported MVP Indicators

- Simple and exponential moving averages.
- RSI using an explicitly versioned period and smoothing convention.
- MACD with versioned fast, slow, and signal periods.
- Momentum over configured lookback windows.
- Realized volatility and drawdown.
- Trend breadth across the approved ETF universe.

## Market Regime

The MVP may classify the market as `risk_on`, `neutral`, `risk_off`, or `insufficient_data`. Classification must be rule-based, documented, deterministic, and accompanied by factor-level evidence. It must not be presented as a guarantee or trade command.

## Candidate Scoring

Scores may combine trend, momentum, volatility, drawdown, liquidity proxies, and data quality. Every component must expose its weight, raw value, normalized value, and contribution. Scores must remain comparable only within the same model version and asset universe.

## Data Quality Rules

- Record source, retrieval time, observation time, currency, timezone, and adjustment policy.
- Reject impossible values and duplicate observations.
- Mark stale, incomplete, or estimated data explicitly.
- Do not silently forward-fill signals across material gaps.
- Reject analysis inputs whose dataset-version point-in-time evidence exceeds the manifest boundary.

## Boundaries

- No calculations in UI components.
- No individual-stock analysis in MVP.
- No leverage, inverse, derivatives, or automatic execution logic.
- No unreviewed AI-generated numeric signal may influence a score.
- An input manifest does not itself imply that any indicator, regime, candidate score, portfolio allocation, or recommendation has been calculated.

## Validation

Golden datasets must cover indicator calculations, missing data, holidays, split-adjusted data, regime boundaries, deterministic reruns, and exact recovery of versioned input identity. Numeric tolerances and reference formulas must be documented with tests.
