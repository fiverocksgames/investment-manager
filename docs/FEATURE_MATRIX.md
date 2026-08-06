# Feature Traceability Matrix

## Status Values

- Proposed — requirement captured but not approved
- Planned — approved for a roadmap phase
- In Design — specifications in progress
- In Development — implementation in progress
- In Validation — tests or review in progress
- Done — Definition of Done satisfied
- Deferred — intentionally postponed
- Excluded — outside agreed scope

## Traceability Rules

1. Every behavior has one or more stable Requirement IDs.
2. Each row links planning, design, data, API, UI, tests, and PR evidence.
3. Use `N/A` only with a short rationale.
4. Do not mark Done until all applicable columns contain evidence.
5. Requirement IDs are never deleted; superseded rows retain history.

## Governance

| Requirement ID | Requirement | Phase | Status | Planning / Design | DB | API | UI | Test | PR |
|---|---|---:|---|---|---|---|---|---|---|
| GOV-BOOT-001 | Establish project governance and required documents | 0 | Done | `PROJECT_CHARTER.md`, `ROADMAP.md` | N/A — governance | N/A — governance | N/A — governance | Documentation run #12 | #1 |
| GOV-TRACE-001 | Maintain end-to-end feature traceability | 0 | Done | This document | N/A | N/A | N/A | Documentation run #12 | #1 |
| GOV-AI-001 | Preserve context for future AI and human contributors | 0 | Done | `AGENTS.md`, `AI_HANDOFF.md`, `WORKLOG.md` | N/A | N/A | N/A | Handoff review | #1 |
| GOV-DOC-001 | Require documentation review for functional PRs | 0 | Done | `CONTRIBUTING.md`, `docs/DECISIONS.md` | N/A | N/A | N/A | Documentation CI | #1 |
| GOV-POLICY-001 | Maintain Project Development Policy v1 | 0 | Done | `PROJECT_POLICY.md` | N/A | N/A | N/A | Documentation run #41 | #14 |

## Phase 1 Infrastructure Requirements

| Requirement ID | Requirement | Phase | Status | Planning / Design | DB | API | UI | Test | PR |
|---|---|---:|---|---|---|---|---|---|---|
| REQ-INFRA-001 | Bootstrap a maintainable React, TypeScript, and Vite frontend | 1 | Done | Issue #3, `docs/ARCHITECTURE.md` | N/A | N/A | `src/`, Vite config | Frontend run #7 | #4 |
| REQ-UI-001 | Provide a responsive application shell with clear capability status | 1 | Done | Issue #3 | N/A | N/A | `src/App.tsx`, `src/index.css` | Build passed | #4 |
| REQ-PWA-001 | Provide a PWA baseline and generated web manifest | 1 | In Validation | `docs/ARCHITECTURE.md` | N/A | N/A | `vite-plugin-pwa` | Install and offline validation pending | #4 |
| REQ-DEPLOY-001 | Build and deploy through GitHub Pages | 1 | Done | `docs/ARCHITECTURE.md` | N/A | N/A | Repository-relative base path | Production deployment verified | #4 |
| REQ-AUTH-001 | Authenticate through Supabase Google login | 1 | Done | `docs/SUPABASE_SETUP.md`, `docs/SECURITY.md` | Supabase Auth | Supabase client | Auth-aware shell | Sign-in, persistence, and sign-out verified | #6 |
| REQ-INFRA-002 | Provide guarded browser-safe Supabase configuration | 1 | Done | `.env.example` | N/A | `src/lib/supabase.ts` | Configuration state | Missing and configured builds verified | #6, #8 |
| REQ-SEC-001 | Separate public identifiers from privileged credentials | 1 | Done | `docs/SECURITY.md` | RLS pending for user tables | No service-role client | Safe errors | Production configuration verified | #6, #8 |

## Phase 2 Data Platform Requirements

| Requirement ID | Requirement | Phase | Status | Planning / Design | DB | API | UI | Test | PR |
|---|---|---:|---|---|---|---|---|---|---|
| REQ-DATA-001 | Define provider-independent assets, series, observations, runs, failures, and source snapshots | 2 | In Design | Issue #15, `docs/DATA_MODEL.md`, `docs/ARCHITECTURE.md` | `docs/DATABASE.md` | `docs/API_SPEC.md` | N/A — design only | `docs/TEST_PLAN.md` | TBD |
| REQ-DATA-002 | Preserve source, revision, quality, cutoff, and freshness metadata | 2 | In Design | `docs/DATA_MODEL.md`, `docs/DATA_SOURCES.md` | Observation and snapshot design | Canonical response metadata | Freshness UI planned | Freshness and revision scenarios | TBD |
| REQ-PROVIDER-001 | Isolate Yahoo Finance, FRED, ECOS, and FX behind a common adapter contract | 2 | In Design | `docs/ARCHITECTURE.md`, `docs/DATA_SOURCES.md`, DEC-009 | Provider and alias tables | Internal provider contract | N/A | Provider contract tests | TBD |
| REQ-PROVIDER-002 | Apply bounded validation, caching, retry, and failure classification per dataset | 2 | In Design | Dataset, cache, and retry policies; DEC-011 | Policy and failure tables | Stable error categories | Degraded state planned | Cache, retry, and failure scenarios | TBD |
| REQ-OPS-002 | Execute idempotent ingestion and publish coherent immutable source snapshots | 2 | In Design | `docs/OPERATIONS.md`, DEC-010 | Runs, failures, snapshots | Operations status model | Operations status planned | Integration and transaction tests | TBD |
| REQ-MKT-001 | Collect and normalize market, macro, and FX data | 2 | Planned | Phase 2 design documents | Phase 2 schema planned | Canonical read models | Data views planned | Provider and integration tests | TBD |
| REQ-MKT-002 | Expose source, retrieval time, and freshness status | 2 | Planned | Phase 2 design documents | Snapshot metadata planned | Response envelope | Freshness badge planned | Freshness tests | TBD |
| REQ-OPS-001 | Run scheduled data and analysis jobs through GitHub Actions | 2 | Planned | `docs/OPERATIONS.md` | Job status planned | Status model | Operations status planned | Workflow tests | TBD |

## Later MVP Requirements

| Requirement ID | Requirement | Phase | Status | Planning / Design | DB | API | UI | Test | PR |
|---|---|---:|---|---|---|---|---|---|---|
| REQ-SIG-001 | Calculate moving averages, RSI, and MACD | 3 | Planned | `docs/ANALYSIS_SPEC.md` | Derived metrics | Planned | Metric views | Formula tests | TBD |
| REQ-SIG-002 | Calculate momentum and volatility | 3 | Planned | `docs/ANALYSIS_SPEC.md` | Derived metrics | Planned | Metric views | Formula tests | TBD |
| REQ-SIG-003 | Classify market regime | 3 | Planned | `docs/ANALYSIS_SPEC.md` | Regime snapshots | Planned | Regime summary | Threshold tests | TBD |
| REQ-PORT-001 | Import and normalize a Google Sheets portfolio | 4 | Planned | `docs/PORTFOLIO_SPEC.md` | Portfolio tables | Planned | Import flow | Import tests | TBD |
| REQ-PORT-002 | Compare actual and target allocations | 4 | Planned | `docs/PORTFOLIO_SPEC.md` | Snapshots | Planned | Allocation views | Calculation tests | TBD |
| REQ-PORT-003 | Produce explainable non-executing rebalancing suggestions | 4 | Planned | Portfolio and investment policy | Runs | Planned | Rebalance view | Policy tests | TBD |
| REQ-REC-001 | Filter eligible Korean and US ETFs | 5 | Planned | PRD and investment policy | Universe | Planned | Candidate list | Eligibility tests | TBD |
| REQ-REC-002 | Rank ETF candidates with documented factors | 5 | Planned | Analysis and policy specs | Scores | Planned | Score explanation | Scoring tests | TBD |
| REQ-REC-003 | Show evidence, risks, assumptions, and confidence | 5 | Planned | PRD and investment policy | Snapshots | Planned | Detail view | Explanation tests | TBD |

## Deferred or Excluded

| Requirement ID | Requirement | Phase | Status | Rationale |
|---|---|---:|---|---|
| REQ-BKT-001 | Backtest investment strategies | 7 | Deferred | Requires point-in-time datasets and bias controls after MVP |
| REQ-NEWS-001 | Analyze news and disclosures | 7 | Deferred | Data rights and model validation require separate design |
| REQ-TRADE-001 | Execute brokerage orders | N/A | Excluded | Product is a DSS, not an automated trading system |
| REQ-ASSET-001 | Recommend individual stocks | N/A | Excluded | MVP is ETF-focused |
| REQ-LEV-001 | Recommend leverage or inverse products | N/A | Excluded | Conflicts with investment policy |
