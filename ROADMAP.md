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

- Phase 2 architecture and provider-independent canonical data models
- Python 3.12 package and CI baseline
- FRED economic-series adapter, protected API-key handling, deterministic fixtures, and verified live retrieval
- Yahoo daily market-price/FX adapter, controlled live smoke, bounded retry integration, HTTP header hardening, and verified live retrieval
- Bank of Korea ECOS `StatisticSearch` economic-series adapter, secret-based live smoke, sanitized transport diagnostics, and verified live retrieval
- Provider-independent bounded retry executor with exponential backoff, jitter, partial-result stop, and retry-exhaustion evidence
- Canonical FX normalization with explicit base/quote direction and deterministic Decimal inverse normalization
- Deterministic immutable source-snapshot publication with explicit cutoff, checksum, and snapshot identity
- Transactional idempotent snapshot persistence with remotely validated Supabase schema and foreign-key indexing
- Provenance-preserving process-local cache executor with explicit TTL and no silent stale fallback
- Provider-independent scheduled-ingestion orchestration with explicit partial/failure policy and operational execution evidence
- Production Yahoo SPY scheduling implementation with durable ingestion-run/failure persistence, merged on `main`
- Live-success evidence recorded for FRED, Yahoo, and ECOS provider retrieval

### Active Next Milestones

1. Production-live validation of the merged Yahoo scheduler: apply operational-status migration, configure `SUPABASE_DB_URL`, manually dispatch the workflow, and verify durable run evidence
2. Dataset and snapshot versioning
3. Broaden scheduled ingestion to additional approved datasets/providers after the initial production path is proven

### Exit Criteria

- Market, macro, and FX providers map into provider-independent canonical records.
- FX direction is explicit and never inferred from ticker text.
- Source identity, observation time, retrieval time, revision, quality, and freshness are preserved.
- Missing, stale, partial, failed, and ambiguous data never silently become trusted analysis inputs.
- Cache and retries cannot misrepresent freshness or provenance.
- Immutable source snapshots make downstream calculations reproducible with deterministic content identity and cutoff semantics.
- Persisted observations and snapshots are transactionally idempotent and immutable-conflict safe.
- Remote database deployment is evidenced separately from committed migration files.
- Scheduled jobs fail safely and expose durable sanitized operational evidence.
- Production scheduling is not called live until the workflow, required secret, remote schema, and persisted run evidence are actually verified.

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
