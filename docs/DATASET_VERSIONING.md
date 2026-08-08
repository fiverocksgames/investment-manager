# Dataset Versioning

## Purpose

`DatasetVersion` gives downstream analysis a reproducible immutable identity for one logical dataset assembled from one or more already-published `SourceSnapshot` values.

This layer does not copy observations and does not merge provider payloads. It records exactly which immutable source snapshots constitute a logical dataset version at an explicit point-in-time boundary.

## Requirements

This contract implements `REQ-DATA-002`, `REQ-OPS-002`, and `REQ-MKT-002`.

## Canonical Contract

A dataset version contains:

- `version_id`: deterministic UUIDv5 identity.
- `dataset`: normalized logical dataset name.
- `as_of`: timezone-aware UTC data boundary.
- `created_at`: timezone-aware UTC operational creation timestamp.
- `snapshot_ids`: non-empty deterministic ordered membership.
- `checksum`: lowercase SHA-256 content identity.

All member source snapshots must belong to the same logical dataset. Every snapshot cutoff must be at or before `as_of`, and every snapshot publication time must be at or before `created_at`.

## Deterministic Identity

Caller iteration order is not identity. Members are canonically ordered by provider, cutoff timestamp, and snapshot UUID.

The checksum covers stable source content metadata only:

- logical dataset;
- `as_of`;
- member snapshot UUID;
- member provider;
- member cutoff;
- member source checksum.

Operational `created_at` and source `published_at` timestamps are deliberately excluded from version identity. They remain persisted evidence, but rerunning publication at another operational time cannot rewrite the content identity.

`version_id` is UUIDv5 over dataset, `as_of`, and checksum. Identical dataset/as-of/content therefore produces the same version ID.

## Fail-Closed Rules

Publication fails when:

- dataset or member list is empty;
- any member belongs to another logical dataset;
- a snapshot ID is duplicated;
- two different snapshots claim the same provider/cutoff identity;
- a member cutoff is after `as_of`;
- a member was published after `created_at`;
- `as_of` or `created_at` is timezone-naive;
- `created_at` precedes `as_of`.

No quality, freshness, source metadata, observation value, or source-snapshot identity is rewritten by this layer.

## Persistence

`DatasetVersionRepository` persists a dataset version and its ordered memberships in one transaction.

Before inserting the version, each referenced source snapshot must already exist and match its immutable persisted metadata. Identical replay is idempotent. The same version UUID with conflicting content, missing/conflicting source snapshot evidence, conflicting membership order, or incorrect persisted membership count causes rollback.

The PostgreSQL tables are server-managed. RLS is enabled and no browser/client policies are defined in this milestone.

## Scope Boundary

A `DatasetVersion` groups snapshots for exactly one logical dataset. A future analysis-input manifest may combine versions from multiple datasets, but cross-dataset bundling, fallback priority, provider reconciliation, retention/deletion, portfolio logic, and backtesting are outside this contract.
