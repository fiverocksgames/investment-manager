# Immutable Source Snapshot Publication

## Purpose

Define how normalized canonical observations become an immutable `SourceSnapshot` that downstream analysis can reference explicitly and reproduce later.

## Publication Boundary

`SourceSnapshotPublisher` accepts normalized `Observation` values only. It does not call providers, parse raw payloads, write to persistence, refresh freshness state, or perform analysis.

A snapshot is scoped to exactly one logical dataset and one provider. Cross-provider merging, provider fallback, and triangulation occur outside this publication boundary and require separate policy.

## Eligibility Rules

Publication fails closed unless all of the following hold:

- `dataset` and `provider` are explicit non-empty identifiers.
- `cutoff_at` and `published_at` are timezone-aware and normalized to UTC.
- `published_at` is not earlier than `cutoff_at`.
- every input observation belongs to the declared provider.
- observation IDs are unique across the complete input set.
- `PARTIAL` quality is rejected unless an explicit `SnapshotPublicationPolicy` allows it.
- at least one observation is at or before the requested cutoff.

Observations after the cutoff are excluded rather than rewritten. The publisher never changes observation time, retrieval time, quality, freshness, source identity, revision, or provider metadata.

## Deterministic Identity

Eligible observations are sorted by `observation_id` before identity generation, so input iteration order cannot change snapshot content identity.

The SHA-256 checksum is derived from stable canonical content:

- dataset
- provider
- cutoff
- observation ID
- observation kind and subject ID
- observation timestamp
- exact Decimal string value
- unit
- quality and freshness states
- provider/source identity
- retrieval time and revision
- source attributes sorted by key

The `snapshot_id` is a deterministic UUIDv5 over dataset, provider, cutoff, and checksum. Reordering the same logical eligible input set therefore produces the same checksum and snapshot ID.

`published_at` is operational publication metadata and is intentionally not part of content identity. Persistence must treat an existing deterministic snapshot ID as idempotent content rather than silently replacing it with different source content.

## Partial Quality

The default policy rejects canonical observations whose quality is `partial`. A dataset may explicitly opt in with `SnapshotPublicationPolicy(allow_partial_quality=True)` only when its approved dataset policy allows partial publication.

Allowing partial quality does not upgrade it to valid. The original quality and freshness remain attached to the input observation and must remain visible to downstream policy.

## Failure Behavior

`SnapshotPublicationError` is raised for deterministic publication failures such as:

- empty dataset/provider
- naive datetime values
- publication before cutoff
- empty input
- duplicate observation IDs
- provider mismatch
- disallowed partial quality
- no observations eligible at the cutoff

These are validation or policy failures and must not be retried as provider transport failures.

## Initial Scope

Implemented now:

- in-memory publication
- deterministic content checksum
- deterministic snapshot identity
- cutoff filtering
- provider boundary validation
- partial-quality policy
- deterministic network-free tests

Deferred:

- Supabase/database persistence
- transactional publication
- idempotent database constraints
- snapshot query APIs
- cache integration
- scheduled ingestion integration
- dataset versioning
- cross-provider fallback/selection

## Security and Privacy

The checksum uses canonical observation content already inside the trusted data boundary. Secrets, provider credentials, raw request URLs, raw payloads, and personal portfolio information are not inputs to source snapshot identity.
