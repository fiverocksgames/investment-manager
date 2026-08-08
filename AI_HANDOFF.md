# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, remotely deployed persistence schema evidence, a merged provenance-preserving cache executor, merged scheduled-ingestion orchestration, and merged first production scheduling/durable-status infrastructure.

PR #64 merged as `0ed5753bcf2bd31db4c768b953a3d34536ec8409`; Issue #63 closed.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/scheduled-postgres-diagnostics`
- Issue: #67 — `fix: diagnose scheduled Postgres connectivity and index ingestion snapshot FK`
- Draft PR: #68 — `fix: diagnose scheduled Postgres connectivity and index ingestion snapshot FK`

## Remote Production Evidence

- Supabase migration `ingestion_operational_status` is applied to project `xztjjgzpryrfcppqkbdo`.
- Remote schema verification confirmed `ingestion_runs` / `ingestion_failures` constraints and RLS enabled with no client-facing policies.
- User configured GitHub Actions repository secret `SUPABASE_DB_URL`.
- First real `Scheduled Yahoo Ingestion` run: `31256711191` on merged `main` commit `0ed5753bcf2bd31db4c768b953a3d34536ec8409`.
- Secret verification passed and the psycopg runtime installed successfully.
- The actual ingestion step failed safely with sanitized `OperationalError`.
- Logs did not expose the DB URL, password, host, raw exception text, provider payload, or financial values.
- Remote `ingestion_runs` count remained `0` after the failed workflow, so no durable run row was written by that attempt.
- Exact external connectivity cause remains unproven; do not infer authentication, DNS, TLS, or timeout from the generic `OperationalError` alone.

## Active Fix

- `investment_manager/jobs/scheduled_yahoo.py` now classifies database failures using exception type/structure only, without reading or logging raw exception text.
- Safe categories include `timeout`, `dns`, `tls`, `connection`, `authentication`, `operational`, and generic `database`.
- Added deterministic tests proving secret-like exception messages are not needed for classification.
- Supabase performance advisor found `ingestion_runs.snapshot_id` FK without a covering index; migration `202608080004_ingestion_snapshot_fk_index.sql` adds it with `CREATE INDEX IF NOT EXISTS`.

## Validation Status

- Diagnostic implementation head `7b661b1a7f16a33b93c33a7fc52862913a2d8404`: Python run #112 passed.
- Latest living-document head requires final Python/Documentation CI before PR #68 can be marked Ready for Review.
- Production scheduled ingestion success is **not yet verified**.

## Exact Next Steps

1. Finish latest-head CI for PR #68.
2. Mark PR #68 Ready for Review if applicable checks pass.
3. Stop for explicit user merge approval.
4. After merge, apply `ingestion_snapshot_fk_index` to Supabase and confirm the advisor finding is gone.
5. Ask the user to manually re-run `Scheduled Yahoo Ingestion` on `main` because the current GitHub connector cannot dispatch a new workflow.
6. Inspect the new run logs. Use only the sanitized failure category if it fails.
7. If it succeeds, verify matching `ingestion_runs`, optional `ingestion_failures`, snapshot linkage, provider attempt count, and accepted record count remotely before recording production-live success.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit or log database URLs, passwords, service-role credentials, provider secrets, raw payloads, or personal investment data.
3. Financial values remain `Decimal`; persisted financial values use PostgreSQL `numeric`.
4. Datetimes remain timezone-aware and UTC-normalized.
5. Cache/retry/orchestration must never rewrite freshness or provenance.
6. Partial/failed provider outcomes must not silently become trusted published data.
7. Substantial PRs begin as Draft.
8. Never merge without explicit user approval.
