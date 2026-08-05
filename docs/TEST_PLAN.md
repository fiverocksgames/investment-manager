# Test Plan

## Purpose

Define the validation strategy for documentation, frontend, data ingestion, analysis, portfolio calculations, authentication, database policies, and deployment.

## Test Levels

### Documentation

Validate required files, Requirement ID references, internal links, decision records, Markdown rendering, and consistency among charter, specifications, feature matrix, worklog, and handoff.

### Unit tests

Cover pure calculations, normalization, validation, scoring components, allocation drift, currency conversion, error mapping, and policy constraints. Tests must be deterministic and include boundary cases.

### Contract tests

Verify provider adapters, API response envelopes, Google Sheets schema, Supabase database functions, and model-version metadata. External calls should use controlled fixtures for routine CI.

### Integration tests

Verify ingestion through normalized storage, analysis from a fixed cutoff, portfolio imports, snapshot creation, rebalance guidance, authentication, and Row Level Security isolation.

### End-to-end tests

Verify the primary user journey: sign in, view data freshness, inspect market analysis, import or select a portfolio, review allocation and drift, generate guidance, and see limitations. No test should place an order.

## Required Scenarios

- Missing, stale, duplicate, revised, malformed, and partial data.
- Market holidays, timezone boundaries, split-adjusted prices, and currency conversion.
- Indicator and regime threshold boundaries.
- Unsupported instruments and policy violations.
- Multi-user isolation and unauthenticated access.
- Provider outage, retry exhaustion, job overlap, and recovery from a prior good state.
- PWA build, routing under GitHub Pages, offline shell behavior, and update handling.

## Numeric Validation

Indicator and portfolio calculations require documented formulas, golden fixtures, expected results, and explicit tolerances. Floating-point comparisons must not rely on exact binary equality.

## CI Gates

A PR may require formatting, linting, type checking, unit tests, contract tests, documentation checks, build verification, migration validation, secret scanning, and dependency review as those capabilities are introduced.

## Test Evidence

Every PR must list commands or automated checks run, results, untested areas, and known limitations. Failed or skipped required checks prevent completion unless an explicit risk acceptance is documented.

## Release Acceptance

Before an MVP production release, all critical requirements in `FEATURE_MATRIX.md` must link to passing validation evidence, security isolation tests must pass, restore readiness must be demonstrated, and outstanding high-severity defects must be resolved or explicitly accepted.
