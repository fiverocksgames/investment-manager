# AI Handoff

## Current State

Phase 2 now has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, and active persistence/idempotency work.

PR #45 merged as `878f0bb69cf0df70de12898b42ec4f8e25786320`; Issue #44 closed. Snapshot publication is deterministic and in-memory.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/persistence-idempotency`
- Issue: #46 — `feat: add persistence and idempotent snapshot storage`
- Draft PR: #47 — `feat: add persistence and idempotent snapshot storage`

## Active Implementation

- `investment_manager/data/persistence.py` adds `SnapshotRepository`, `PersistenceResult`, and `PersistenceError` behind an injected DB-API-compatible connection factory.
- `supabase/migrations/202608080001_data_platform_persistence.sql` adds server-managed canonical observation, source snapshot, and ordered membership tables.
- Financial values use PostgreSQL `numeric`; canonical times use `timestamptz`; provider attributes use `jsonb`.
- Identical immutable identity replay is idempotent. Same-ID conflicting content fails closed and is never overwritten.
- Observations, snapshot, and exact ordered membership are one transaction; any persistence failure rolls back all writes.
- RLS is enabled on the three data-platform tables with no client-facing policies, so browser access remains denied by default.
- `tests/test_persistence.py` uses a deterministic fake DB to cover atomic write, replay, conflicts, rollback, Decimal preservation, UTC timestamps, and membership validation.
- `docs/PERSISTENCE.md` defines transaction, immutability, secret, RLS, and migration-validation boundaries.

## Validation Status

- Initial implementation head `42d2b8414a54dc75930bad3dd233d636c6ce4f5c`: Python run #78 and Documentation run #130 passed.
- The remote Supabase migration has **not** been applied or live-validated. Committed SQL is not evidence of remote schema deployment.
- Final living-document updates require a fresh latest-head Python and Documentation CI gate before Ready for Review.

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

Complete operations/test/traceability/worklog/changelog updates for PR #47, run Python and Documentation CI on the final head, and mark Ready for Review only if both pass. Stop for explicit user merge approval. After merge, apply and validate the migration against the protected Supabase project as a separate evidence step before calling persistence remotely deployed.
