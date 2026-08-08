# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, remotely deployed persistence schema evidence, and active provenance-preserving cache work.

PR #55 merged as `3ea639233da1d8d42e7ce9e4ff34d3ea9240cb26`; Issue #53 closed. Remote persistence and follow-up covering-index evidence are documented on `main`.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/cache-executor`
- Issue: #57 — `feat: add provenance-preserving cache executor`
- Draft PR: #58 — `feat: add provenance-preserving cache executor`

## Active Implementation

- `investment_manager/data/cache.py` adds `CacheExecutor` and `CacheExecution`.
- Cache identity includes provider plus the complete canonical `FetchRequest` boundary.
- `DatasetPolicy.cache_ttl` controls process-local cache lifetime.
- Only fully successful `FetchResult` values are cached; partial and failed results are not cached.
- Exact expiry triggers a provider call.
- Expired data is not returned as an implicit stale-on-error fallback.
- Cache hits return the stored canonical result without rewriting observation identity, Decimal values, quality, freshness, source metadata, or `retrieved_at`.
- Cache timing metadata (`cached_at`, `expires_at`) is UTC-aware execution metadata and is not provider provenance.
- `docs/CACHE_EXECUTOR.md` defines the provenance/freshness boundary and deferred distributed-cache behavior.

## Validation Status

- Initial implementation/documentation head `b825dcc4bf2c391becfc700de466b8902f9c7b93`: Python run #87 and Documentation run #146 passed.
- Deterministic cache tests cover miss/hit, exact expiry, request/provider isolation, partial/failed non-caching, stale-on-error exclusion, dataset mismatch, UTC validation, provider-result mismatch, and exact provenance preservation.
- Latest-head CI must be re-run after living-document updates before PR #58 is Ready for Review.

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

Finish latest-head Python and Documentation CI for PR #58. If both pass, update the PR validation evidence and mark Ready for Review. Stop for explicit user merge approval. After merge, proceed to scheduled ingestion and operational status reporting.
