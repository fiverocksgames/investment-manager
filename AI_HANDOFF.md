# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, remotely deployed persistence schema evidence, a merged provenance-preserving cache executor, and merged scheduled-ingestion orchestration.

PR #62 merged as `6d2805f2c66fb91e61f87e4264c382c1d94895ad`; Issue #61 closed. Production scheduling plus durable ingestion-run/failure persistence is now active work.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/production-scheduled-ingestion`
- Issue: #63 — `feat: add production scheduling and durable ingestion-run persistence`
- Draft PR: #64 — `feat: add production scheduled ingestion and durable run status`

## Active Implementation

- `investment_manager/data/ingestion.py` adds `IngestionFetchExecution` and propagates actual provider-attempt evidence from bounded retry.
- Catch-all ingestion failures are sanitized to exception type only; raw exception strings are not persisted.
- `investment_manager/data/operational_status.py` adds atomic/idempotent `IngestionStatusRepository` persistence for terminal runs and ordered failures.
- Migration `202608080003_ingestion_operational_status.sql` adds server-managed `ingestion_runs` and `ingestion_failures`, with RLS enabled and no client-facing policies.
- `pyproject.toml` adds optional `postgres` runtime dependency using psycopg 3.
- `investment_manager/jobs/scheduled_yahoo.py` is the first production job entrypoint: Yahoo SPY daily, 10-day request window, 3-attempt bounded retry, immutable snapshot persistence, then durable run status.
- `.github/workflows/scheduled-yahoo-ingestion.yml` supports manual dispatch and weekday UTC cron `45 23 * * 1-5`, runs only on `main`, and reads database connectivity only from the `SUPABASE_DB_URL` repository secret.
- Console output is limited to safe operational identifiers/status/counts; observation values and connection strings are never printed.

## Validation Status

- Initial implementation/test head `e66e7e97b8b7171479a88f7180cf4602ca387fab`: Python run #101 passed.
- Deterministic tests cover durable terminal status persistence, identical replay, conflicting run identity rollback, non-terminal rejection, provider-attempt propagation, sanitized secret-like exceptions, workflow trigger/secret boundaries, and optional PostgreSQL dependency configuration.
- Technical/living-document updates are in progress; latest-head Python and Documentation CI must pass before PR #64 can move to Ready for Review.
- Production-live scheduler validation is **not complete**.

## Production-Live Validation Still Required

Do not claim production scheduled ingestion success until all are verified:

1. PR #64 is approved and merged.
2. `202608080003_ingestion_operational_status.sql` is applied to Supabase project `xztjjgzpryrfcppqkbdo`.
3. GitHub repository secret `SUPABASE_DB_URL` is configured with a GitHub-runner-reachable PostgreSQL connection string.
4. A real `Scheduled Yahoo Ingestion` run on `main` succeeds.
5. The corresponding `ingestion_runs` row and snapshot linkage are verified remotely.

Current GitHub connector capabilities do not expose repository-secret creation, so secret configuration may require a user/manual GitHub Settings step unless another connected capability becomes available.

## Persistent Data Platform Evidence

- Initial persistence and follow-up covering-index migrations are already applied to Supabase project `xztjjgzpryrfcppqkbdo`.
- Supabase performance advisor no longer reports the previously observed unindexed foreign key.
- Duplicate remote migration-history entries named `snapshot_observation_fk_index` remain documented; schema state is correct because that migration uses `CREATE INDEX IF NOT EXISTS`.
- The new operational-status migration has not yet been remotely applied and must not be described as deployed.

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

Finish latest-head CI and living-document reconciliation for PR #64. If Python and Documentation CI pass, update the PR validation evidence and mark it Ready for Review. Stop for explicit user merge approval. After merge, apply the operational-status migration, configure/verify `SUPABASE_DB_URL`, manually run `Scheduled Yahoo Ingestion`, inspect durable run evidence, and only then record production-live success.
