# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, remotely deployed persistence schema evidence, a merged provenance-preserving cache executor, merged scheduled-ingestion orchestration, and verified production scheduled-ingestion success with durable run evidence.

PR #64 merged as `0ed5753bcf2bd31db4c768b953a3d34536ec8409`; Issue #63 closed. PR #68 merged as `ad762ed10eebe3b50ef3924e4fd6978a826ab680`; Issue #67 closed.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/scheduled-ingestion-live-evidence`
- Issue: #69 — `docs: record first production scheduled-ingestion success`
- Evidence-only PR pending creation/validation.

## Verified Production Scheduled-Ingestion Evidence

- Supabase migrations `ingestion_operational_status` and `ingestion_snapshot_fk_index` are applied to project `xztjjgzpryrfcppqkbdo`.
- The prior `ingestion_runs.snapshot_id` unindexed-foreign-key advisor finding is resolved.
- GitHub Actions repository secret `SUPABASE_DB_URL` is configured with a working pooler connection string; secret values are never recorded in repository evidence.
- Earlier production runs `31256711191`, `31257558763`, and `31257858229` failed safely before durable run persistence while DB connectivity was being corrected. Their failure evidence remains part of operational history and is not reclassified as success.
- First verified successful `Scheduled Yahoo Ingestion` run: `31257977677` on `main` commit `ad762ed10eebe3b50ef3924e4fd6978a826ab680`.
- Safe workflow output:
  - `run_id=5346037b-2772-4c22-8e04-4d59fad0daf7`
  - `provider=yahoo`
  - `dataset=market_prices`
  - `status=succeeded`
  - `provider_attempts=1`
  - `records_received=8`
  - `records_accepted=8`
  - `snapshot_id=725526a7-a925-54ff-a070-dcc2b92b96fd`
- Remote Supabase verification confirmed the exact durable `ingestion_runs` row, linked Yahoo `market_prices` snapshot, 8 snapshot members, and zero `ingestion_failures` rows for the run.
- Snapshot cutoff and publication timestamps are UTC-aware and the persisted checksum is present.
- This is bounded evidence that production scheduling, live Yahoo retrieval, immutable snapshot persistence, and durable operational-status persistence succeeded together for this run. It is not a guarantee of future provider or database availability.

## Operational Interpretation

The successful run followed correction of the protected database connection configuration to a GitHub-runner-reachable Supabase pooler URI. The exact secret and password are intentionally not documented. Do not infer that every pooler/direct configuration will work in all environments.

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

Finish this evidence-only update, pass Documentation CI, and stop for explicit merge approval. After merge, the next Phase 2 architectural milestone is dataset/snapshot versioning unless a higher-priority operational hardening task is selected first.
