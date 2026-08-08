# Analysis Input Manifests

## Purpose

An analysis input manifest is the immutable boundary between versioned data and a future deterministic analysis run. It binds the exact `DatasetVersion` selected for each logical dataset without copying observations or changing source provenance.

This milestone implements input identity and persistence only. It does not calculate indicators, classify regimes, rank candidates, allocate portfolios, recommend trades, or execute orders.

## Requirements

- `REQ-DATA-002`: analysis inputs reference immutable versioned datasets.
- `REQ-SIG-002`: future analysis reruns can recover the exact versioned input set.
- `REQ-BKT-001`: historical input identity is preserved for future point-in-time backtesting.

## Model

`AnalysisInputManifest` contains:

- deterministic `manifest_id`;
- timezone-aware UTC `as_of`;
- operational `created_at`;
- ordered `version_ids`;
- lowercase SHA-256 `checksum`.

Each member is one already-published `DatasetVersion`. A manifest may span multiple logical datasets, but it may contain at most one version for a given dataset.

## Canonical Ordering and Identity

Caller iteration order is not identity. Members are sorted by normalized logical dataset and then version UUID.

The canonical checksum payload contains:

- manifest `as_of`;
- for each ordered member: logical dataset, dataset-version UUID, dataset-version `as_of`, and dataset-version checksum.

Operational `created_at` is deliberately excluded from content identity. The manifest UUID is UUIDv5 over the manifest namespace, `as_of`, and SHA-256 checksum.

Therefore identical logical inputs at the same `as_of` produce the same manifest identity even when constructed in a different caller order or at a different operational creation time.

## Point-in-Time Rules

A manifest fails closed when:

- no dataset versions are supplied;
- `as_of` or `created_at` is timezone-naive;
- `created_at` precedes manifest `as_of`;
- a member dataset version has `as_of` later than manifest `as_of`;
- a member dataset version has `created_at` later than manifest `created_at`;
- two members represent the same logical dataset;
- member identity/content conflicts with persisted immutable dataset-version evidence.

These rules prevent a future analysis run from silently selecting information that was not available within its declared point-in-time boundary.

## Persistence Contract

Persistence uses one transaction for the manifest row and its exact ordered memberships.

Before inserting the manifest, the repository verifies every referenced `dataset_versions` row matches the supplied immutable dataset, `as_of`, `created_at`, and checksum. Missing or conflicting referenced versions fail closed.

Insertion is immutable and replay-safe:

- identical replay is idempotent;
- a conflicting existing manifest row fails;
- conflicting membership at an existing position fails;
- the final membership count must exactly equal the manifest member count;
- any failure rolls back the transaction.

## Database Shape

The additive migration creates server-managed tables:

- `analysis_input_manifests`;
- `analysis_input_manifest_versions`.

Both tables enable Row Level Security and intentionally define no browser/client policies in this milestone. Server-side database credentials remain the only intended write path.

## Security and Privacy

Manifest identity and persistence contain no database credentials, provider secrets, raw provider payloads, observation values, or personal portfolio data. The manifest stores only stable data-version identity and point-in-time metadata.

## Deferred Work

The following remain separate reviewed milestones:

- analysis parameter/model-version manifests;
- indicator calculations;
- market-regime classification;
- ETF candidate scoring;
- provider fallback or reconciliation;
- retention/deletion policy;
- automatic manifest creation after ingestion;
- portfolio and recommendation behavior;
- backtest execution.
