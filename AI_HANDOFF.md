# AI Handoff

## Current State

Investment Manager is in Phase 1 — Infrastructure. Phase 0 governance is complete, and Draft PR #4 contains the first runnable frontend baseline using React, TypeScript, Vite, Tailwind CSS, PWA support, and GitHub Pages automation.

## Repository and Active Work

- Repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/phase-1-frontend`
- Issue: #3 — `feat: bootstrap Phase 1 frontend platform`
- Pull request: #4 — `feat: bootstrap Phase 1 frontend platform`
- PR state: Draft pending final documentation and review

## Completed in PR #4

- React 19 application shell.
- TypeScript and Vite build configuration.
- Tailwind CSS and PostCSS configuration.
- PWA registration and generated manifest configuration.
- GitHub Actions frontend build validation.
- GitHub Pages artifact and deployment jobs for pushes to `main`.
- Responsive UI that states which capabilities are not connected.
- Architecture and feature traceability updates.

## Validation Evidence

Frontend run #2, run ID `31003228610`, completed successfully.

- Checkout: passed.
- Node.js 22 setup: passed.
- `npm install`: passed.
- `npm run build`: passed.
- Artifact upload and deployment were skipped as expected for a pull request.

Frontend run #1 failed due to an incompatible optional PWA assets generator dependency. The unused package was removed; no force or legacy peer-dependency bypass was introduced.

## Required Before Merge

1. Confirm Frontend and Documentation workflows pass on the latest PR head.
2. Review the application shell, Vite base path, PWA configuration, and Pages workflow.
3. Resolve review findings.
4. Mark the PR ready for review only after pre-merge checks pass.
5. Merge after approval.

## Required After Merge

1. Verify the push-to-`main` workflow uploads the Pages artifact.
2. Verify GitHub Pages deployment succeeds and the site loads under `/investment-manager/`.
3. Validate PWA installation and offline behavior in a supported browser.
4. Record deployment evidence in Worklog and Handoff.

## Known Limitations

- No `package-lock.json` is committed.
- CI currently uses `npm install`, not `npm ci`.
- No authentication, database, market data, portfolio, or recommendation integration exists.
- No browser-level PWA or accessibility validation has been completed.
- Successful PR CI does not prove production deployment.

## Development Rules

1. Read `PROJECT_CHARTER.md`, `AGENTS.md`, `WORKLOG.md`, and this file first.
2. Follow Issue → Design → Documentation → Implementation → Test → PR.
3. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md`.
4. Keep financial calculations outside the UI.
5. Never commit secrets or personal portfolio data.
6. Update Worklog and Handoff in every PR.
7. Never claim validation without evidence.

## Run and Test Instructions

Current expected commands:

```text
npm install
npm run dev
npm run build
```

Only `npm install` and `npm run build` have been verified in GitHub Actions. Local development and browser behavior have not been independently verified.

## Exact Next Recommended Task

Inspect the latest PR #4 workflow results after the documentation commits. Resolve any failures, update the PR body with final evidence, and mark the PR ready for review when all pre-merge checks pass.
