# Portfolio Specification

## Purpose

Define portfolio ingestion, analysis, target allocation, and rebalance guidance for a conservative long-term ETF investor. The system is advisory and never submits orders.

## Requirements

- `REQ-PORT-001`: Import portfolio holdings from an approved Google Sheets schema.
- `REQ-PORT-002`: Calculate current weights, asset-class exposure, currency exposure, gains, losses, and concentration.
- `REQ-PORT-003`: Compare current weights with a user-approved target allocation.
- `REQ-PORT-004`: Generate explainable rebalance guidance subject to policy constraints.
- `REQ-PORT-005`: Store dated portfolio snapshots for performance and drift analysis.

## Supported Assets

MVP portfolios may contain approved Korean ETFs, US ETFs, bond ETFs, gold ETFs, cash, and a separately capped Bitcoin allocation. Unsupported instruments remain visible when imported but receive no recommendation.

## Google Sheets Contract

Required fields: account identifier, ticker, exchange, quantity, average cost, currency, and as-of date. Optional fields include asset-class override and notes. Raw source rows must be preserved or reproducibly referenced; normalization errors must be reported by row.

## Calculations

- Market value in native currency and reporting currency.
- Portfolio and asset-class weights.
- Target drift in percentage points.
- Concentration by asset, issuer, geography, currency, and asset class when metadata exists.
- Realized and unrealized performance only when source data supports accurate calculation.

## Rebalance Policy

Guidance must use configurable tolerance bands and may prioritize contributions before sales. It must account for data freshness, minimum trade size, user restrictions, and available cash. Tax, fees, liquidity, and exchange-rate impacts must be disclosed as limitations unless explicitly modeled.

## Safety Rules

- Never imply guaranteed returns.
- Never recommend leverage, inverse ETFs, derivatives, or individual stocks in MVP.
- Never generate an executable order payload.
- Flag recommendations that would violate the approved investment policy.
- Preserve user approval as the final decision point.

## Snapshots and Auditability

Each snapshot must record valuation time, market-data version, exchange rates, portfolio source version, analysis model version, and policy version. Recalculation from the same inputs must be deterministic.

## Validation

Tests must cover multi-currency holdings, missing prices, zero quantities, duplicate rows, stale sheets, rounding, tolerance boundaries, unsupported assets, and cash-flow effects.
