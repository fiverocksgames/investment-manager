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
```

## Components

### Web Application

Responsibilities:

- Authentication flow and session handling
- Market, candidate, portfolio, and operations views
- Rendering explanations, timestamps, and risk disclosures
- Input validation feedback and user-controlled refresh requests where supported

Non-responsibilities:

- Financial indicator calculation
- Portfolio rebalancing calculation
- Secret-bearing provider calls
- Brokerage transactions

### Supabase Auth

- Google login for MVP
- User identity for ownership boundaries
- Future OTP only after a separate decision

### Supabase PostgreSQL

- User-owned portfolio metadata and snapshots
- Normalized market observations and derived analysis snapshots
- Recommendation snapshots and job status
- Row Level Security for private data

### Python Jobs

Logical modules:

- Data Adapters — provider-specific retrieval and parsing
- Normalization — symbols, dates, timezones, currencies, units
- Analysis Engine — indicators, momentum, volatility, regime
- Portfolio Engine — holdings normalization, allocation, rebalance math
- Recommendation Engine — eligibility, factors, scores, explanations
- Persistence — transactional writes and idempotency
- Operations — retries, freshness, telemetry, failure summaries

### GitHub Actions

- Scheduled data and analysis execution
- CI for lint, typing, tests, build, documentation, and security checks
- Secrets supplied only through repository or environment secrets

### Google Sheets Integration

- MVP portfolio source
- Read-only import principle
- Explicit sheet schema and validation
- No brokerage or automatic transaction synchronization

## Data Flow

1. A scheduled job retrieves raw observations from provider adapters.
2. Inputs are validated, timestamped, and normalized.
3. Normalized observations are persisted with source metadata.
4. Analysis Engine produces versioned derived metrics and regime snapshots.
5. Portfolio Engine imports and normalizes authorized user holdings.
6. Recommendation Engine combines eligible assets with analysis outputs and policy rules.
7. The web app reads authorized snapshots and renders explanations.

## Boundaries

- Provider schemas stop at adapter boundaries.
- Financial calculations stop at engine boundaries.
- Public client configuration is distinct from server-side secrets.
- User-owned data is protected in database policies.
- The UI never becomes the sole source of calculation logic.

## Reliability

- Jobs must be idempotent for the same dataset and observation period.
- Writes should be transactional where partial state would mislead users.
- Stale data remains visible only with an explicit stale status.
- Provider failures must not silently reuse old values as current.
- Derived outputs reference their input timestamps and calculation version.

## Security

- No service-role key in the frontend.
- Row Level Security enabled before user data tables are exposed.
- Logs redact tokens, spreadsheet content, and personal holdings.
- External inputs are schema-validated and size-limited.
- Dependencies and workflows use pinned or reviewed versions where practical.

## Deployment

- Frontend: static build deployed to GitHub Pages.
- Database/Auth: Supabase managed services.
- Scheduled backend: GitHub Actions Python workflows.

The initial design avoids a continuously running custom backend. A dedicated API service requires a future decision if job-based and Supabase interfaces become insufficient.

## Architectural Quality Attributes

- Auditability
- Explainability
- Reproducibility
- Security and privacy
- Low operational cost
- Replaceable data providers
- AI and contributor maintainability
