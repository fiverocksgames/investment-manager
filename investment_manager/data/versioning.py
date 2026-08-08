"""Deterministic versioning for one logical dataset over immutable source snapshots."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Protocol
from uuid import NAMESPACE_URL, UUID, uuid5

from .models import SourceSnapshot


class DatasetVersionError(RuntimeError):
    """Raised when a dataset version cannot be published or persisted safely."""


def _required(value: str, name: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError(f"{name} must not be empty")
    return normalized


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class DatasetVersion:
    version_id: UUID
    dataset: str
    as_of: datetime
    created_at: datetime
    snapshot_ids: tuple[UUID, ...]
    checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "dataset", _required(self.dataset, "dataset"))
        as_of = _utc(self.as_of, "as_of")
        created = _utc(self.created_at, "created_at")
        object.__setattr__(self, "as_of", as_of)
        object.__setattr__(self, "created_at", created)
        if created < as_of:
            raise ValueError("created_at must not precede as_of")
        if not self.snapshot_ids:
            raise ValueError("dataset version must contain snapshots")
        if len(set(self.snapshot_ids)) != len(self.snapshot_ids):
            raise ValueError("dataset version snapshot_ids must be unique")
        checksum = self.checksum.strip().lower()
        if len(checksum) != 64 or any(char not in "0123456789abcdef" for char in checksum):
            raise ValueError("checksum must be lowercase SHA-256 hex")
        object.__setattr__(self, "checksum", checksum)


class DatasetVersionPublisher:
    """Create stable dataset-version identity independent of caller iteration order."""

    def publish(
        self,
        *,
        dataset: str,
        as_of: datetime,
        created_at: datetime,
        snapshots: tuple[SourceSnapshot, ...],
    ) -> DatasetVersion:
        normalized_dataset = _required(dataset, "dataset")
        normalized_as_of = _utc(as_of, "as_of")
        normalized_created = _utc(created_at, "created_at")
        if normalized_created < normalized_as_of:
            raise DatasetVersionError("created_at must not precede as_of")
        if not snapshots:
            raise DatasetVersionError("dataset version requires at least one source snapshot")

        seen_ids: set[UUID] = set()
        seen_boundaries: dict[tuple[str, datetime], UUID] = {}
        for snapshot in snapshots:
            if snapshot.dataset != normalized_dataset:
                raise DatasetVersionError("source snapshot dataset must match dataset version")
            if snapshot.snapshot_id in seen_ids:
                raise DatasetVersionError("duplicate snapshot_id in dataset version input")
            seen_ids.add(snapshot.snapshot_id)
            if snapshot.cutoff_at > normalized_as_of:
                raise DatasetVersionError("source snapshot cutoff must not exceed dataset version as_of")
            if snapshot.published_at > normalized_created:
                raise DatasetVersionError("source snapshot published_at must not exceed dataset version created_at")
            boundary = (snapshot.provider, snapshot.cutoff_at)
            previous = seen_boundaries.get(boundary)
            if previous is not None and previous != snapshot.snapshot_id:
                raise DatasetVersionError("conflicting snapshots share provider/cutoff boundary")
            seen_boundaries[boundary] = snapshot.snapshot_id

        ordered = tuple(
            sorted(
                snapshots,
                key=lambda item: (item.provider, item.cutoff_at.isoformat(), str(item.snapshot_id)),
            )
        )
        payload = {
            "dataset": normalized_dataset,
            "as_of": normalized_as_of.isoformat(),
            "snapshots": [
                {
                    "snapshot_id": str(snapshot.snapshot_id),
                    "provider": snapshot.provider,
                    "cutoff_at": snapshot.cutoff_at.isoformat(),
                    "checksum": snapshot.checksum,
                }
                for snapshot in ordered
            ],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        checksum = hashlib.sha256(encoded).hexdigest()
        version_id = uuid5(
            NAMESPACE_URL,
            f"investment-manager:dataset-version:{normalized_dataset}:{normalized_as_of.isoformat()}:{checksum}",
        )
        return DatasetVersion(
            version_id=version_id,
            dataset=normalized_dataset,
            as_of=normalized_as_of,
            created_at=normalized_created,
            snapshot_ids=tuple(snapshot.snapshot_id for snapshot in ordered),
            checksum=checksum,
        )


class Cursor(Protocol):
    def execute(self, operation: str, parameters: tuple[Any, ...] = ()) -> Any: ...
    def fetchone(self) -> Any: ...
    def close(self) -> Any: ...


class Connection(Protocol):
    def cursor(self) -> Cursor: ...
    def commit(self) -> Any: ...
    def rollback(self) -> Any: ...
    def close(self) -> Any: ...


@dataclass(frozen=True, slots=True)
class DatasetVersionPersistenceResult:
    version_id: UUID
    created_version: bool
    inserted_memberships: int


_INSERT_VERSION = """
insert into dataset_versions (version_id, dataset, as_of, created_at, checksum)
values (%s, %s, %s, %s, %s)
on conflict (version_id) do nothing
returning version_id
"""
_SELECT_VERSION = """
select dataset, as_of, created_at, checksum from dataset_versions where version_id = %s
"""
_SELECT_SNAPSHOT = """
select dataset, provider, cutoff_at, published_at, checksum from source_snapshots where snapshot_id = %s
"""
_INSERT_MEMBERSHIP = """
insert into dataset_version_snapshots (version_id, position, snapshot_id)
values (%s, %s, %s)
on conflict (version_id, position) do nothing
returning version_id
"""
_SELECT_MEMBERSHIP = """
select snapshot_id from dataset_version_snapshots where version_id = %s and position = %s
"""
_COUNT_MEMBERSHIPS = """
select count(*) from dataset_version_snapshots where version_id = %s
"""


class DatasetVersionRepository:
    """Persist one dataset version and exact ordered snapshot membership atomically."""

    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    def persist(
        self,
        version: DatasetVersion,
        snapshots: tuple[SourceSnapshot, ...],
    ) -> DatasetVersionPersistenceResult:
        by_id = {snapshot.snapshot_id: snapshot for snapshot in snapshots}
        if len(by_id) != len(snapshots):
            raise DatasetVersionError("duplicate snapshot_id in persistence input")
        if set(by_id) != set(version.snapshot_ids):
            raise DatasetVersionError("persistence snapshots must exactly match dataset version snapshot_ids")
        ordered = tuple(by_id[snapshot_id] for snapshot_id in version.snapshot_ids)
        if any(snapshot.dataset != version.dataset for snapshot in ordered):
            raise DatasetVersionError("persisted snapshot dataset must match dataset version")

        connection = self._connection_factory()
        cursor = connection.cursor()
        created_version = False
        inserted_memberships = 0
        try:
            for snapshot in ordered:
                cursor.execute(_SELECT_SNAPSHOT, (str(snapshot.snapshot_id),))
                row = cursor.fetchone()
                expected = (
                    snapshot.dataset,
                    snapshot.provider,
                    snapshot.cutoff_at,
                    snapshot.published_at,
                    snapshot.checksum,
                )
                if row is None or tuple(row) != expected:
                    raise DatasetVersionError("referenced source snapshot is missing or conflicts with persisted content")

            values = (version.dataset, version.as_of, version.created_at, version.checksum)
            cursor.execute(_INSERT_VERSION, (str(version.version_id),) + values)
            if cursor.fetchone() is not None:
                created_version = True
            else:
                cursor.execute(_SELECT_VERSION, (str(version.version_id),))
                row = cursor.fetchone()
                if row is None or tuple(row) != values:
                    raise DatasetVersionError("existing version_id has conflicting immutable content")

            for position, snapshot_id in enumerate(version.snapshot_ids):
                cursor.execute(_INSERT_MEMBERSHIP, (str(version.version_id), position, str(snapshot_id)))
                if cursor.fetchone() is not None:
                    inserted_memberships += 1
                else:
                    cursor.execute(_SELECT_MEMBERSHIP, (str(version.version_id), position))
                    row = cursor.fetchone()
                    if row is None or str(row[0]) != str(snapshot_id):
                        raise DatasetVersionError("existing dataset-version membership conflicts with immutable order")

            cursor.execute(_COUNT_MEMBERSHIPS, (str(version.version_id),))
            row = cursor.fetchone()
            if row is None or int(row[0]) != len(version.snapshot_ids):
                raise DatasetVersionError("persisted dataset-version membership count does not match version")

            connection.commit()
            return DatasetVersionPersistenceResult(
                version_id=version.version_id,
                created_version=created_version,
                inserted_memberships=inserted_memberships,
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
