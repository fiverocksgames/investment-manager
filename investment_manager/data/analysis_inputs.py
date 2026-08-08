"""Deterministic cross-dataset input manifests over immutable dataset versions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Protocol
from uuid import NAMESPACE_URL, UUID, uuid5

from .versioning import DatasetVersion


class AnalysisInputManifestError(RuntimeError):
    """Raised when an analysis input manifest cannot be published or persisted safely."""


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class AnalysisInputManifest:
    manifest_id: UUID
    as_of: datetime
    created_at: datetime
    version_ids: tuple[UUID, ...]
    checksum: str

    def __post_init__(self) -> None:
        as_of = _utc(self.as_of, "as_of")
        created_at = _utc(self.created_at, "created_at")
        object.__setattr__(self, "as_of", as_of)
        object.__setattr__(self, "created_at", created_at)
        if created_at < as_of:
            raise ValueError("created_at must not precede as_of")
        if not self.version_ids:
            raise ValueError("analysis input manifest must contain dataset versions")
        if len(set(self.version_ids)) != len(self.version_ids):
            raise ValueError("analysis input manifest version_ids must be unique")
        checksum = self.checksum.strip().lower()
        if len(checksum) != 64 or any(char not in "0123456789abcdef" for char in checksum):
            raise ValueError("checksum must be lowercase SHA-256 hex")
        object.__setattr__(self, "checksum", checksum)


class AnalysisInputManifestPublisher:
    """Create stable cross-dataset input identity independent of caller order."""

    def publish(
        self,
        *,
        as_of: datetime,
        created_at: datetime,
        versions: tuple[DatasetVersion, ...],
    ) -> AnalysisInputManifest:
        normalized_as_of = _utc(as_of, "as_of")
        normalized_created = _utc(created_at, "created_at")
        if normalized_created < normalized_as_of:
            raise AnalysisInputManifestError("created_at must not precede as_of")
        if not versions:
            raise AnalysisInputManifestError("analysis input manifest requires dataset versions")

        seen_datasets: set[str] = set()
        seen_ids: set[UUID] = set()
        for version in versions:
            if version.dataset in seen_datasets:
                raise AnalysisInputManifestError("analysis input manifest may contain only one version per dataset")
            seen_datasets.add(version.dataset)
            if version.version_id in seen_ids:
                raise AnalysisInputManifestError("duplicate dataset version in analysis input manifest")
            seen_ids.add(version.version_id)
            if version.as_of > normalized_as_of:
                raise AnalysisInputManifestError("dataset version as_of must not exceed manifest as_of")
            if version.created_at > normalized_created:
                raise AnalysisInputManifestError("dataset version created_at must not exceed manifest created_at")

        ordered = tuple(sorted(versions, key=lambda item: (item.dataset, str(item.version_id))))
        payload = {
            "as_of": normalized_as_of.isoformat(),
            "versions": [
                {
                    "dataset": version.dataset,
                    "version_id": str(version.version_id),
                    "as_of": version.as_of.isoformat(),
                    "checksum": version.checksum,
                }
                for version in ordered
            ],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        checksum = hashlib.sha256(encoded).hexdigest()
        manifest_id = uuid5(
            NAMESPACE_URL,
            f"investment-manager:analysis-input-manifest:{normalized_as_of.isoformat()}:{checksum}",
        )
        return AnalysisInputManifest(
            manifest_id=manifest_id,
            as_of=normalized_as_of,
            created_at=normalized_created,
            version_ids=tuple(version.version_id for version in ordered),
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
class AnalysisInputManifestPersistenceResult:
    manifest_id: UUID
    created_manifest: bool
    inserted_memberships: int


_INSERT_MANIFEST = """
insert into analysis_input_manifests (manifest_id, as_of, created_at, checksum)
values (%s, %s, %s, %s)
on conflict (manifest_id) do nothing
returning manifest_id
"""
_SELECT_MANIFEST = """
select as_of, created_at, checksum from analysis_input_manifests where manifest_id = %s
"""
_SELECT_VERSION = """
select dataset, as_of, created_at, checksum from dataset_versions where version_id = %s
"""
_INSERT_MEMBERSHIP = """
insert into analysis_input_manifest_versions (manifest_id, position, dataset, version_id)
values (%s, %s, %s, %s)
on conflict (manifest_id, position) do nothing
returning manifest_id
"""
_SELECT_MEMBERSHIP = """
select dataset, version_id from analysis_input_manifest_versions where manifest_id = %s and position = %s
"""
_COUNT_MEMBERSHIPS = """
select count(*) from analysis_input_manifest_versions where manifest_id = %s
"""


class AnalysisInputManifestRepository:
    """Persist one manifest and exact ordered dataset-version membership atomically."""

    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    def persist(
        self,
        manifest: AnalysisInputManifest,
        versions: tuple[DatasetVersion, ...],
    ) -> AnalysisInputManifestPersistenceResult:
        by_id = {version.version_id: version for version in versions}
        if len(by_id) != len(versions):
            raise AnalysisInputManifestError("duplicate version_id in persistence input")
        if set(by_id) != set(manifest.version_ids):
            raise AnalysisInputManifestError("persistence versions must exactly match manifest version_ids")
        ordered = tuple(by_id[version_id] for version_id in manifest.version_ids)
        if len({version.dataset for version in ordered}) != len(ordered):
            raise AnalysisInputManifestError("persistence versions must contain distinct datasets")

        connection = self._connection_factory()
        cursor = connection.cursor()
        created_manifest = False
        inserted_memberships = 0
        try:
            for version in ordered:
                cursor.execute(_SELECT_VERSION, (str(version.version_id),))
                row = cursor.fetchone()
                expected = (version.dataset, version.as_of, version.created_at, version.checksum)
                if row is None or tuple(row) != expected:
                    raise AnalysisInputManifestError(
                        "referenced dataset version is missing or conflicts with persisted content"
                    )

            values = (manifest.as_of, manifest.created_at, manifest.checksum)
            cursor.execute(_INSERT_MANIFEST, (str(manifest.manifest_id),) + values)
            if cursor.fetchone() is not None:
                created_manifest = True
            else:
                cursor.execute(_SELECT_MANIFEST, (str(manifest.manifest_id),))
                row = cursor.fetchone()
                if row is None or tuple(row) != values:
                    raise AnalysisInputManifestError("existing manifest_id has conflicting immutable content")

            for position, version in enumerate(ordered):
                cursor.execute(
                    _INSERT_MEMBERSHIP,
                    (str(manifest.manifest_id), position, version.dataset, str(version.version_id)),
                )
                if cursor.fetchone() is not None:
                    inserted_memberships += 1
                else:
                    cursor.execute(_SELECT_MEMBERSHIP, (str(manifest.manifest_id), position))
                    row = cursor.fetchone()
                    if row is None or str(row[0]) != version.dataset or str(row[1]) != str(version.version_id):
                        raise AnalysisInputManifestError(
                            "existing analysis-input membership conflicts with immutable order"
                        )

            cursor.execute(_COUNT_MEMBERSHIPS, (str(manifest.manifest_id),))
            row = cursor.fetchone()
            if row is None or int(row[0]) != len(manifest.version_ids):
                raise AnalysisInputManifestError("persisted manifest membership count does not match manifest")

            connection.commit()
            return AnalysisInputManifestPersistenceResult(
                manifest_id=manifest.manifest_id,
                created_manifest=created_manifest,
                inserted_memberships=inserted_memberships,
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
