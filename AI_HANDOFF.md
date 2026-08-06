# AI Handoff

## Current State

Investment Manager has completed Phase 1 infrastructure and authentication and adopted Project Development Policy v1. Phase 2 Data Platform design is active in the canonical repository.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/phase-2-data-platform-design`
- Issue: #15 — `docs: design Phase 2 data platform`
- PR: not yet created

All Issues, branches, pull requests, CI evidence, reviews, merges, and project records remain in the canonical repository.

## Governing Documents

Read these before changing behavior:

- `PROJECT_CHARTER.md`
- `PROJECT_POLICY.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `docs/INVESTMENT_POLICY.md`
- `WORKLOG.md`
- `docs/FEATURE_MATRIX.md`

The repository is the single source of truth.

## Completed Baseline

- React, TypeScript, Vite, Tailwind CSS, and PWA shell.
- GitHub Pages build and deployment.
- Supabase Auth with Google OAuth.
- Session restoration after refresh and browser restart.
- Sign-out and safe missing-configuration behavior.
- Project Development Policy v1 in PR #14 with Documentation run #41.

## Active Phase 2 Design

Issue #15 defines the provider-independent Data Platform before implementation. The branch currently contains:

- `docs/DATA_MODEL.md` with canonical assets, aliases, series, observations, dataset policies, cache policies, retry policies, ingestion runs, failures, quality states, freshness states, and source snapshots.
- `docs/ARCHITECTURE.md` with provider adapter, validation, normalization, cache, persistence, operations, and snapshot boundaries.
- `docs/DATA_SOURCES.md` with Yahoo Finance, FRED, ECOS, FX, freshness, cache, retry, and fallback rules.
- `docs/DATABASE.md` with planned Phase 2 reference, observation, operational, and snapshot tables.
- `docs/API_SPEC.md` with internal provider contracts and canonical read envelopes.
- `docs/OPERATIONS.md` with concurrency, idempotency, retries, observability, run states, and recovery rules.
- `docs/TEST_PLAN.md` with deterministic provider contract, integration, cache, freshness, revision, and failure tests.
- `docs/DECISIONS.md` with accepted canonical model, immutable snapshot, and policy-driven freshness decisions.
- `docs/FEATURE_MATRIX.md` with Phase 2 Requirement IDs and traceability.

## Phase 2 Requirements

- `REQ-DATA-001`
- `REQ-DATA-002`
- `REQ-PROVIDER-001`
- `REQ-PROVIDER-002`
- `REQ-OPS-002`

Legacy `REQ-MKT-001`, `REQ-MKT-002`, and `REQ-OPS-001` remain planned implementation requirements.

## Key Design Rules

1. Provider payloads stop at adapter boundaries.
2. Canonical observations preserve provider, source identifier, observation time, retrieval time, unit, currency, quality, freshness, and revision metadata.
3. Failed runs never publish successful source snapshots.
4. Prior good data retains its original timestamps and may appear only with explicit stale state.
5. Cache entries preserve provenance and cannot imply freshness.
6. Retries are bounded and apply only to retryable failure categories.
7. Analysis consumes an immutable source snapshot identifier and cutoff.
8. The UI performs no provider normalization or financial calculations.

## Security Boundaries

- Provider and service-role credentials remain server-side in trusted jobs.
- No secret enters the frontend bundle or repository.
- Public observations and private portfolio data remain separate authorization domains.
- User-owned tables require default-deny RLS and cross-user isolation tests before use.

## Known Limitations

- Phase 2 is design-only; no provider adapter or ingestion workflow exists.
- No database migration has been created for the Phase 2 model.
- Current provider access methods, terms, identifiers, and rate limits require implementation-time verification.
- No protected routes or user-owned application tables exist.
- No RLS policies or cross-user isolation tests exist.
- No `package-lock.json` is committed; frontend CI uses `npm install`.
- PWA installation and offline behavior remain unverified.

## Development Rules

1. Follow `PROJECT_POLICY.md`.
2. Work from an Issue and stable Requirement IDs.
3. Update specifications before implementation.
4. Keep provider formats and financial calculations out of the UI.
5. Never commit secrets or personal portfolio data.
6. Update Worklog, Handoff, Changelog, and Feature Matrix in substantial PRs.
7. Never claim validation without evidence.
8. Never merge without explicit user approval.

## Run and Test Instructions

```text
npm install
npm run dev
npm run build
```

Phase 2 Python commands do not yet exist and must not be invented before the implementation baseline is added.

## Exact Next Recommended Task

Complete Issue #15 by updating the living documents, creating a Draft PR, and passing Documentation CI. After approval and merge, create a focused Issue for the Python provider abstraction and canonical domain-model implementation before adding Yahoo Finance, FRED, ECOS, or FX adapters.
