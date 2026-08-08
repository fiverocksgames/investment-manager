# Persistence and Idempotent Snapshot Storage

## Purpose

Define the first server-side persistence contract for canonical observations and immutable source snapshots.

## Storage Boundary

The committed migration targets PostgreSQL/Supabase. Data-platform tables are server-managed and are not browser-facing user tables.

- `data_observations` stores canonical normalized observations.
- `source_snapshots` stores immutable deterministic snapshot identity and cutoff metadata.
- `source_snapshot_observations` stores exact ordered snapshot membership.

Financial values use PostgreSQL `numeric`. Observation, retrieval, cutoff, and publication times use `timestamptz`. Provider metadata uses `jsonb`.

## Immutability

`observation_id` and `snapshot_id` are immutable identities. Persistence uses insert-if-absent semantics. If an identity already exists, the repository reads the persisted content and compares it to the canonical input.

- identical content is an idempotent replay and succeeds without duplicate rows;
- conflicting content under the same identity fails with `PersistenceError`;
- no conflicting row is overwritten or refreshed in place.

Snapshot membership is also immutable. `(snapshot_id, position)` identifies ordered membership and a snapshot may not contain the same observation twice.

## Transaction Boundary

`SnapshotRepository.persist()` writes the exact observations, snapshot row, and ordered memberships in one database transaction. Every input observation ID must exactly match `SourceSnapshot.observation_ids` before a connection is opened.

The transaction commits only after:

1. every observation is inserted or verified identical;
2. the snapshot is inserted or verified identical;
3. every membership position is inserted or verified identical;
4. persisted membership count exactly matches the snapshot.

Any validation, SQL, or conflict failure rolls back the full transaction.

## Connection Contract

The Python repository accepts an injected DB-API-compatible connection factory. The core package intentionally adds no mandatory PostgreSQL driver dependency in this milestone. A deployment/runtime may later provide an approved driver without changing the canonical persistence semantics.

Database URLs, passwords, service-role credentials, and other secrets are runtime-only configuration and must never appear in code, logs, fixtures, PR text, or committed SQL.

## RLS and Access

The migration enables Row Level Security on all three Phase 2 persistence tables and deliberately creates no client-facing policies. This keeps browser access denied by default. Server-side ingestion access and future user-owned portfolio/RLS design require separately reviewed configuration.

Supabase security advisor reports `rls_enabled_no_policy` informational notices for these tables. Those notices are expected for the current server-managed deny-by-default design and are not treated as missing client authorization policy.

## Verified Remote Evidence

The initial `data_platform_persistence` migration was applied successfully to the protected Supabase project after PR #47 merged. Remote schema inspection confirmed:

- all three persistence tables exist;
- `numeric`, `timestamptz`, UUID, and `jsonb` column types match the committed contract;
- primary keys, foreign keys, uniqueness constraints, checksum/publication-order checks, and retrieval-order checks exist;
- RLS is enabled on all three tables;
- no client-facing RLS policies exist;
- the migration is recorded by Supabase.

A bounded remote smoke used temporary UUIDs and no personal investment data. It inserted one canonical observation, one snapshot, and one ordered membership; replayed the identical observation with `ON CONFLICT DO NOTHING`; verified exactly one row remained and PostgreSQL preserved the value as `123.45`; confirmed a conflicting same-ID insert was rejected by the primary-key constraint; and deleted all temporary rows afterward.

This is bounded evidence for the tested schema and transaction primitives. It is not a claim that the Python `SnapshotRepository` has yet been executed end-to-end against a live PostgreSQL driver.

## Advisor Follow-up

After the initial remote migration, Supabase performance advisor reported that the foreign key from `source_snapshot_observations.observation_id` lacked a covering index. PR #51 added `202608080002_snapshot_observation_fk_index.sql`, which creates `source_snapshot_observations_observation_id_idx` using `create index if not exists`.

After PR #51 merged as `46b209f7c824c3a439ecb26a2fd20559ad8462f9`, the follow-up migration was applied remotely and the performance advisor was re-run. The `unindexed_foreign_keys` finding is no longer present. The remaining performance notices are `unused_index` informational notices, which are expected for newly created/empty tables and are not evidence that intended indexes should be removed.

Supabase migration history currently contains two entries named `snapshot_observation_fk_index` with different migration versions. Because the migration SQL is idempotent (`create index if not exists`), the resulting schema contains the intended index rather than duplicate indexes. The duplicate history entry is retained as execution evidence and must not be hidden or rewritten without a separately reviewed migration-history repair procedure.

The separate Supabase Auth warning for leaked-password protection is outside this persistence schema change and requires a dedicated authentication/security decision.

## Migration Validation Boundary

Routine CI validates Python persistence behavior and documentation without connecting to a live Supabase project. Remote migration evidence must be recorded separately and never inferred from committed SQL alone.

The initial persistence schema and the follow-up foreign-key covering index have both been remotely verified. This evidence does not guarantee future availability, prove application-runtime connectivity, or replace future live `SnapshotRepository` integration testing.

## Initial Limitations

This milestone does not implement:

- a mandatory PostgreSQL driver or live Python repository smoke;
- ingestion-run persistence;
- user-owned portfolio tables or user RLS policies;
- cache execution;
- scheduler/orchestration;
- dataset/snapshot version migration policy;
- deletion/correction workflows;
- automatic repair of duplicate Supabase migration-history entries.

These remain later Phase 2 tasks.
