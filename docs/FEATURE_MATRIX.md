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
| GOV-DOC-001 | Require documentation review for functional PRs | 0 | Done | `CONTRIBUTING.md`, `docs/DECISIONS.md` | N/A | N/A | N/A | PR template and documentation CI | #1 |

## Phase 1 Infrastructure Requirements

| Requirement ID | Requirement | Phase | Status | Planning / Design | DB | API | UI | Test | PR |
|---|---|---:|---|---|---|---|---|---|---|
| REQ-INFRA-001 | Bootstrap a maintainable React, TypeScript, and Vite frontend | 1 | In Validation | Issue #3, `docs/ARCHITECTURE.md` | N/A — frontend baseline | N/A — static shell | `src/`, `index.html`, Vite config | Frontend run #2 build passed | #4 |
| REQ-UI-001 | Provide a responsive application shell with clear capability status | 1 | In Validation | Issue #3, `docs/ARCHITECTURE.md` | N/A | N/A | `src/App.tsx`, `src/index.css` | TypeScript and Vite build passed | #4 |
| REQ-PWA-001 | Provide a PWA baseline and generated web manifest | 1 | In Validation | Issue #3, `docs/ARCHITECTURE.md` | N/A | N/A | `vite-plugin-pwa`, `src/vite-env.d.ts` | Build passed; browser install validation pending | #4 |
| REQ-DEPLOY-001 | Build and deploy the static application through GitHub Pages | 1 | In Validation | Issue #3, `docs/ARCHITECTURE.md` | N/A | N/A | Repository-relative Vite base path | PR build passed; post-merge deployment pending | #4 |
| REQ-AUTH-001 | Authenticate users through Supabase Google login | 1 | Planned | `docs/PRD.md`, `docs/SECURITY.md` | `docs/DATABASE.md` | `docs/API_SPEC.md` | Auth screens planned | `docs/TEST_PLAN.md` | TBD |

## MVP Product Requirements

| Requirement ID | Requirement | Phase | Status | Planning / Design | DB | API | UI | Test | PR |
|---|---|---:|---|---|---|---|---|---|---|
| REQ-MKT-001 | Collect and normalize market, macro, and FX data | 2 | Planned | `docs/DATA_SOURCES.md`, `docs/ARCHITECTURE.md` | `docs/DATABASE.md` | `docs/API_SPEC.md` | Data status planned | `docs/TEST_PLAN.md` | TBD |
| REQ-MKT-002 | Expose source, retrieval time, and freshness status | 2 | Planned | `docs/DATA_SOURCES.md` | `docs/DATABASE.md` | `docs/API_SPEC.md` | Freshness badge planned | `docs/TEST_PLAN.md` | TBD |
| REQ-SIG-001 | Calculate moving averages, RSI, and MACD in Analysis Engine | 3 | Planned | `docs/ANALYSIS_SPEC.md` | Derived metrics planned | `docs/API_SPEC.md` | Metric views planned | `docs/TEST_PLAN.md` | TBD |
| REQ-SIG-002 | Calculate momentum and volatility | 3 | Planned | `docs/ANALYSIS_SPEC.md` | Derived metrics planned | `docs/API_SPEC.md` | Metric views planned | `docs/TEST_PLAN.md` | TBD |
| REQ-SIG-003 | Classify risk-on, neutral, or risk-off market regime | 3 | Planned | `docs/ANALYSIS_SPEC.md` | Regime snapshots planned | `docs/API_SPEC.md` | Regime summary planned | `docs/TEST_PLAN.md` | TBD |
| REQ-PORT-001 | Import and normalize a Google Sheets portfolio | 4 | Planned | `docs/PORTFOLIO_SPEC.md` | `docs/DATABASE.md` | `docs/API_SPEC.md` | Import flow planned | `docs/TEST_PLAN.md` | TBD |
| REQ-PORT-002 | Compare actual and target allocations | 4 | Planned | `docs/PORTFOLIO_SPEC.md` | Portfolio snapshots planned | `docs/API_SPEC.md` | Allocation views planned | `docs/TEST_PLAN.md` | TBD |
| REQ-PORT-003 | Produce explainable, non-executing rebalancing suggestions | 4 | Planned | `docs/PORTFOLIO_SPEC.md`, `docs/INVESTMENT_POLICY.md` | Suggestion snapshots planned | `docs/API_SPEC.md` | Rebalance view planned | `docs/TEST_PLAN.md` | TBD |
| REQ-REC-001 | Filter eligible Korean and U.S. ETFs | 5 | Planned | `docs/PRD.md`, `docs/INVESTMENT_POLICY.md` | Candidate universe planned | `docs/API_SPEC.md` | Candidate list planned | `docs/TEST_PLAN.md` | TBD |
| REQ-REC-002 | Rank ETF candidates with documented factors and weights | 5 | Planned | `docs/ANALYSIS_SPEC.md`, `docs/INVESTMENT_POLICY.md` | Score snapshots planned | `docs/API_SPEC.md` | Score explanation planned | `docs/TEST_PLAN.md` | TBD |
| REQ-REC-003 | Show recommendation evidence, risks, assumptions, and confidence | 5 | Planned | `docs/PRD.md`, `docs/INVESTMENT_POLICY.md` | Recommendation snapshots planned | `docs/API_SPEC.md` | Recommendation detail planned | `docs/TEST_PLAN.md` | TBD |
| REQ-OPS-001 | Run scheduled data and analysis jobs through GitHub Actions | 2 | Planned | `docs/OPERATIONS.md` | Job status planned | Status endpoint planned | Operations status planned | `docs/TEST_PLAN.md` | TBD |

## Deferred or Excluded

| Requirement ID | Requirement | Phase | Status | Rationale |
|---|---|---:|---|---|
| REQ-BKT-001 | Backtest investment strategies | 7 | Deferred | Requires point-in-time datasets and bias controls after MVP |
| REQ-NEWS-001 | Analyze news and disclosures | 7 | Deferred | Data rights, source quality, and model validation require separate design |
| REQ-TRADE-001 | Execute brokerage orders | N/A | Excluded | Product is a DSS, not an automated trading system |
| REQ-ASSET-001 | Recommend individual stocks | N/A | Excluded | MVP is ETF-focused and conservative |
| REQ-LEV-001 | Recommend leverage or inverse products | N/A | Excluded | Conflicts with MVP investment policy |
