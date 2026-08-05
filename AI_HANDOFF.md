# AI Handoff

## Current State

Investment Manager has completed Phase 1 infrastructure and authentication. The canonical development repository is now `fiverocksgames/investment-manager`. Phase 2 Data Platform design is the next product-development objective after Project Development Policy v1 is merged.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/project-policy-v1`
- Issue: #13 — `docs: establish project development policy v1`
- PR: not yet created

All Issues, branches, pull requests, CI evidence, reviews, merges, and project records are maintained in the canonical repository. External repositories are not part of the normal development workflow.

## Governing Documents

Read these before changing behavior:

- `PROJECT_CHARTER.md`
- `PROJECT_POLICY.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `docs/INVESTMENT_POLICY.md`
- `WORKLOG.md`
- `docs/FEATURE_MATRIX.md`

The repository is the single source of truth. Important decisions must not exist only in conversation history.

## Completed Phase 1 Baseline

- React 19, TypeScript, and Vite application shell.
- Tailwind CSS and PostCSS configuration.
- PWA registration and generated manifest.
- GitHub Pages build and deployment workflow.
- Supabase browser client using public Vite variables.
- Authentication context with initial session restoration and auth-state subscription.
- Google sign-in and sign-out.
- Safe missing-configuration UI state.
- GitHub Actions Variables wiring for `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`.
- Supabase setup, security, traceability, Worklog, and Changelog documentation.

## Validation Evidence

The deployed application has been manually verified for:

- Successful GitHub Pages deployment.
- Supabase configuration detection after repository Variables were added and a new build was deployed.
- Successful Google OAuth sign-in and callback.
- Session persistence after page refresh.
- Session persistence after closing and reopening the browser.
- Successful sign-out.

PWA installation and offline behavior have not been browser-verified.

## Current Policy Work

Issue #13 establishes:

- `fiverocksgames/investment-manager` as the canonical repository.
- Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close.
- No direct commits to `main`.
- Draft PR and explicit user-approval requirements.
- Constitution and living-document classifications.
- Requirement traceability and AI handoff requirements.

## Security Boundaries

- Only `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` may enter the frontend build.
- Never commit service-role keys, database passwords, Google client secrets, JWT secrets, or personal portfolio data.
- Authentication proves identity but does not authorize user data access.
- User-owned tables require default-deny Row Level Security and cross-user isolation tests before use.

## Known Limitations

- No protected routes or user-owned application tables exist.
- No RLS policies or cross-user isolation tests exist.
- No `package-lock.json` is committed; CI uses `npm install`.
- PWA installation and offline behavior remain unverified.
- Market data, macro data, FX data, portfolio analysis, indicators, and recommendation capabilities are not implemented.

## Development Rules

1. Follow `PROJECT_POLICY.md`.
2. Work from an Issue and stable Requirement IDs for substantial changes.
3. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md` when requirements or evidence change.
4. Keep financial calculations outside the UI.
5. Never commit secrets or personal portfolio data.
6. Update Worklog, Handoff, and Changelog in every substantial PR.
7. Never claim validation without evidence.
8. Never merge without explicit user approval.

## Run and Test Instructions

```text
npm install
npm run dev
npm run build
```

For local authentication, copy `.env.example` to `.env.local`, use only the browser-safe project URL and publishable key, and follow `docs/SUPABASE_SETUP.md`.

## Exact Next Recommended Task

Complete Issue #13 by creating a Draft PR, verifying Documentation CI, and requesting user approval before merge. After merge, create the Phase 2 Data Platform design Issue and define provider-independent schemas for assets, observations, source metadata, retrieval timestamps, freshness status, and ingestion failures before implementing provider adapters.
