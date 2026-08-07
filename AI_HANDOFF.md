# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, and merged transactional persistence/idempotency contracts.

PR #47 merged as `b68388ffbe3b16e00fa51d224f02564ab6bf3c62`; Issue #46 closed. The repository now contains the server-managed persistence schema and `SnapshotRepository`, but the Supabase migration has **not** been applied to the remote project.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active follow-up: Issue #48 — `docs: reconcile post-merge persistence living state`
- Active branch: `agent/post-merge-persistence-docs`
- Next functional milestone: protected remote Supabase migration/application validation

## Merged Persistence Implementation

- `investment_manager/data/persistence.py` provides `SnapshotRepository`, `PersistenceResult`, and `PersistenceError` behind an injected DB-API-compatible connection factory.
- `supabase/migrations/202608080001_data_platform_persistence.sql` defines server-managed canonical observation, source snapshot, and ordered membership tables.
- Financial values use PostgreSQL `numeric`; canonical times use `timestamptz`; provider attributes use `jsonb`.
- Identical immutable identity replay is idempotent. Same-ID conflicting content fails closed and is never overwritten.
- Observations, snapshot, and exact ordered membership publish in one transaction; any persistence failure rolls back all writes.
- RLS is enabled on the three data-platform tables with no client-facing policies, so browser access remains denied by default.

## Validation Status

- PR #47 initial implementation head `42d2b8414a54dc75930bad3dd233d636c6ce4f5c`: Python run #78 and Documentation run #130 passed.
- PR #47 final evidence head `e88e59e8c5b86d439bfa7521d8f4e00a36c7314f`: Python run #85 and Documentation run #137 passed.
- PR #47 merged to `main` as `b68388ffbe3b16e00fa51d224f02564ab6bf3c62` and Issue #46 closed.
- The remote Supabase migration has **not** been applied or live-validated. Committed SQL is not evidence of remote schema deployment.
- ECOS Live Smoke run `31182329368` already succeeded on merged `main` with 99 trusted observations on attempt 1; no new ECOS action is currently pending.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit or log database URLs, passwords, service-role credentials, provider secrets, raw payloads, or personal investment data.
3. Financial values remain `Decimal`; persisted financial values use PostgreSQL `numeric`.
4. Datetimes remain timezone-aware and UTC-normalized; persistence uses `timestamptz`.
5. Immutable identity conflicts fail closed; never overwrite them silently.
6. Substantial PRs begin as Draft.
7. Never merge without explicit user approval.
8. Never claim remote migration success without actual execution evidence.

## Exact Next Recommended Task

Apply `supabase/migrations/202608080001_data_platform_persistence.sql` to the protected Supabase project and validate the created tables, constraints, RLS state, and idempotent transaction behavior. This requires an authenticated Supabase connection/tool or protected manual execution. Do not make changes that depend on remote database access until that connection is available.
