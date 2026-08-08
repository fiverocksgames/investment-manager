# Dataset Versioning Remote Deployment Evidence

## Scope

This document records the bounded remote deployment evidence for the dataset-versioning schema introduced by PR #72. It does not claim live execution of the Python `DatasetVersionRepository` against production and does not contain credentials, DSNs, observation values, or personal investment data.

## Deployment

- Repository merge commit: `a88dae118afbcfd3ab1e09d4c8c6643a9cd457bb`
- Supabase project: `xztjjgzpryrfcppqkbdo`
- Source migration: `supabase/migrations/202608080005_dataset_versioning.sql`
- Remote migration name: `dataset_versioning`
- Migration application result: success
- Remote migration history contains the applied `dataset_versioning` entry.

## Remote Schema Verification

The production schema contains:

- `public.dataset_versions`
- `public.dataset_version_snapshots`

Verified constraints include:

- `dataset_versions.version_id` primary key
- lowercase 64-character SHA-256 checksum check
- `created_at >= as_of` check
- unique `(dataset, as_of, checksum)` content identity
- `dataset_version_snapshots(version_id, position)` primary key
- non-negative membership position check
- foreign key from membership `version_id` to `dataset_versions`
- foreign key from membership `snapshot_id` to `source_snapshots`
- unique `(version_id, snapshot_id)` membership identity

Verified indexes include:

- `dataset_versions(dataset, as_of desc)`
- `dataset_version_snapshots(snapshot_id)`
- primary/unique indexes created by the constraints above

## RLS and Security Boundary

Both dataset-version tables have RLS enabled and zero browser/client policies. This is intentional: these Phase 2 tables remain server-managed and deny browser access by default until a separately reviewed access policy exists.

Supabase Security Advisor therefore reports `rls_enabled_no_policy` INFO for these tables. This is expected rather than a deployment failure. The separate project-level Auth leaked-password-protection warning predates and is unrelated to dataset versioning.

## Performance Advisor

The Performance Advisor reports no `unindexed_foreign_keys` finding for the dataset-version tables. The newly created lookup and FK indexes currently appear as `unused_index` INFO because the tables are new and have little or no workload history. They should not be removed based solely on this initial signal.

Remediation reference for unused-index advisor messages: https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index

## Evidence Boundary

This deployment evidence proves that the reviewed migration was applied and that the resulting production schema, constraints, indexes, and RLS state match the intended design at inspection time.

It does **not** prove:

- future database availability;
- live production execution of the Python `DatasetVersionRepository`;
- automatic creation of dataset versions after every ingestion run;
- cross-dataset analysis-input composition;
- provider fallback or reconciliation;
- portfolio, strategy, recommendation, or backtest behavior.
