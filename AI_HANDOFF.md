# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers; bounded retry; explicit FX normalization; immutable source snapshots; transactional snapshot persistence; provenance-preserving cache execution; scheduled-ingestion orchestration; durable operational status; verified production Yahoo scheduled ingestion; and deterministic logical dataset versioning.

PR #72 merged as `a88dae118afbcfd3ab1e09d4c8c6643a9cd457bb`; Issue #71 closed. Migration `202608080005_dataset_versioning.sql` has now been applied to Supabase project `xztjjgzpryrfcppqkbdo` and the resulting schema has been remotely inspected.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/dataset-versioning-remote-evidence`
- Issue: #73 — `docs: record remote dataset-versioning deployment evidence`
- PR: evidence-only PR pending CI/Ready-for-Review completion

## Dataset Versioning

- `DatasetVersion` represents one immutable version of exactly one logical dataset.
- `DatasetVersionPublisher` groups already-published `SourceSnapshot` values without copying or rewriting observation content.
- Identity is deterministic across caller ordering and uses SHA-256 plus UUIDv5 over dataset, `as_of`, and stable source-snapshot identity/content metadata.
- Point-in-time validation rejects future cutoff/publication, dataset mismatch, duplicate IDs, and conflicting provider/cutoff boundaries.
- `DatasetVersionRepository` verifies already-persisted source snapshot metadata before atomically persisting version and ordered membership.
- Identical replay is idempotent; immutable conflicts roll back.

## Remote Dataset-Version Deployment Evidence

- Supabase migration `dataset_versioning` applied successfully after PR #72 merge.
- Remote migration history contains the applied migration.
- `dataset_versions` and `dataset_version_snapshots` exist with the expected primary keys, foreign keys, uniqueness checks, checksum/time checks, and ordered membership constraint.
- `dataset_version_snapshots.snapshot_id` has an explicit covering index; `version_id` is covered by the composite primary key.
- `dataset_versions(dataset, as_of desc)` index exists for version lookup.
- Both tables have RLS enabled and zero client-facing policies, matching the intentional server-managed deny-by-default design.
- Supabase Performance Advisor reports no unindexed-foreign-key warning for the new tables. New indexes currently appear only as `unused_index` INFO because the tables are new/low-usage.
- Supabase Security Advisor reports `rls_enabled_no_policy` INFO for the new tables, which is expected for this server-only phase. The existing Auth leaked-password-protection warning is unrelated and remains a separate security decision.
- Python `DatasetVersionRepository` live connectivity has **not** been separately executed against production; do not claim it has.

## Verified Production Scheduled-Ingestion Evidence

- GitHub Actions run `31257977677` on `main` succeeded with Yahoo `market_prices`, one provider attempt, eight received/accepted observations, and durable snapshot/run evidence.
- Remote Supabase verification confirmed the matching durable run row, linked snapshot, eight snapshot members, and zero failure rows.
- This remains bounded evidence for that run, not a guarantee of future provider/database availability.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit or log database URLs, passwords, service-role credentials, provider secrets, raw payloads, or personal investment data.
3. Financial values remain `Decimal`; persisted financial values use PostgreSQL `numeric`.
4. Datetimes remain timezone-aware and UTC-normalized.
5. Cache/retry/orchestration/versioning must never rewrite freshness or provenance.
6. Partial/failed provider outcomes must not silently become trusted published data.
7. Substantial PRs begin as Draft.
8. Never merge without explicit user approval.

## Exact Next Steps

1. Finish Issue #73 evidence-only documentation and Documentation CI.
2. Mark the evidence PR Ready for Review when latest-head CI passes; stop for explicit merge approval.
3. After evidence is merged, next Phase 2 architecture work should define a reproducible cross-dataset analysis-input manifest, or separately broaden production scheduling to additional approved provider/dataset paths.
