# AI Handoff

## Current State

Investment Manager is in Phase 0 — Foundation. Draft PR #1 contains the governance, specifications, repository templates, ownership rules, documentation CI, and MIT license. No application, database migration, deployment workflow, or application test suite exists.

## Repository and Active Work

- Repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/project-bootstrap`
- Pull request: #1 — `docs: establish project governance`
- PR state: Draft pending CI inspection and human documentation review

## Completed in PR #1

- All 21 required governance and specification documents.
- Feature and bug Issue forms.
- Pull request template with mandatory governance and investment-safety checks.
- CODEOWNERS assigning repository review ownership to `@fiverocksgames`.
- Documentation workflow that checks required files, Markdown lint, and offline Markdown links.
- MIT `LICENSE` and accepted decision `DEC-008`.

## Required Before Merge

1. Inspect the GitHub Actions result for the latest PR head.
2. Fix every documentation lint or link failure.
3. Review charter, PRD, feature matrix, specifications, and investment policy for scope consistency.
4. Confirm the PR body records only validations actually performed.
5. Update `WORKLOG.md`, this file, and the PR description with final evidence.
6. Mark the PR ready for review only after the above pass.

Repository settings still requiring review, either before merge or in a linked follow-up Issue:

- Labels and milestones.
- Branch protection and required checks.
- Secret scanning and dependency/security features.

## Development Rules

1. Read `PROJECT_CHARTER.md`, `AGENTS.md`, `WORKLOG.md`, and this file first.
2. Follow Issue → Design → Documentation → Implementation → Test → PR.
3. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md`.
4. Keep financial calculations outside the UI.
5. Never commit secrets or personal portfolio data.
6. Update Worklog and Handoff in every PR.
7. Never claim a command or CI check passed without evidence.

## Technical Direction

- React, TypeScript, Vite, PWA, TailwindCSS.
- GitHub Pages hosting.
- Supabase PostgreSQL and Auth.
- Python scheduled jobs through GitHub Actions.
- Google Sheets portfolio input.
- Yahoo Finance, FRED, and ECOS as candidate free sources subject to current access and terms verification.

## Investment Boundaries

- Conservative, long-term, ETF-first decision support.
- No automated trading, individual-stock recommendations, leverage, inverse products, derivatives, margin, or short selling in MVP.
- Outputs must disclose evidence, timestamps, freshness, assumptions, uncertainty, rationale, and risks.
- Bitcoin is not approved for implementation without a separate explicit policy decision.

## Run and Test Instructions

There is no runnable application or application test suite. Do not invent setup commands.

For PR #1, use the `Documentation` GitHub Actions workflow plus human review. The workflow is defined in `.github/workflows/docs.yml`.

## Exact Next Recommended Task

Inspect the latest PR #1 workflow run and changed files. Resolve failures, complete the final documentation review, and then decide whether the PR is ready for review. Phase 1 application bootstrap must use a new Issue and focused branch after this PR is merged.
