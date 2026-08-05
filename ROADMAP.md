# Roadmap

## Principles

- Documentation and requirements precede implementation.
- Each phase has explicit entry and exit criteria.
- MVP scope is protected from advanced-feature expansion.
- Phase completion requires traceability, validation, and handoff updates.

## Phase 0 — Foundation

**Status:** Complete

**Objective:** establish durable project governance.

Deliverables:

- Required project and specification documents
- Requirement ID and feature traceability conventions
- Issue and PR templates
- GitHub Actions documentation checks
- Contribution, decision, worklog, and AI handoff processes

Exit criteria:

- `GOV-BOOT-001`, `GOV-TRACE-001`, `GOV-AI-001`, and `GOV-DOC-001` documented
- Bootstrap PR reviewed and merged

## Phase 1 — Infrastructure

**Status:** Complete, except PWA offline validation remains tracked separately

**Objective:** deploy a secure application shell.

Deliverables:

- React, TypeScript, Vite, TailwindCSS
- PWA manifest and service worker baseline
- GitHub Pages deployment
- Supabase project integration
- Google login
- Environment and secret handling

Exit evidence:

- Authenticated user reached the deployed shell
- GitHub Pages deployment succeeded
- Google OAuth callback succeeded
- Session persisted after refresh and browser restart
- Sign-out succeeded
- Public frontend identifiers were separated from privileged credentials

Remaining validation:

- Browser-level PWA installation and offline behavior

## Phase 2 — Data Platform

**Status:** Next

**Objective:** collect, normalize, validate, and timestamp free market and macro data.

Deliverables:

- Provider-independent asset and observation schemas
- Yahoo Finance market adapters
- FRED macro adapters
- ECOS macro adapters
- FX normalization
- Source metadata and retrieval timestamps
- Data freshness, caching, retries, and status reporting
- Scheduled GitHub Actions jobs

Exit criteria:

- Source metadata and timestamps are visible
- Missing and stale data fail safely
- Normalized schemas are provider-independent
- Provider failures do not silently produce investment signals

## Phase 3 — Analysis Engine

**Objective:** produce reproducible market metrics and regimes.

Deliverables:

- Moving averages
- RSI
- MACD
- Momentum
- Volatility
- Risk-on / neutral / risk-off regime classification

Exit criteria:

- Formula specifications and unit tests agree
- Outputs include input period and data timestamp
- UI contains no duplicate calculation logic

## Phase 4 — Portfolio Engine

**Objective:** analyze user holdings without executing trades.

Deliverables:

- Google Sheets portfolio import
- Holdings normalization
- Asset-class and geography classification
- Target allocation comparison
- Rebalancing suggestions
- Portfolio snapshots and performance foundations

Exit criteria:

- Invalid rows are reported clearly
- Rebalancing output is explainable and non-executing
- User data is isolated through authorization and RLS

## Phase 5 — Recommendation Engine

**Objective:** rank conservative ETF candidates with transparent evidence.

Deliverables:

- Eligibility filters
- Multi-factor scoring
- Recommendation explanations
- Risk factors and exclusions
- Data confidence and freshness indicators

Exit criteria:

- Every score maps to documented inputs and weights
- Recommendations disclose assumptions and limitations
- Unsupported assets remain excluded

## Phase 6 — Notification and Automation

**Objective:** deliver scheduled summaries safely.

Deliverables:

- Daily and weekly reports
- Telegram notification integration
- Job monitoring and failure reporting

Exit criteria:

- Notifications contain timestamps and source status
- Duplicate delivery and secret exposure controls are tested

## Phase 7 — Advanced

Potential post-MVP work:

- Backtesting and strategy comparison
- News and disclosure analysis
- Multi-user collaboration
- OTP and stronger authentication
- Additional portfolio sources

These items require separate decisions and must not enter MVP implicitly.
