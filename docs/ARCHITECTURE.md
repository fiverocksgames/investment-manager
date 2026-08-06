# Architecture

## Overview

Investment Manager uses a static React PWA for presentation, Supabase for identity and persisted application data, and Python jobs in GitHub Actions for data collection and deterministic financial analysis.

## Context

```text
User
  |
  v
React + TypeScript PWA on GitHub Pages
  |                 \
  |                  \ Google Sheets portfolio source
  v
Supabase Auth + PostgreSQL
  ^
  |
Python data, analysis, portfolio, and recommendation jobs
  |
  +-- Yahoo Finance
  +-- FRED
  +-- ECOS
  +-- approved FX sources
```

## Layered Architecture

```text
Provider Adapter
      |
      v
Validation and Normalization
      |
      v
Canonical Observation Model
      |
      +--> Cache
      |
      +--> Supabase Persistence
      |
      v
Analysis Engine
      |
      v
Portfolio and Recommendation Engines
      |
      v
React UI
```

Provider payloads never cross the adapter boundary. All downstream consumers use the canonical entities defined in [`DATA_MODEL.md`](DATA_MODEL.md).

## Implemented Frontend Baseline

Phase 1 established:

- React 19 and TypeScript
- Vite static build
- Tailwind CSS styling
- `vite-plugin-pwa` service-worker registration and manifest generation
- GitHub Actions build validation and Pages deployment
- Supabase Auth with Google OAuth

The UI remains presentation-only and does not calculate financial indicators or normalize provider data.

## Phase 2 Components

### Provider Adapters

Each provider adapter owns authentication, request construction, response parsing, provider error mapping, and provider-specific identifiers. Initial adapters are planned for Yahoo Finance, FRED, ECOS, and approved FX sources.

### Validation and Normalization

The normalization layer converts provider output into canonical assets, series, observations, currencies, units, frequencies, and timestamps. Invalid values are rejected rather than coerced silently.

### Canonical Data Model

The model contains assets, aliases, economic series, providers, observations, dataset policies, ingestion runs, failures, quality states, freshness states, and immutable source snapshots. Observation identity includes provider and source revision dimensions so revised macro data and corrected prices remain auditable.

### Cache

The cache reduces unnecessary provider calls but never replaces source metadata or freshness evaluation. A cache hit must expose the original observation time, retrieval time, and expiry decision. Expired data may be returned only with an explicit stale state.

### Persistence

Supabase PostgreSQL stores normalized reference data, observations, ingestion metadata, and later derived outputs. Writes are idempotent and transactional when partial publication could mislead consumers.

### Operations

GitHub Actions runs scheduled Python ingestion jobs. Concurrency controls prevent overlapping runs for the same dataset. Runs record commit SHA, provider, dataset, cutoff, counts, warnings, failures, and final status.

## Data Flow

1. A scheduled job creates an ingestion-run record with an explicit cutoff.
2. The provider adapter retrieves a bounded dataset.
3. The response is schema-validated and mapped into canonical records.
4. Quality and freshness states are calculated from the dataset policy.
5. Normalized observations and source metadata are persisted idempotently.
6. A source snapshot is published only when required validation succeeds.
7. Downstream analysis consumes a specific successful source snapshot.
8. The UI reads normalized data and displays source, cutoff, and freshness information.

## Failure Boundaries

- Provider failures never create successful snapshots.
- Partial datasets are marked `partial` and are not promoted when the dataset policy requires completeness.
- Retry exhaustion produces a stable failure category.
- Prior good observations remain intact but are never relabeled as current.
- Required-input failure blocks dependent analysis.
- Fallback providers require a separate accepted decision and comparison tests.

## Security

- Provider credentials are available only to trusted jobs.
- No service-role or provider secret enters the frontend bundle.
- Logs redact credentials and sensitive request parameters.
- User-owned data requires default-deny Row Level Security before exposure.
- Public market data and private portfolio data remain separate authorization domains.

## Deployment

- Frontend: GitHub Pages
- Database and Auth: Supabase
- Scheduled backend: GitHub Actions Python workflows
- No continuously running custom API service is required for Phase 2

## Quality Attributes

- Auditability
- Explainability
- Reproducibility
- Explicit freshness
- Fail-safe degradation
- Provider replaceability
- Low operational cost
- Security and privacy

## Current Limitations

- Provider adapters and scheduled ingestion are not implemented.
- Database migrations for the Phase 2 model are not created.
- Provider terms, rate limits, and identifiers require implementation-time verification.
- PWA installation and offline behavior remain unverified.
- `package-lock.json` is not committed; frontend CI still uses `npm install`.
