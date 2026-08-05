# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog, and the project will use semantic versioning once releasable software exists.

## [Unreleased]

### Added

- `PROJECT_POLICY.md` as the durable project development-policy document
- Canonical-repository governance requirements
- Explicit Draft PR, CI, user-approval, merge, and Issue-close controls
- Constitution and living-document classifications
- Project governance, specifications, contributor rules, AI handoff, and requirement traceability
- Issue and pull request templates, CODEOWNERS, documentation CI, and MIT License
- React 19, TypeScript, Vite, Tailwind CSS, PWA, and GitHub Pages frontend baseline
- Supabase JavaScript client with guarded browser configuration
- Authentication context for session restoration and auth-state changes
- Google sign-in and sign-out actions
- Authentication-aware application shell and visible configuration/error states
- Placeholder-only `.env.example`
- Supabase project, Google provider, redirect, and security setup guide
- GitHub Actions repository Variables wiring for `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`

### Changed

- Defined `fiverocksgames/investment-manager` as the canonical development repository
- Standardized the workflow as Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close
- Prohibited direct commits to `main` and merges without explicit user approval
- Clarified that repository documentation, not conversation history, is the single source of truth
- Moved the project from Phase 0 governance through Phase 1 infrastructure and authentication
- Updated architecture and feature traceability with implemented frontend and authentication evidence
- Removed the unused `@vite-pwa/assets-generator` dependency after CI exposed an incompatible peer dependency
- Clarified that browser-safe Supabase identifiers do not replace Row Level Security
- Synchronized the Phase 1 implementation into `e20cboy/investment-manager`
- Set Phase 2 Data Platform design as the next development objective

### Validation

- Documentation run #12 passed required-document, Markdown lint, and offline link checks
- Frontend run #7 and Documentation run #26 passed before PR #4 merge
- Frontend run #15 and Documentation run #33 passed before PR #6 merge
- Frontend run #18 passed the Supabase GitHub Variables workflow change before PR #8 merge
- Upstream GitHub Pages deployment completed successfully
- Google OAuth sign-in and callback completed successfully in the deployed application
- Authenticated session persisted after page refresh and browser restart
- Sign-out completed successfully
- Project Policy v1 documentation CI is pending on Issue #13

### Known Limitations

- No user-owned database tables or Row Level Security policies exist
- Cross-user data isolation has not been tested
- `package-lock.json` is not yet committed, so CI uses `npm install` rather than `npm ci`
- Browser-level PWA installation and offline behavior still require verification
- Market data, portfolio, analysis, and recommendation capabilities are not connected
