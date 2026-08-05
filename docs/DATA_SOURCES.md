# Data Sources

## Purpose

Document approved free data providers, the fields consumed, known limitations, attribution, and fallback behavior.

## Provider Principles

- Use only sources whose access method and terms are compatible with the project.
- Preserve source attribution, retrieval time, observation time, and revision metadata.
- Normalize provider symbols and units through canonical instrument and series identifiers.
- Do not represent delayed, revised, or unofficial data as real-time or final.
- Provider availability is not guaranteed; all consumers must handle missing data.

## Yahoo Finance

Intended use: historical and latest available market prices for approved ETFs, indices, and exchange-rate proxies where suitable.

Risks and limitations: unofficial access patterns may change, symbols vary by exchange, timestamps and adjusted-price behavior require validation, and data may be delayed or incomplete. The implementation must isolate the provider behind an adapter and must not depend on undocumented fields without tests.

## FRED

Intended use: US macroeconomic and financial series such as policy rates, inflation, labor, yield, and stress indicators.

Requirements: record series ID, units, frequency, seasonal-adjustment status, observation date, retrieval date, and vintage/revision information when available. Series definitions must be reviewed before use in scoring.

## ECOS

Intended use: Bank of Korea economic and financial statistics relevant to Korean investors, including rates, prices, growth, and exchange-rate data.

Requirements: preserve statistic code, item code, cycle, units, observation period, and source metadata. Korean calendar and publication delays must be considered.

## Google Sheets

Intended use: user-controlled portfolio input. Sheets are not a market-data provider and are not the application database.

Requirements: explicit schema, user consent, least-privilege access, row-level validation, import versioning, and clear error reporting. The source sheet must never be modified without a separately approved requirement.

## Data Quality Classification

Each observation or dataset should expose a quality state such as `valid`, `stale`, `partial`, `revised`, `estimated`, `invalid`, or `unavailable`. Quality state must propagate into analysis and portfolio outputs.

## Fallback Policy

Fallback sources may be introduced only through a documented decision and validation comparison. The system must not silently combine inconsistent sources. When no approved source is reliable, return `insufficient_data` and preserve the last known good result with its timestamp.

## Review Checklist

Before adding a source, document access method, licensing or terms, authentication, rate limits, fields, units, timezone, revision behavior, data quality checks, failure modes, attribution, retention, and removal strategy.
