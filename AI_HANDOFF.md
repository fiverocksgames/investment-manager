# AI Handoff

## Current State

Investment Manager is in Phase 1 — Infrastructure. The fork now contains the complete validated frontend and Supabase authentication baseline, including GitHub Actions wiring for the public Supabase build variables.

## Repository and Active Work

- Temporary authoritative repository: `fiverocksgames/investment-manager`
- Intended upstream repository: `e20cboy/investment-manager`
- Default branch: `main`
- Active branch: `agent/upstream-sync-prep`
- Issue: #9 — `docs: prepare fork for upstream synchronization`
- Previous merged PRs: #4, #6, #8

The immediate goal is a one-time forced synchronization in which the fork version is authoritative and conflicting upstream Phase 0 content may be discarded.

## Implemented Baseline

- React 19, TypeScript, and Vite application shell.
- Tailwind CSS and PostCSS configuration.
- PWA registration and generated manifest.
- GitHub Pages build and deployment workflow.
- Supabase browser client using public Vite variables.
- Authentication context with initial session restoration and auth-state subscription.
- Google sign-in and sign-out actions.
- Safe missing-configuration UI state.
- GitHub Actions Variables wiring for `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`.
- Supabase setup, security, traceability, Worklog, and Changelog documentation.

## Validation Evidence

- Frontend run #18 passed after the GitHub Variables workflow change.
- Earlier frontend and documentation runs passed dependency installation, production build, required-document checks, Markdown lint, and link validation.
- PR builds succeeded without Supabase variables, proving the safe unconfigured fallback.

This does not prove real Google OAuth, browser session persistence, GitHub Pages deployment, or database authorization.

## Upstream Synchronization Procedure

1. Merge the final synchronization-preparation PR into the fork `main`.
2. Create a browser-based cross-repository PR from `fiverocksgames:main` to `e20cboy:main`.
3. Resolve conflicts by keeping the fork version as authoritative.
4. Confirm all React, Supabase, workflow, and documentation files are present.
5. Run upstream CI and merge after success.
6. Synchronize the fork from upstream after the one-time replacement.
7. For future work, create feature branches in the fork and open upstream PRs directly from those branches without first merging them into fork `main`.

## Security Boundaries

- Only `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` may enter the frontend build.
- Never commit service-role keys, database passwords, Google client secrets, JWT secrets, or personal portfolio data.
- Authentication proves identity but does not authorize user data access.
- User-owned tables require default-deny Row Level Security and isolation tests.

## Known Limitations

- No real Supabase project or Google provider is connected.
- GitHub repository Variables are not yet configured in the final upstream repository.
- OAuth callback, session restoration, and sign-out are not browser-verified.
- No protected routes, user-owned tables, RLS policies, or isolation tests exist.
- No `package-lock.json` is committed; CI uses `npm install`.
- GitHub Pages deployment and PWA offline behavior remain unverified.

## Development Rules

1. Read `PROJECT_CHARTER.md`, `AGENTS.md`, `WORKLOG.md`, and this file first.
2. Follow Issue → Design → Documentation → Implementation → Test → PR.
3. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md`.
4. Keep financial calculations outside the UI.
5. Never commit secrets or personal portfolio data.
6. Update Worklog and Handoff in every PR.
7. Never claim validation without evidence.

## Run and Test Instructions

```text
npm install
npm run dev
npm run build
```

For local authentication, copy `.env.example` to `.env.local`, use only the browser-safe project URL and publishable key, and follow `docs/SUPABASE_SETUP.md`.

## Exact Next Recommended Task

Complete the one-time upstream synchronization, verify upstream CI, then configure Supabase, Google OAuth, GitHub Actions Variables, and browser-level authentication in a separate tracked task.
