# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, remotely deployed persistence schema evidence, and a merged provenance-preserving Cache Executor.

PR #58 merged as `74dd4e4da743b6ce0d9d2f0760edc7b640f197a4`; Issue #57 closed. Final PR head `4c2f472ba8e45497650233067a80d197ad4f5468` passed Python run #93 and Documentation run #152 before merge.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active reconciliation branch: `agent/post-cache-merge-reconcile`
- Issue: #59 — `docs: reconcile post-cache merge active state`
- Runtime feature PRs: none open at reconciliation start

## Verified Cache Executor State

- `investment_manager/data/cache.py` provides `CacheExecutor` and `CacheExecution`.
- Cache identity includes provider plus the complete canonical `FetchRequest` boundary.
- `DatasetPolicy.cache_ttl` controls process-local cache lifetime.
- Only fully successful `FetchResult` values are cached; partial and failed results are not cached.
- Exact expiry triggers a provider call.
- Expired data is not returned as an implicit stale-on-error fallback.
- Cache hits preserve observation identity, Decimal values, observed/retrieved timestamps, quality, freshness, revision, and source attributes exactly.
- Cache timing metadata is timezone-aware UTC execution metadata and remains separate from source freshness and provider provenance.
- No Redis/distributed cache, persistence, background refresh, stale-on-error, provider fallback, scheduler integration, or UI behavior is implied by this milestone.

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
5. Cache reuse must never rewrite freshness or provenance.
6. Partial/failed provider outcomes must not silently become cached trusted data.
7. Substantial PRs begin as Draft.
8. Never merge without explicit user approval.

## Exact Next Recommended Task

After this documentation reconciliation passes Documentation CI and is merged with explicit approval, proceed to the next Phase 2 milestone: scheduled ingestion and operational status reporting. That milestone should begin with a scoped Issue and design for safe scheduling, run-status evidence, failure reporting, secret handling, and manual/provider smoke boundaries before implementation.
