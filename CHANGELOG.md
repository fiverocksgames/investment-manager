# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog, and the project will use semantic versioning once releasable software exists.

## [Unreleased]

### Added

- Project governance, specifications, contributor rules, AI handoff, and requirement traceability
- Issue and pull request templates, CODEOWNERS, documentation CI, and MIT License
- React 19, TypeScript, Vite, Tailwind CSS, PWA, and GitHub Pages frontend baseline
- Supabase JavaScript client with guarded browser configuration
- Authentication context for session restoration and auth-state changes
- Google sign-in and sign-out actions
- Authentication-aware application shell and visible configuration/error states
- Placeholder-only `.env.example`
- Supabase project, Google provider, redirect, and security setup guide

### Changed

- Moved the project from Phase 0 governance into Phase 1 infrastructure
- Updated architecture and feature traceability with implemented frontend and authentication evidence
- Removed the unused `@vite-pwa/assets-generator` dependency after CI exposed an incompatible peer dependency
- Clarified that browser-safe Supabase identifiers do not replace Row Level Security

### Validation

- Documentation run #12 passed required-document, Markdown lint, and offline link checks
- Frontend run #7 and Documentation run #26 passed before PR #4 merge
- Frontend run #9 (`31004808492`) passed dependency installation and production build for the initial Supabase authentication implementation

### Known Limitations

- A real Supabase project and Google OAuth provider are not yet configured
- OAuth callback, browser session persistence, and sign-out are not yet verified end to end
- No user-owned database tables or Row Level Security policies exist
- `package-lock.json` is not yet committed, so CI uses `npm install` rather than `npm ci`
- GitHub Pages deployment and browser-level PWA behavior still require verification
- Market data, portfolio, and recommendation capabilities are not connected
