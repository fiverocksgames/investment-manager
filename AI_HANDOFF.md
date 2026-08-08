# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, remotely deployed base persistence schema evidence, a merged provenance-preserving cache executor, merged scheduled-ingestion orchestration, and a merged production-scheduling/durable-status implementation.

PR #64 merged as `0ed5753bcf2bd31db4c768b953a3d34536ec8409`; Issue #63 closed. There are currently no open pull requests. Source/CI implementation is complete for the first Yahoo SPY production scheduling path, but production-live scheduler validation is not complete.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Reconciliation branch: `agent/post-production-scheduler-reconcile`
- Issue: #65 — `docs: reconcile post-production-scheduler merge state`
- No functional implementation PR is currently active.

## Merged Production Scheduling Implementation

- `investment_manager/data/ingestion.py` preserves actual provider-attempt evidence from bounded retry through `IngestionFetchExecution`.
- Catch-all ingestion failures are sanitized to exception type only; raw exception strings are not persisted.
- `investment_manager/data/operational_status.py` provides atomic/idempotent `IngestionStatusRepository` persistence for terminal runs and ordered failures.
- Migration `202608080003_ingestion_operational_status.sql` defines server-managed `ingestion_runs` and `ingestion_failures`, with RLS enabled and no client-facing policies.
- `pyproject.toml` provides the optional `postgres` runtime dependency using psycopg 3.
- `investment_manager/jobs/scheduled_yahoo.py` is the first production job entrypoint: Yahoo SPY daily, 10-day request window, three-attempt bounded retry, immutable snapshot persistence, then durable run status.
- `.github/workflows/scheduled-yahoo-ingestion.yml` supports manual dispatch and weekday UTC cron `45 23 * * 1-5`, runs only on `main`, and reads database connectivity only from the `SUPABASE_DB_URL` repository secret.
- Console output is limited to safe operational identifiers/status/counts; observation values and connection strings are never printed.

## Validation Status

- PR #64 final head `e05f9a0e016cca1e26961893a9d84b227507037a`: Python run #110 and Documentation run #168 passed before merge.
- PR #64 merged as `0ed5753bcf2bd31db4c768b953a3d34536ec8409`.
- Deterministic tests cover durable terminal status persistence, identical replay, conflicting run identity rollback, non-terminal rejection, provider-attempt propagation, sanitized secret-like exceptions, workflow trigger/secret boundaries, and optional PostgreSQL dependency configuration.
- Production-live scheduler validation is **not complete**.

## Production-Live Validation Still Required

Do not claim production scheduled ingestion success until all are verified:

1. Apply `202608080003_ingestion_operational_status.sql` to Supabase project `xztjjgzpryrfcppqkbdo`.
2. Configure GitHub repository secret `SUPABASE_DB_URL` with a GitHub-runner-reachable PostgreSQL connection string.
3. Manually dispatch `Scheduled Yahoo Ingestion` on `main`.
4. Verify the workflow succeeds.
5. Verify the corresponding `ingestion_runs` row and snapshot linkage remotely.

Current GitHub connector capabilities do not expose repository-secret creation or generic manual workflow dispatch, so steps 2 and 3 require user/manual GitHub actions unless another connected capability becomes available.

## Persistent Data Platform Evidence

- Initial persistence and follow-up covering-index migrations are already applied to Supabase project `xztjjgzpryrfcppqkbdo`.
- Supabase performance advisor no longer reports the previously observed unindexed foreign key.
- Duplicate remote migration-history entries named `snapshot_observation_fk_index` remain documented; schema state is correct because that migration uses `CREATE INDEX IF NOT EXISTS`.
- The operational-status migration is source-controlled on `main` but has not yet been remotely applied and must not be described as deployed.

## Known Boundary

Snapshot persistence and durable ingestion-status persistence are separate transactions. A committed snapshot can exist even if subsequent status persistence fails. The workflow fails visibly in that case, but there is not yet one cross-table transaction spanning both repositories.

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

Finish Issue #65 documentation reconciliation and latest-head Documentation CI. If it passes, mark the documentation PR Ready for Review and stop for merge approval. After that merge, the next functional step is protected production-live validation: apply the operational-status migration, configure `SUPABASE_DB_URL`, manually dispatch `Scheduled Yahoo Ingestion`, and inspect the durable run evidence.