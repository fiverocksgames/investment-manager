# AI Handoff

## Current State

Phase 2 now has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, and remotely deployed persistence schema evidence.

PR #47 merged as `b68388ffbe3b16e00fa51d224f02564ab6bf3c62`; Issue #46 closed. PR #51 merged as `46b209f7c824c3a439ecb26a2fd20559ad8462f9`; Issue #50 closed. The initial persistence migration and follow-up foreign-key covering-index migration have both been applied to Supabase project `xztjjgzpryrfcppqkbdo`.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/persistence-index-evidence`
- Issue: #53 — `docs: record remote persistence index validation evidence`
- Draft PR: to be opened for evidence-only documentation

## Verified Remote Persistence Evidence

- Supabase migration `data_platform_persistence` is recorded remotely.
- `data_observations`, `source_snapshots`, and `source_snapshot_observations` exist with expected `numeric`, `timestamptz`, UUID, and `jsonb` storage.
- Primary keys, foreign keys, ordered-membership uniqueness, checksum/publication-order checks, and retrieval-order checks were verified remotely.
- RLS is enabled on all three data-platform tables and there are intentionally no client-facing policies.
- A bounded remote smoke inserted one temporary observation/snapshot/membership, replayed identical observation content without duplication, verified PostgreSQL preserved `123.45`, confirmed a conflicting same-ID insert is rejected, and removed all smoke rows afterward.
- This does not yet prove the Python `SnapshotRepository` against a live PostgreSQL driver; the smoke validated the deployed schema and persistence primitives directly.

## Verified Follow-up Index Evidence

- `supabase/migrations/202608080002_snapshot_observation_fk_index.sql` creates `source_snapshot_observations_observation_id_idx` with `create index if not exists`.
- The follow-up migration was applied remotely after PR #51 merged.
- Supabase performance advisor no longer reports `unindexed_foreign_keys` for `source_snapshot_observations.observation_id`.
- Remaining `unused_index` notices are informational and expected for newly created/empty data-platform tables.
- Supabase migration history currently contains two entries named `snapshot_observation_fk_index` with different versions. The SQL is idempotent so schema state is correct; the duplicate history entry is documented and must not be silently rewritten.
- RLS-without-policy notices remain expected for the server-managed deny-by-default design.
- The separate leaked-password-protection Auth warning is outside this persistence work and requires a dedicated security decision.

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

Open a Draft evidence-only PR for Issue #53, run Documentation CI, and mark Ready for Review only if the latest head passes. Stop for explicit user merge approval. After merge, continue with the next Phase 2 milestone; live Python `SnapshotRepository` connectivity remains a separate future task unless intentionally prioritized.
