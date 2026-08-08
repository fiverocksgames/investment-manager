# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, deterministic immutable source-snapshot publication, remotely deployed snapshot persistence, provenance-preserving cache execution, scheduled-ingestion orchestration, and verified production Yahoo scheduled-ingestion success with durable run evidence.

PR #70 merged as `6a500adcae708da3ce2b33614856e5de55598f4c`; Issue #69 closed. The first verified production Scheduled Yahoo Ingestion remains run `31257977677` with durable Supabase run/snapshot evidence.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/dataset-versioning`
- Issue: #71 — `feat: add deterministic dataset and snapshot versioning`
- Requirement IDs: `REQ-DATA-002`, `REQ-OPS-002`, `REQ-MKT-002`
- PR: #72 — Draft pending final latest-head CI, then Ready for Review

## Dataset Versioning Scope

- `DatasetVersion` represents one immutable version of exactly one logical dataset.
- `DatasetVersionPublisher` groups one or more already-published `SourceSnapshot` values without copying or rewriting observation content.
- Caller order is not identity. Members are ordered deterministically by provider, cutoff, and snapshot UUID.
- SHA-256 version content covers dataset, `as_of`, and stable member snapshot identity/content metadata. Operational creation/publication timestamps are not content identity.
- UUIDv5 derives deterministic version identity from dataset, `as_of`, and checksum.
- Publication fails closed on dataset mismatch, duplicate snapshot IDs, conflicting provider/cutoff identities, look-ahead cutoff, publication after version creation, empty input, or timezone-naive boundaries.
- `DatasetVersionRepository` requires every member source snapshot to exist with matching immutable persisted dataset/provider/cutoff/`published_at`/checksum evidence before atomically writing the version and ordered memberships.
- Identical replay is idempotent. Conflicting version content or membership order rolls back.
- Migration `202608080005_dataset_versioning.sql` adds server-managed `dataset_versions` and `dataset_version_snapshots` with RLS enabled and no client-facing policies.
- Cross-dataset analysis-input bundles, provider fallback/reconciliation, retention/deletion, portfolio logic, and backtesting remain out of scope.

## Validation Status

- Deterministic network-free unit/fake-DB tests cover identity/order stability, UTC normalization, mismatch/duplicate/conflict/look-ahead rejection, publication-time boundaries, atomic persistence, replay, persisted source-snapshot publication conflict, and immutable version conflict.
- Python run #127 failed because the initial new test imported `pytest` while repository CI uses `unittest discover` and does not install pytest. The suite was converted to the repository test contract.
- Head `10ee278428b9536f3cd7d6cc05830da3a7708e9f` passed Python #128 and Documentation #188 before final living-document evidence commits.
- Final living-document commits require one last latest-head Python/Documentation CI confirmation before PR #72 can be marked Ready for Review.
- The new migration is committed only; it must not be applied remotely before explicit merge approval.

## Verified Production Scheduled-Ingestion Evidence

- GitHub Actions run `31257977677` on `main` succeeded with `provider=yahoo`, `dataset=market_prices`, `provider_attempts=1`, `records_received=8`, `records_accepted=8`, and snapshot `725526a7-a925-54ff-a070-dcc2b92b96fd`.
- Remote Supabase verification confirmed the exact durable run row, linked snapshot, 8 snapshot members, and zero failure rows.
- This is bounded evidence for that run, not a guarantee of future provider/database availability.

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

1. Confirm latest-head Python and Documentation CI after final living-document commits.
2. If both pass, update PR #72 validation evidence and mark Ready for Review.
3. Stop for explicit user merge approval.
4. Only after approval and merge, apply `202608080005_dataset_versioning.sql` remotely and verify schema/advisor evidence before claiming deployment.
