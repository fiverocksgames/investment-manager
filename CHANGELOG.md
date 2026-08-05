# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog, and the project will use semantic versioning once releasable software exists.

## [Unreleased]

### Added

- Project governance, specifications, contributor rules, AI handoff, and requirement traceability
- Issue and pull request templates, CODEOWNERS, documentation CI, and MIT License
- React 19 and TypeScript frontend baseline
- Vite static build configuration
- Tailwind CSS and PostCSS configuration
- PWA registration and manifest generation through `vite-plugin-pwa`
- Responsive Investment Manager application shell
- GitHub Actions frontend build validation
- GitHub Pages artifact and deployment workflow for pushes to `main`

### Changed

- Moved the project from Phase 0 governance into Phase 1 infrastructure
- Updated architecture and feature traceability with implemented frontend evidence
- Removed the unused `@vite-pwa/assets-generator` dependency after CI exposed an incompatible peer dependency

### Validation

- Documentation run #12 passed required-document, Markdown lint, and offline link checks
- Frontend run #2 (`31003228610`) passed dependency installation and production build

### Known Limitations

- `package-lock.json` is not yet committed, so CI uses `npm install` rather than `npm ci`
- GitHub Pages deployment has not yet been verified after a push to `main`
- PWA installation, offline behavior, and browser accessibility require validation
- Authentication, database, market data, portfolio, and recommendation capabilities are not connected
