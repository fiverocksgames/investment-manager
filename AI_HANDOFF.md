# AI Handoff

## Current State

Investment Manager is in Phase 1 — Infrastructure. Phase 0 governance and the frontend platform are merged. Draft PR #6 adds the first Supabase authentication integration while deliberately separating build validation from real OAuth validation.

## Repository and Active Work

- Repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/phase-1-auth`
- Issue: #5 — `feat: bootstrap Supabase authentication`
- Pull request: #6 — `feat: bootstrap Supabase authentication`
- PR state: Draft

## Completed in PR #6

- Supabase JavaScript client dependency.
- Guarded client initialization using browser-safe Vite variables.
- `.env.example` with placeholders only.
- Authentication context for session restoration and auth-state subscription.
- Google sign-in and sign-out actions.
- UI states for loading, missing configuration, signed out, signed in, and errors.
- `docs/SUPABASE_SETUP.md` covering project, provider, redirect, and validation setup.
- Security and feature-traceability updates.

## Validation Evidence

Frontend run #9, run ID `31004808492`, completed successfully.

- `npm install`: passed.
- `npm run build`: passed.
- The application built without Supabase environment variables.

This proves compile-time and missing-configuration behavior only. It does not prove Google OAuth, callback routing, session persistence in a browser, or database authorization.

## Required Before Ready for Review

1. Confirm Frontend and Documentation workflows pass on the latest documentation head.
2. Configure a real Supabase project outside the repository.
3. Enable Google as an authentication provider.
4. Add exact localhost and GitHub Pages redirect URLs.
5. Verify sign-in, callback, refresh persistence, error handling, and sign-out.
6. Record the browser validation evidence without committing secrets.
7. Resolve review findings.

## Security Boundaries

- `VITE_SUPABASE_URL` and the publishable or anon key are browser-visible identifiers.
- Service-role keys, database passwords, and Google client secrets never belong in Vite variables.
- Authentication proves identity but does not authorize user data access.
- User-owned tables require default-deny Row Level Security and isolation tests before frontend access.

## Known Limitations

- No real Supabase project or Google provider is connected.
- No protected routes or user-owned database tables exist.
- No RLS policies or cross-user isolation tests exist.
- No `package-lock.json` is committed; CI uses `npm install`.
- GitHub Pages and PWA browser validation remain pending from the previous phase.

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

For local authentication, copy `.env.example` to `.env.local` and use only the
browser-safe project URL and publishable or anon key. Follow
`docs/SUPABASE_SETUP.md`. Do not commit `.env.local`.

## Exact Next Recommended Task

Check the latest Frontend and Documentation workflow results. If green, configure a real Supabase project and Google OAuth provider, then complete browser-level authentication validation before marking PR #6 ready for review.
