# Roadmap

## Operating Principles

- Documentation and requirements precede implementation.
- Every milestone follows `PROJECT_POLICY.md`.
- Status must reflect verified evidence, not intent.
- No provider, feature, or release is called complete without tests and required validation.
- Explicit user approval is required before merge.

## Release 0.1 — Application Foundation

**Status:** Complete with residual validation work

Completed:

- React, TypeScript, Vite, and Tailwind CSS application shell
- PWA manifest and service-worker baseline
- GitHub Pages deployment
- Supabase integration
- Google OAuth login
- Session persistence and sign-out validation
- Separation of public frontend configuration from privileged credentials

Remaining:

- Browser-level PWA installation and offline validation
- User-owned tables, RLS policies, and cross-user isolation tests
- Reproducible frontend dependency lockfile

## Release 0.2 — Data Platform

**Status:** In progress

### Completed

- Phase 2 architecture and data-platform design
- Canonical provider-independent data models
- Provider capability, request, result, and protocol contracts
- Python 3.12 package and CI baseline
- Official FRED Version 1 economic-series adapter
- Protected runtime-only FRED API-key handling
- Fixture-based FRED adapter tests
- Manual protected FRED live smoke workflow
- Successful live FRED connectivity validation
- Smoke policy that tolerates expected `DGS10` missing-value and date-boundary warnings only when valid observations exist

### Active Next Milestones

1. Yahoo market-data adapter contract verification and implementation
2. ECOS economic-statistics adapter
3. FX normalization provider
4. Normalization and immutable source-snapshot integration
5. Cache executor with preserved provenance
6. Bounded retry executor
7. Scheduled ingestion and operational status reporting
8. Dataset and snapshot versioning

### Exit Criteria

- Market and macro providers map into provider-independent canonical records.
- Source identity, observation time, retrieval time, revision, quality, and freshness are preserved.
- Missing, stale, partial, and failed data never silently become trusted analysis inputs.
- Cache and retries cannot misrepresent freshness or provenance.
- Scheduled jobs fail safely and expose operational evidence.

## Release 0.3 — Portfolio Engine

**Status:** Planned

Planned:

- Google Sheets portfolio import
- Holdings normalization
- Asset-class, geography, and currency classification
- Portfolio snapshots and daily asset-value history
- Target-allocation comparison
- Explainable rebalancing suggestions
- Authorization, RLS, and cross-user isolation

## Release 0.4 — Strategy and Analysis Engine

**Status:** Planned

Planned:

- Daily and weekly indicator windows
- Moving averages
- RSI
- MACD
- Momentum and volatility
- Risk-on, neutral, and risk-off regimes
- Conservative multi-asset allocation logic
- Reproducible input snapshot and cutoff metadata

## Release 0.5 — Backtest and Reporting

**Status:** Planned

Planned:

- Strategy backtesting
- Benchmark comparison
- Transaction-cost and slippage assumptions
- Drawdown and risk reporting
- Daily and weekly summaries
- Telegram notification integration

## Release 1.0 — Stable Investment Manager

**Status:** Future

Target characteristics:

- Stable provider and canonical-data contracts
- Reproducible portfolio and strategy outputs
- Clear confidence, freshness, and limitation disclosures
- Documented operations and recovery procedures
- No trade execution; analysis and decision support only

## Definition of Done

A functional milestone is complete only when all applicable items are satisfied:

1. A scoped Issue exists with acceptance criteria and exclusions.
2. Design and provider contracts are verified before implementation.
3. Work occurs on a dedicated branch, never directly on `main`.
4. Implementation preserves architecture, security, and data-integrity rules.
5. Deterministic tests cover success, failure, and partial-result behavior.
6. Required technical and living documentation is updated.
7. Python, frontend, documentation, and other applicable CI checks pass.
8. Live validation is completed when safe and materially necessary.
9. A substantial pull request begins as Draft.
10. The pull request is marked Ready for Review only after evidence is complete.
11. Explicit user approval is received before merge.
12. Merge and Issue closure are verified.
13. `WORKLOG.md`, `AI_HANDOFF.md`, `CHANGELOG.md`, roadmap, release history, and traceability are current.

## Post-MVP Candidates

The following require separate decisions and must not enter MVP implicitly:

- News and disclosure analysis
- Additional portfolio sources
- Multi-user collaboration
- Stronger authentication methods
- Automated order execution
