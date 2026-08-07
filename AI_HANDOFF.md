# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, explicit FX normalization, and active immutable source-snapshot publication work.

PR #43 merged as `da322d96ef4905712b511139e5bbb1ea9da1b575`; Issue #42 closed. Canonical FX direction is explicit and never inferred from ticker text.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/immutable-source-snapshots`
- Issue: #44 — `feat: integrate immutable source snapshot publication`
- Draft PR: #45 — `feat: integrate immutable source snapshot publication`

## Active Implementation

- `investment_manager/data/snapshots.py` adds `SnapshotPublicationPolicy`, `SnapshotPublicationError`, and `SourceSnapshotPublisher`.
- Publication consumes normalized `Observation` values only and never calls providers or mutates source observations.
- One dataset/provider boundary is enforced per snapshot; observations after the explicit UTC cutoff are excluded.
- Duplicate observation IDs and provider mismatches fail closed.
- `PARTIAL` quality is rejected by default and may be allowed only through explicit policy.
- Eligible observations are deterministically sorted before SHA-256 checksum generation.
- Snapshot UUIDv5 is deterministic from dataset, provider, cutoff, and checksum.
- Empty eligible sets and publication-before-cutoff fail explicitly.
- `docs/SOURCE_SNAPSHOTS.md`, data model, operations, test plan, roadmap, traceability, worklog, and changelog document the contract and deferred persistence boundary.

## Validation Status

- Initial implementation head `e1e6e44fe5e31ae4b6325362782c09c78f94fe7c`: Python run #65 and Documentation run #117 passed.
- Documentation-complete head `9c9ad4f7e7350fed1bfb68f270e536b94662606e`: Python run #73 and Documentation run #125 passed.
- PR #45 must still satisfy the normal latest-head CI gate after any final evidence-only document changes before Ready for Review.
- No live network validation is required because snapshot publication is a pure in-memory canonical operation.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit secrets, raw live payloads, secret-bearing URLs, or personal investment data.
3. Financial values remain `Decimal`; datetimes remain timezone-aware and UTC-normalized.
4. Never hide failed, partial, stale, or ambiguous data.
5. Snapshot validation failures publish nothing and are not provider-retry candidates.
6. Substantial PRs begin as Draft.
7. Never merge without explicit user approval.

## Exact Next Recommended Task

Run Python and Documentation CI on the latest PR #45 head after final evidence updates. If both pass, update the PR body and mark Ready for Review. Stop for explicit user merge approval. After merge, proceed to the cache executor or persistence/idempotent ingestion according to the roadmap.
