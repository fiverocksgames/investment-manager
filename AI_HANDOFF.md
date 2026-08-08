# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers; bounded retry; explicit FX normalization; immutable source snapshots; transactional snapshot persistence; provenance-preserving cache execution; scheduled-ingestion orchestration; durable operational status; verified production Yahoo scheduled ingestion; deterministic logical dataset versioning; and a Draft cross-dataset analysis-input manifest milestone.

PR #74 merged as `0840fc81c83447ed816a0b4be1ca876cea151224`; Issue #73 closed. Dataset-versioning remote deployment evidence is recorded. Active work is Issue #75 / Draft PR #76.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/analysis-input-manifests`
- Issue: #75 — `feat: add deterministic cross-dataset analysis input manifests`
- Draft PR: #76
- Requirement IDs: `REQ-DATA-002`, `REQ-SIG-002`, `REQ-BKT-001`

## Analysis Input Manifest Scope

- `AnalysisInputManifest` binds exactly one immutable `DatasetVersion` per logical dataset into a reproducible cross-dataset input set.
- Caller order is not identity. Members are canonically ordered by dataset and version UUID.
- SHA-256 + UUIDv5 identity includes manifest `as_of` plus stable dataset-version identity/content metadata; operational manifest `created_at` does not rewrite identity.
- Publication rejects empty input, duplicate logical datasets, duplicate versions, timezone-naive boundaries, look-ahead dataset versions, and versions created after the manifest creation boundary.
- `AnalysisInputManifestRepository` verifies referenced persisted `dataset_versions` immutable metadata before atomically persisting the manifest and ordered membership.
- Identical replay is idempotent; missing/conflicting versions or conflicting immutable manifest/membership content fail closed and roll back.
- Migration `202608080006_analysis_input_manifests.sql` is committed only and must not be applied remotely before explicit PR merge approval.
- No indicator, regime, candidate-score, portfolio, recommendation, or backtest execution is implemented in this milestone.

## Validation Status

- Deterministic `unittest`/fake-DB coverage added for order/creation-time identity stability, UTC normalization, empty/duplicate/look-ahead/naive-boundary rejection, persisted-version verification, idempotent replay, immutable conflict, and rollback.
- Head `a7bb9cef07a3efb9e89bf308ce7d86c920b8a19d` passed Python run #138 and Documentation run #202.
- Living/spec documentation updates are in progress; latest-head CI must be reconfirmed after those commits before Ready for Review.

## Security and Data Boundaries

1. Never commit or log database URLs, passwords, service-role credentials, provider secrets, raw payloads, observation values, or personal investment data.
2. Datetimes remain timezone-aware and UTC-normalized.
3. Input manifests reference immutable version identity; they do not copy or rewrite observations.
4. RLS is enabled on the new server-managed tables with no client-facing policies in this milestone.
5. No remote migration or live repository-connectivity claim before separately executed evidence.
6. Never merge without explicit user approval.

## Exact Next Steps

1. Finish affected `ANALYSIS_SPEC`, database/architecture, feature-matrix, worklog, and changelog updates.
2. Confirm latest-head Python and Documentation CI.
3. Update PR #76 validation evidence and mark Ready for Review only when required CI passes.
4. Stop for explicit user merge approval.
5. Only after approval and merge, apply `202608080006_analysis_input_manifests.sql` remotely and verify schema/advisor evidence before claiming deployment.
