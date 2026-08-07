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
2. Each row links planning, design, implementation, tests, and PR evidence.
3. Requirement IDs are never deleted.
4. Do not mark Done until applicable evidence exists.

## Governance

| Requirement ID | Requirement | Phase | Status | Design / Implementation | Test | PR |
|---|---|---:|---|---|---|---|
| GOV-BOOT-001 | Establish project governance and required documents | 0 | Done | `PROJECT_CHARTER.md`, `ROADMAP.md` | Documentation run #12 | #1 |
| GOV-TRACE-001 | Maintain end-to-end feature traceability | 0 | Done | This document | Documentation CI | #1 |
| GOV-AI-001 | Preserve context for AI and human contributors | 0 | Done | `AGENTS.md`, `AI_HANDOFF.md`, `WORKLOG.md` | Handoff review | #1 |
| GOV-DOC-001 | Require documentation review for functional PRs | 0 | Done | `CONTRIBUTING.md`, `docs/DECISIONS.md` | Documentation CI | #1 |
| GOV-POLICY-001 | Maintain Project Development Policy v1 | 0 | Done | `PROJECT_POLICY.md` | Documentation run #41 | #14 |

## Phase 1 Infrastructure

| Requirement ID | Requirement | Phase | Status | Design / Implementation | Test | PR |
|---|---|---:|---|---|---|---|
| REQ-INFRA-001 | Bootstrap React, TypeScript, and Vite frontend | 1 | Done | `src/`, Vite config | Frontend run #7 | #4 |
| REQ-UI-001 | Provide responsive application shell | 1 | Done | `src/App.tsx`, `src/index.css` | Build passed | #4 |
| REQ-PWA-001 | Provide PWA baseline and manifest | 1 | In Validation | `vite-plugin-pwa` | Browser install/offline pending | #4 |
| REQ-DEPLOY-001 | Deploy through GitHub Pages | 1 | Done | GitHub Pages workflow | Production verified | #4 |
| REQ-AUTH-001 | Authenticate with Supabase Google login | 1 | Done | Auth provider and client | Sign-in, persistence, sign-out | #6 |
| REQ-INFRA-002 | Guard browser-safe Supabase configuration | 1 | Done | `.env.example`, `src/lib/supabase.ts` | Configured and missing states | #6, #8 |
| REQ-SEC-001 | Separate public and privileged credentials | 1 | Done | Security and setup docs | Production configuration | #6, #8 |

## Phase 2 Data Platform

| Requirement ID | Requirement | Phase | Status | Design / Implementation | Test | PR |
|---|---|---:|---|---|---|---|
| REQ-DATA-001 | Provider-independent assets, series, observations, runs, failures, and snapshots | 2 | Done | `docs/DATA_MODEL.md`, `investment_manager/data/models.py` | Python run #1 | #16, #18 |
| REQ-DATA-002 | Preserve source, revision, quality, cutoff, and freshness metadata | 2 | Done | Canonical metadata, policies, and snapshots | Python run #1 | #16, #18 |
| REQ-PROVIDER-001 | Common provider adapter contract | 2 | In Validation | `DataProvider`, `FredProvider`, `YahooProvider`, Yahoo live smoke | Provider fixtures and smoke validation; Python run #20 | #18, #20, #29, #31 |
| REQ-PROVIDER-002 | Explicit validation and failure classification | 2 | In Validation | Canonical failures, provider adapters, bounded retry, Yahoo transport headers | Deterministic failure, smoke, retry, and transport tests; Python run #28, Documentation run #78 | #18, #20, #29, #31, #33, #35 |
| REQ-OPS-002 | Idempotent ingestion and immutable snapshots | 2 | In Design | `docs/OPERATIONS.md`, `SourceSnapshot` | Executor and transaction tests not implemented | #16 |
| REQ-OPS-003 | Apply bounded retries only to retryable provider failures | 2 | In Validation | `RetryPolicy`, `RetryExecution`, `BoundedRetryExecutor` | Python run #26; live retry exhaustion observed safely | #33 |
| REQ-MKT-001 | Collect and normalize market, macro, and FX data | 2 | In Validation | FRED macro plus Yahoo daily market/FX adapter and hardened transport | FRED/Yahoo fixtures; live runs `31141445027`, `31150601290`; Python run #28 | #20, #29, #31, #33, #35 |
| REQ-MKT-002 | Expose source, retrieval time, and freshness | 2 | In Validation | FRED revision metadata and Yahoo metadata plus bounded smoke evidence | Metadata and smoke tests; Python run #20 | #20, #29, #31 |
| REQ-OPS-001 | Run scheduled data and analysis jobs | 2 | Planned | Python CI and manual provider smoke workflows only | Scheduled workflow tests planned | TBD |

## Later MVP Requirements

| Requirement ID | Requirement | Phase | Status | Evidence |
|---|---|---:|---|---|
| REQ-SIG-001 | Calculate moving averages, RSI, and MACD | 3 | Planned | `docs/ANALYSIS_SPEC.md` |
| REQ-SIG-002 | Calculate momentum and volatility | 3 | Planned | `docs/ANALYSIS_SPEC.md` |
| REQ-SIG-003 | Classify market regime | 3 | Planned | `docs/ANALYSIS_SPEC.md` |
| REQ-PORT-001 | Import Google Sheets portfolio | 4 | Planned | `docs/PORTFOLIO_SPEC.md` |
| REQ-PORT-002 | Compare actual and target allocations | 4 | Planned | `docs/PORTFOLIO_SPEC.md` |
| REQ-PORT-003 | Produce non-executing rebalance guidance | 4 | Planned | Portfolio and investment policy docs |
| REQ-REC-001 | Filter eligible Korean and US ETFs | 5 | Planned | PRD and investment policy |
| REQ-REC-002 | Rank ETF candidates with documented factors | 5 | Planned | Analysis and policy specs |
| REQ-REC-003 | Show evidence, risks, assumptions, and confidence | 5 | Planned | PRD and investment policy |

## Deferred or Excluded

| Requirement ID | Requirement | Phase | Status | Rationale |
|---|---|---:|---|---|
| REQ-BKT-001 | Backtest investment strategies | 7 | Deferred | Requires point-in-time datasets and bias controls |
| REQ-NEWS-001 | Analyze news and disclosures | 7 | Deferred | Requires separate data-rights and model validation design |
| REQ-TRADE-001 | Execute brokerage orders | N/A | Excluded | Product is a DSS, not an automated trader |
| REQ-ASSET-001 | Recommend individual stocks | N/A | Excluded | MVP is ETF-focused |
| REQ-LEV-001 | Recommend leverage or inverse products | N/A | Excluded | Conflicts with investment policy |
