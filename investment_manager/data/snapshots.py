"""Deterministic publication of immutable canonical source snapshots."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid5

from .models import DataQualityState, Observation, SourceSnapshot


class SnapshotPublicationError(ValueError):
    """Raised when normalized observations cannot be safely published."""


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise SnapshotPublicationError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class SnapshotPublicationPolicy:
    """Controls which normalized observations may enter a source snapshot."""

    allow_partial_quality: bool = False


class SourceSnapshotPublisher:
    """Build deterministic source snapshots without mutating observations."""

    def __init__(self, policy: SnapshotPublicationPolicy | None = None) -> None:
        self._policy = policy or SnapshotPublicationPolicy()

    def publish(
        self,
        *,
        dataset: str,
        provider: str,
        cutoff_at: datetime,
        published_at: datetime,
        observations: tuple[Observation, ...],
    ) -> SourceSnapshot:
        normalized_dataset = dataset.strip().lower()
        normalized_provider = provider.strip().lower()
        if not normalized_dataset:
            raise SnapshotPublicationError("dataset must not be empty")
        if not normalized_provider:
            raise SnapshotPublicationError("provider must not be empty")

        cutoff = _utc(cutoff_at, "cutoff_at")
        published = _utc(published_at, "published_at")
        if published < cutoff:
            raise SnapshotPublicationError("published_at must not precede cutoff_at")
        if not observations:
            raise SnapshotPublicationError("observations must not be empty")

        seen_ids = set()
        for observation in observations:
            if observation.observation_id in seen_ids:
                raise SnapshotPublicationError("duplicate observation_id is not allowed")
            seen_ids.add(observation.observation_id)
            if observation.source.provider != normalized_provider:
                raise SnapshotPublicationError("all observations must match the snapshot provider")
            if observation.quality is DataQualityState.PARTIAL and not self._policy.allow_partial_quality:
                raise SnapshotPublicationError("partial-quality observation is not publishable by policy")

        eligible = tuple(observation for observation in observations if observation.observed_at <= cutoff)
        if not eligible:
            raise SnapshotPublicationError("no observations are eligible at the requested cutoff")

        ordered = tuple(sorted(eligible, key=lambda observation: str(observation.observation_id)))
        checksum = self._checksum(
            dataset=normalized_dataset,
            provider=normalized_provider,
            cutoff_at=cutoff,
            observations=ordered,
        )
        snapshot_id = uuid5(
            NAMESPACE_URL,
            f"source-snapshot:{normalized_dataset}:{normalized_provider}:{cutoff.isoformat()}:{checksum}",
        )

        return SourceSnapshot(
            snapshot_id=snapshot_id,
            dataset=normalized_dataset,
            provider=normalized_provider,
            cutoff_at=cutoff,
            published_at=published,
            observation_ids=tuple(observation.observation_id for observation in ordered),
            checksum=checksum,
        )

    @staticmethod
    def _checksum(
        *,
        dataset: str,
        provider: str,
        cutoff_at: datetime,
        observations: tuple[Observation, ...],
    ) -> str:
        payload = {
            "dataset": dataset,
            "provider": provider,
            "cutoff_at": cutoff_at.isoformat(),
            "observations": [
                {
                    "observation_id": str(observation.observation_id),
                    "kind": observation.kind.value,
                    "subject_id": str(observation.subject_id),
                    "observed_at": observation.observed_at.isoformat(),
                    "value": str(observation.value),
                    "unit": observation.unit,
                    "quality": observation.quality.value,
                    "freshness": observation.freshness.value,
                    "source": {
                        "provider": observation.source.provider,
                        "source_identifier": observation.source.source_identifier,
                        "retrieved_at": observation.source.retrieved_at.isoformat(),
                        "revision": observation.source.revision,
                        "attributes": dict(sorted(observation.source.attributes.items())),
                    },
                }
                for observation in observations
            ],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
