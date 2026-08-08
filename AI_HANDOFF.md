# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, remotely deployed persistence schema evidence, and a merged provenance-preserving cache executor.

PR #58 merged as `74dd4e4da743b6ce0d9d2f0760edc7b640f197a4`; Issue #57 closed. Scheduled ingestion orchestration and operational status reporting are now active work.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/scheduled-ingestion`
- Issue: #61 — `feat: add scheduled ingestion orchestration and operational run status`
- Draft PR: #62 — `feat: add scheduled ingestion orchestration and operational status`

## Active Implementation

- `investment_manager/data/ingestion.py` adds `IngestionJob`, `IngestionExecution`, and `IngestionOrchestrator`.
- Jobs explicitly bind provider, canonical request, dataset policy, UTC cutoff, and partial-publication policy.
- Fetch execution can compose the existing cache/retry boundary without rewriting canonical provenance.
- Fully failed fetches publish nothing.
- Partial results remain operationally partial; publication requires explicit permission.
- Immutable snapshot publication filters observations by explicit cutoff before persistence.
- Persistence failure is fail-closed and cannot be reported as accepted/persisted data.
- `docs/SCHEDULED_INGESTION.md` defines scheduling, failure, partial-result, and operational evidence boundaries.

## Validation Status

- Implementation/test head `74a7801c0b8e8d8c55bb58bdba03791b0f2a82d7`: Python run #96 and Documentation run #156 passed.
- Deterministic tests cover success, fully failed fetch, partial denied, partial allowed, persistence failure, cache-hit evidence, and UTC cutoff validation.
- Living-document updates require latest-head CI before PR #62 can be marked Ready for Review.

## Persistent Data Platform Evidence

- Initial persistence and follow-up covering-index migrations are applied to Supabase project `xztjjgzpryrfcppqkbdo`.
- Supabase performance advisor no longer reports the previously observed unindexed foreign key.
- Duplicate remote migration-history entries named `snapshot_observation_fk_index` remain documented; schema state is correct because the migration uses `CREATE INDEX IF NOT EXISTS`.
- Live Python `SnapshotRepository` connectivity remains a separate future task.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit or log database URLs, passwords, service-role credentials, provider secrets, raw payloads, or personal investment data.
3. Financial values remain `Decimal`; persisted financial values use PostgreSQL `numeric`.
4. Datetimes remain timezone-aware and UTC-normalized.
5. Cache/retry/orchestration must never rewrite freshness or provenance.
6. Partial/failed provider outcomes must not silently become trusted published data.
7. Substantial PRs begin as Draft.
8. Never merge without explicit user approval.

## Exact Next Recommended Task

Finish living-document/traceability updates and latest-head Python/Documentation CI for PR #62. If both pass, update PR validation evidence and mark Ready for Review. Stop for explicit user merge approval. After merge, decide and implement the production scheduling/durable run-status mechanism before dataset/snapshot versioning.
