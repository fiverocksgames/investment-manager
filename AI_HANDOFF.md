# AI Handoff

## Current State

Investment Manager has completed Phase 1 infrastructure and authentication. The upstream deployment at `e20cboy/investment-manager` is live on GitHub Pages and has passed end-to-end Google OAuth validation.

## Repository and Active Work

- Working repository: `fiverocksgames/investment-manager`
- Upstream repository: `e20cboy/investment-manager`
- Default branch: `main`
- Active branch: `agent/phase-1-closeout`
- Issue: #11 — `docs: close Phase 1 and prepare Phase 2`

Because the GitHub app can write only to the fork, implement changes in fork feature branches and open upstream PRs manually from those branches to `e20cboy:main`.

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

The upstream deployed application has been manually verified for:

- Successful GitHub Pages deployment.
- Supabase configuration detection after repository Variables were added and a new build was deployed.
- Successful Google OAuth sign-in and callback.
- Session persistence after page refresh.
- Session persistence after closing and reopening the browser.
- Successful sign-out.

PWA installation and offline behavior have not been browser-verified.

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

Create the Phase 2 Data Platform design issue. Define provider-independent schemas for assets, observations, source metadata, retrieval timestamps, freshness status, and ingestion failures before implementing Yahoo Finance, FRED, ECOS, or FX adapters.
