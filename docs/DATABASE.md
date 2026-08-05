# Database Specification

## Purpose

Define the initial Supabase PostgreSQL data model, ownership rules, audit requirements, and migration discipline.

## Principles

- PostgreSQL is the system of record for application metadata, normalized observations, analysis outputs, preferences, and snapshots.
- Google Sheets remains an approved portfolio input, not the authoritative application database.
- Every user-owned row must be protected by Row Level Security.
- Schema changes require versioned migrations and rollback notes.
- Raw provider payloads should be retained only when licensing, privacy, and storage policy permit.

## Core Entities

### Identity and preferences

- `profiles`: Supabase user identifier, display settings, reporting currency, timezone, timestamps.
- `investment_policies`: user-approved allocation constraints and policy version.
- `data_connections`: metadata for external connections; no plaintext secrets.

### Reference data

- `instruments`: canonical identifier, ticker, exchange, asset class, currency, active status.
- `instrument_aliases`: provider-specific symbols and effective dates.
- `data_sources`: provider identity, terms reference, cadence, and health metadata.

### Market and economic data

- `market_prices`: instrument, observation time, open/high/low/close/adjusted close/volume, source, retrieval time.
- `fx_rates`: base currency, quote currency, observation time, rate, source.
- `economic_observations`: series identifier, observation date, value, vintage metadata, source.

### Analysis

- `analysis_runs`: model version, parameter set, input cutoff, status, timestamps.
- `indicator_values`: run, instrument, indicator identifier, value, observation time.
- `market_regimes`: run, regime, confidence or evidence score, factor evidence.
- `candidate_scores`: run, instrument, total score and component contributions.

### Portfolio

- `portfolios`: owner, name, reporting currency, source metadata.
- `portfolio_holdings`: normalized holding state linked to an import or snapshot.
- `portfolio_snapshots`: valuation time, input versions, total value, policy version.
- `rebalance_runs`: snapshot, target allocation, constraints, recommendations, status.

## Keys and Constraints

Use UUID primary keys for user-owned and run entities. Reference observations require uniqueness across canonical entity, observation time, and source/version dimensions. Monetary and quantity fields must use appropriate fixed-precision numeric types rather than floating point.

## Security

RLS must default to deny. Policies must scope rows through `auth.uid()`. Service-role access is limited to trusted scheduled ingestion and maintenance jobs. Secrets must use platform secret storage and must never appear in tables intended for client access.

## Migrations

Migrations are immutable after merge. Each migration must include purpose, linked Requirement IDs, forward validation, compatibility notes, and rollback or corrective migration guidance.

## Retention and Recovery

Retention periods will be documented per dataset. Portfolio snapshots and decision evidence require durable retention. Backup and restore procedures must be tested before production use.
