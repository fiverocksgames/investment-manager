# AI Handoff

## Current State

Investment Manager is in Phase 0 — Foundation. Draft PR #1 establishes the mandatory governance and specification baseline. No application, database migration, deployment workflow, or automated test suite exists yet.

## Repository

- Upstream concept repository: `e20cboy/investment-manager`
- Active fork: `fiverocksgames/investment-manager`
- Default branch: `main`

## Current Branch

- `agent/project-bootstrap`

## Current Pull Request

- PR #1 — `docs: establish project governance`
- Base: `main`
- State: Draft

## Completed in PR #1

The required bootstrap document set now exists:

- `README.md`
- `PROJECT_CHARTER.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `ROADMAP.md`
- `WORKLOG.md`
- `AI_HANDOFF.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/FEATURE_MATRIX.md`
- `docs/ANALYSIS_SPEC.md`
- `docs/PORTFOLIO_SPEC.md`
- `docs/DATABASE.md`
- `docs/API_SPEC.md`
- `docs/SECURITY.md`
- `docs/OPERATIONS.md`
- `docs/DATA_SOURCES.md`
- `docs/INVESTMENT_POLICY.md`
- `docs/TEST_PLAN.md`
- `docs/DECISIONS.md`

## Remaining Phase 0 Work

- Review documents for scope consistency and broken links.
- Add GitHub Issue templates and a pull request template.
- Add Markdown/document validation and baseline CI.
- Review labels, milestones, branch protections, secret scanning, and dependency/security settings.
- Decide and document a software license.
- Review PR #1 against the Definition of Done before marking it ready.

These follow-up items may remain in PR #1 only when they stay within the approved Project Bootstrap scope; otherwise create linked Issues and focused PRs.

## Development Rules

1. Read `PROJECT_CHARTER.md`, `AGENTS.md`, `WORKLOG.md`, and this file before changing the repository.
2. Treat repository documentation as the source of truth; do not rely on chat history.
3. Follow Issue → Design → Documentation → Implementation → Test → PR.
4. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md`.
5. Keep financial calculations in the analysis or portfolio engine, never the UI.
6. Never commit credentials, tokens, or personal portfolio data.
7. Update `WORKLOG.md`, `AI_HANDOFF.md`, and relevant specifications in every PR.
8. Do not claim validations were run when they were not.
9. Keep PR #1 Draft until the bootstrap review is complete.

## Technical Direction

- Frontend: React, TypeScript, Vite, PWA, TailwindCSS.
- Hosting: GitHub Pages.
- Database and authentication: Supabase PostgreSQL and Supabase Auth with Google login.
- Scheduled backend: Python through GitHub Actions.
- Portfolio input: Google Sheets.
- Initial data candidates: Yahoo Finance, FRED, and ECOS, subject to access and terms verification.

## Investment Boundaries

- Conservative, long-term, ETF-first decision support.
- No automated trading.
- No individual-stock recommendations in MVP.
- No leverage, inverse products, derivatives, margin, or short selling.
- Outputs must explain evidence, freshness, assumptions, uncertainty, and risk.
- Bitcoin is not approved for implementation without a separate explicit decision and allocation policy.

## Run Instructions

There is no runnable application. Do not invent installation or run commands. Phase 1 must introduce and verify the development environment before these instructions are added.

## Test Instructions

There is no automated test suite. For PR #1:

- Review Markdown rendering.
- Verify every mandatory document exists.
- Check internal links.
- Verify charter, PRD, feature matrix, specifications, investment policy, worklog, and handoff agree on MVP scope.
- Confirm PR #1 retains the required PR-description sections.
- Record any validation actually performed in the PR body and worklog.

## Known Risks and Assumptions

- Provider contracts, symbol coverage, cadence, and legal usage have not been verified.
- Database tables and RLS policies are specifications only; no migrations exist.
- Google Sheets authentication and import behavior are specifications only.
- Analysis formulas, score weights, and market-regime thresholds are not approved production parameters.
- Repository automation, CI, and security settings are not configured.

## Exact Next Recommended Task

Perform a documentation review of Draft PR #1, then add Issue and PR templates plus documentation validation. Resolve findings and update `WORKLOG.md`, `AI_HANDOFF.md`, and the PR body. Only after the governance baseline is accepted should Phase 1 application bootstrap begin.
