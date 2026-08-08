# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, and remotely deployed persistence schema evidence.

PR #47 merged as `b68388ffbe3b16e00fa51d224f02564ab6bf3c62`; Issue #46 closed. PR #51 merged as `46b209f7c824c3a439ecb26a2fd20559ad8462f9`; Issue #50 is expected to close through the merged PR.

## Verified Remote Persistence Evidence

- Supabase project: `xztjjgzpryrfcppqkbdo`.
- Migration `data_platform_persistence` was applied successfully.
- `data_observations`, `source_snapshots`, and `source_snapshot_observations` exist with expected `numeric`, `timestamptz`, UUID, and `jsonb` storage.
- Primary keys, foreign keys, ordered-membership uniqueness, checksum/publication-order checks, and retrieval-order checks were verified remotely.
- RLS is enabled on all three data-platform tables and there are intentionally no client-facing policies.
- A bounded remote smoke inserted one temporary observation/snapshot/membership, replayed identical observation content without duplication, verified PostgreSQL preserved `123.45`, confirmed a conflicting same-ID insert is rejected, and removed all smoke rows afterward.
- Migration `snapshot_observation_fk_index` was then applied successfully after PR #51 merged.
- Supabase performance advisor no longer reports the prior unindexed foreign-key finding for `source_snapshot_observations.observation_id`.
- Remaining performance notices are `unused_index` INFO entries on newly created/empty tables; they are not evidence that intended indexes should be removed.
- This evidence validates deployed schema/persistence primitives. It does not yet prove the Python `SnapshotRepository` through a live PostgreSQL driver.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Documentation reconciliation issue: #52 — `docs: reconcile post-index persistence state`
- Stale PR #49 predates the verified remote deployment and should not be merged.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit or log database URLs, passwords, service-role credentials, provider secrets, raw payloads, or personal investment data.
3. Financial values remain `Decimal`; persisted financial values use PostgreSQL `numeric`.
4. Datetimes remain timezone-aware and UTC-normalized; persistence uses `timestamptz`.
5. Immutable identity conflicts fail closed; never overwrite them silently.
6. Substantial PRs begin as Draft.
7. Never merge without explicit user approval for that specific PR.
8. Never claim a remote migration, smoke, advisor fix, or live provider result without actual execution evidence.

## Exact Next Recommended Task

Reconcile the remaining living documentation and close stale PR #49 as superseded. After documentation CI passes, stop at Ready for Review for the reconciliation PR. The next functional milestone is cache execution with preserved provenance unless a separate product decision reprioritizes Phase 2 work.
