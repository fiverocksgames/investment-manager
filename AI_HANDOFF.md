# AI Handoff

## Current State

Investment Manager is completing Phase 0 — Foundation. PR #1 contains the
project governance, specifications, repository templates, ownership rules,
documentation CI, and MIT License. Automated documentation validation passes.
No application, database migration, deployment workflow, or application test
suite exists.

## Repository and Active Work

- Repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/project-bootstrap`
- Pull request: #1 — `docs: establish project governance`
- PR state: Ready for Review

## Completed in PR #1

- All 21 required governance and specification documents.
- Feature and bug Issue forms.
- Pull request template with governance and investment-safety checks.
- CODEOWNERS assigning review ownership to `@fiverocksgames`.
- Documentation workflow for required files, Markdown lint, and links.
- MIT `LICENSE` and accepted decision `DEC-008`.
- Markdown lint configuration suited to long specifications and PR templates.

## Validation Evidence

Documentation run #7, run ID `30998869604`, completed successfully.

- Required-document check: passed.
- Markdown lint: 22 files, 0 errors.
- Offline Markdown links: 20 successful, 0 errors.

Run #6 previously failed because default Markdown lint enforced line-length and
PR-template H1 rules. `.markdownlint-cli2.yaml` disables only `MD013` and
`MD041`, after which run #7 passed.

## Required Before Merge

1. Complete human review of MVP-scope consistency.
2. Review investment-safety, freshness, uncertainty, and risk language.
3. Resolve any review findings.
4. Merge only after approval.

Repository settings still requiring review:

- Labels and milestones.
- Branch protection and required checks.
- Secret scanning and dependency-security features.

These settings may be completed before merge or in a linked Phase 0 follow-up
Issue if they do not block the governance baseline.

## Development Rules

1. Read `PROJECT_CHARTER.md`, `AGENTS.md`, `WORKLOG.md`, and this file first.
2. Follow Issue → Design → Documentation → Implementation → Test → PR.
3. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md`.
4. Keep financial calculations outside the UI.
5. Never commit secrets or personal portfolio data.
6. Update Worklog and Handoff in every PR.
7. Never claim validation without evidence.

## Technical Direction

- React, TypeScript, Vite, PWA, and TailwindCSS.
- GitHub Pages hosting.
- Supabase PostgreSQL and Auth.
- Python scheduled jobs through GitHub Actions.
- Google Sheets portfolio input.
- Yahoo Finance, FRED, and ECOS as candidate free data sources, subject to
  current access and terms verification.

## Investment Boundaries

- Conservative, long-term, ETF-first decision support.
- No automated trading, individual-stock recommendations, leverage, inverse
  products, derivatives, margin, or short selling in MVP.
- Outputs must disclose evidence, timestamps, freshness, assumptions,
  uncertainty, rationale, and risks.
- Bitcoin is not approved without a separate policy decision.

## Run and Test Instructions

There is no runnable application or application test suite. Do not invent setup
commands. PR #1 is validated by the `Documentation` GitHub Actions workflow and
human review.

## Exact Next Recommended Task

Review and approve PR #1, then merge it. After merge, create a Phase 1 Issue and
a new focused branch for the React, TypeScript, Vite, PWA, and TailwindCSS
application bootstrap.
