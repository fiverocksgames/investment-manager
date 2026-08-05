# AI Handoff

## Current State

Investment Manager is in Phase 0 — Foundation. The repository has been initialized and Draft PR #1 is establishing governance and specification documents. No application, infrastructure, database migration, workflow, or test code exists yet.

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

## Recent Work

Created or expanded:

- `PROJECT_CHARTER.md`
- `AGENTS.md`
- `ROADMAP.md`
- `CONTRIBUTING.md`
- `WORKLOG.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/FEATURE_MATRIX.md`
- `docs/INVESTMENT_POLICY.md`
- `docs/DECISIONS.md`

## Remaining Bootstrap Work

Required files still to complete:

- Expand `README.md`
- Create `CHANGELOG.md`
- Create `docs/ANALYSIS_SPEC.md`
- Create `docs/PORTFOLIO_SPEC.md`
- Create `docs/DATABASE.md`
- Create `docs/API_SPEC.md`
- Create `docs/SECURITY.md`
- Create `docs/OPERATIONS.md`
- Create `docs/DATA_SOURCES.md`
- Create `docs/TEST_PLAN.md`

Recommended Phase 0 follow-up:

- Add `.github/ISSUE_TEMPLATE/` files
- Add `.github/pull_request_template.md`
- Add Markdown link and documentation checks
- Review repository branch protections and secret-scanning settings

## Development Rules

1. Read `AGENTS.md` before changing the repository.
2. Treat repository documents as the source of truth; do not depend on chat history.
3. Follow Issue → Design → Documentation → Implementation → Test → PR.
4. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md`.
5. Keep all financial calculations outside the UI.
6. Never commit secrets or personal portfolio data.
7. Update `WORKLOG.md` and this file in every PR.
8. Do not claim validations were run when they were not.

## Technical Direction

- Frontend: React, TypeScript, Vite, PWA, TailwindCSS
- Hosting: GitHub Pages
- Database: Supabase PostgreSQL
- Authentication: Supabase Auth with Google login
- Scheduled backend: Python in GitHub Actions
- Portfolio source: Google Sheets
- Data: Yahoo Finance, FRED, ECOS, subject to verification

## Investment Boundaries

- Conservative long-term, ETF-first decision support
- No automated trading
- No individual stocks in MVP
- No leverage, inverse products, derivatives, margin, or short selling
- Recommendations must be explainable and disclose data freshness, uncertainty, assumptions, and risks

## Run Instructions

There is no runnable application yet. Do not invent setup commands. Phase 1 must introduce and document the frontend and development environment before run instructions can be provided.

## Test Instructions

There is no automated test suite yet. For the current documentation PR:

- Review Markdown rendering
- Check internal links after all files exist
- Verify every mandatory document is present
- Verify `PROJECT_CHARTER.md`, `docs/PRD.md`, `docs/FEATURE_MATRIX.md`, and `docs/INVESTMENT_POLICY.md` agree on scope
- Verify PR #1 contains the required PR sections

## Known Risks and Assumptions

- Data provider contracts, symbol coverage, update frequency, and legal usage have not yet been verified.
- Supabase schema and RLS policies are not designed yet.
- Google Sheets authentication and import method are not designed yet.
- Analysis formulas and market-regime thresholds are not approved yet.
- Bitcoin exposure is not approved for MVP implementation without a separate decision.

## Exact Next Recommended Task

Complete the remaining required specification documents in Draft PR #1, beginning with `docs/ANALYSIS_SPEC.md`, `docs/PORTFOLIO_SPEC.md`, and `docs/DATA_SOURCES.md`. Then align database, API, security, operations, and test specifications to those contracts before expanding the README.
