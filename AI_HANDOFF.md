# AI Handoff

## Current State

Phase 2 now has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, and remotely deployed persistence schema evidence.

PR #47 merged as `b68388ffbe3b16e00fa51d224f02564ab6bf3c62`; Issue #46 closed. The initial persistence migration has been applied successfully to Supabase project `xztjjgzpryrfcppqkbdo` and the remote schema was inspected.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/persistence-fk-index`
- Issue: #50 — `fix: add covering index for snapshot observation foreign key`
- Active PR: not yet opened at this handoff update

## Verified Remote Persistence Evidence

- Supabase migration `data_platform_persistence` is recorded remotely.
- `data_observations`, `source_snapshots`, and `source_snapshot_observations` exist with expected `numeric`, `timestamptz`, UUID, and `jsonb` storage.
- Primary keys, foreign keys, ordered-membership uniqueness, checksum/publication-order checks, and retrieval-order checks were verified remotely.
- RLS is enabled on all three data-platform tables and there are intentionally no client-facing policies.
- A bounded remote smoke inserted one temporary observation/snapshot/membership, replayed identical observation content without duplication, verified PostgreSQL preserved `123.45`, confirmed a conflicting same-ID insert is rejected, and removed all smoke rows afterward.
- This does not yet prove the Python `SnapshotRepository` against a live PostgreSQL driver; the smoke validated the deployed schema and persistence primitives directly.

## Active Follow-up

- Supabase performance advisor reported one actionable finding: `source_snapshot_observations.observation_id` lacked a covering index.
- `supabase/migrations/202608080002_snapshot_observation_fk_index.sql` adds `source_snapshot_observations_observation_id_idx` with `create index if not exists`.
- RLS-without-policy notices are expected for the server-managed deny-by-default design.
- Existing unused-index notices are expected on the newly created empty tables and are not removal signals.
- The separate leaked-password-protection Auth warning is outside this persistence migration and requires a dedicated security decision.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit or log database URLs, passwords, service-role credentials, provider secrets, raw payloads, or personal investment data.
3. Financial values remain `Decimal`; persisted financial values use PostgreSQL `numeric`.
4. Datetimes remain timezone-aware and UTC-normalized; persistence uses `timestamptz`.
5. Immutable identity conflicts fail closed; never overwrite them silently.
6. Substantial PRs begin as Draft.
7. Never merge without explicit user approval.
8. Never claim a remote migration or advisor fix succeeded without actual execution evidence.

## Exact Next Recommended Task

Open a Draft PR for Issue #50, run applicable CI, and mark Ready for Review only after latest-head evidence succeeds. Stop for explicit user merge approval. After merge, apply the follow-up index migration to the protected Supabase project and re-run the performance advisor before claiming the foreign-key warning resolved.
