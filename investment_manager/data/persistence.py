"""Transactional persistence for canonical observations and immutable source snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Protocol
from uuid import UUID

from .models import Observation, SourceSnapshot


class PersistenceError(RuntimeError):
    """Raised when persisted immutable content conflicts with canonical input."""


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
class PersistenceResult:
    snapshot_id: UUID
    created_snapshot: bool
    inserted_observations: int
    inserted_memberships: int


_INSERT_OBSERVATION = """
insert into data_observations (
    observation_id, kind, subject_id, observed_at, value, unit, quality, freshness,
    provider, source_identifier, retrieved_at, revision, source_attributes
) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
on conflict (observation_id) do nothing
returning observation_id
"""

_SELECT_OBSERVATION = """
select kind, subject_id, observed_at, value, unit, quality, freshness,
       provider, source_identifier, retrieved_at, revision, source_attributes
from data_observations where observation_id = %s
"""

_INSERT_SNAPSHOT = """
insert into source_snapshots (
    snapshot_id, dataset, provider, cutoff_at, published_at, checksum
) values (%s, %s, %s, %s, %s, %s)
on conflict (snapshot_id) do nothing
returning snapshot_id
"""

_SELECT_SNAPSHOT = """
select dataset, provider, cutoff_at, published_at, checksum
from source_snapshots where snapshot_id = %s
"""

_INSERT_MEMBERSHIP = """
insert into source_snapshot_observations (snapshot_id, position, observation_id)
values (%s, %s, %s)
on conflict (snapshot_id, position) do nothing
returning snapshot_id
"""

_SELECT_MEMBERSHIP = """
select observation_id from source_snapshot_observations
where snapshot_id = %s and position = %s
"""

_COUNT_MEMBERSHIPS = """
select count(*) from source_snapshot_observations where snapshot_id = %s
"""


def _json(value: Any) -> str:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value
        return json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _observation_values(observation: Observation) -> tuple[Any, ...]:
    return (
        str(observation.kind.value),
        str(observation.subject_id),
        observation.observed_at,
        observation.value,
        observation.unit,
        str(observation.quality.value),
        str(observation.freshness.value),
        observation.source.provider,
        observation.source.source_identifier,
        observation.source.retrieved_at,
        observation.source.revision,
        _json(dict(observation.source.attributes)),
    )


def _persisted_observation_matches(row: Any, observation: Observation) -> bool:
    if row is None or len(row) != 12:
        return False
    expected = _observation_values(observation)
    actual = list(row)
    actual[1] = str(actual[1])
    actual[11] = _json(actual[11])
    return tuple(actual) == expected


class SnapshotRepository:
    """Publish one immutable snapshot and its exact observations atomically."""

    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    def persist(self, snapshot: SourceSnapshot, observations: tuple[Observation, ...]) -> PersistenceResult:
        by_id = {observation.observation_id: observation for observation in observations}
        if len(by_id) != len(observations):
            raise PersistenceError("duplicate observation_id in persistence input")
        if set(by_id) != set(snapshot.observation_ids):
            raise PersistenceError("persistence observations must exactly match snapshot observation_ids")
        ordered = tuple(by_id[observation_id] for observation_id in snapshot.observation_ids)
        if any(observation.source.provider != snapshot.provider for observation in ordered):
            raise PersistenceError("observation provider must match snapshot provider")

        connection = self._connection_factory()
        cursor = connection.cursor()
        inserted_observations = 0
        inserted_memberships = 0
        created_snapshot = False
        try:
            for observation in ordered:
                params = (str(observation.observation_id),) + _observation_values(observation)
                cursor.execute(_INSERT_OBSERVATION, params)
                if cursor.fetchone() is not None:
                    inserted_observations += 1
                else:
                    cursor.execute(_SELECT_OBSERVATION, (str(observation.observation_id),))
                    if not _persisted_observation_matches(cursor.fetchone(), observation):
                        raise PersistenceError("existing observation_id has conflicting immutable content")

            snapshot_values = (
                snapshot.dataset,
                snapshot.provider,
                snapshot.cutoff_at,
                snapshot.published_at,
                snapshot.checksum,
            )
            cursor.execute(_INSERT_SNAPSHOT, (str(snapshot.snapshot_id),) + snapshot_values)
            if cursor.fetchone() is not None:
                created_snapshot = True
            else:
                cursor.execute(_SELECT_SNAPSHOT, (str(snapshot.snapshot_id),))
                row = cursor.fetchone()
                if row is None or tuple(row) != snapshot_values:
                    raise PersistenceError("existing snapshot_id has conflicting immutable content")

            for position, observation_id in enumerate(snapshot.observation_ids):
                cursor.execute(_INSERT_MEMBERSHIP, (str(snapshot.snapshot_id), position, str(observation_id)))
                if cursor.fetchone() is not None:
                    inserted_memberships += 1
                else:
                    cursor.execute(_SELECT_MEMBERSHIP, (str(snapshot.snapshot_id), position))
                    row = cursor.fetchone()
                    if row is None or str(row[0]) != str(observation_id):
                        raise PersistenceError("existing snapshot membership conflicts with immutable order")

            cursor.execute(_COUNT_MEMBERSHIPS, (str(snapshot.snapshot_id),))
            count_row = cursor.fetchone()
            if count_row is None or int(count_row[0]) != len(snapshot.observation_ids):
                raise PersistenceError("persisted snapshot membership count does not match snapshot")

            connection.commit()
            return PersistenceResult(
                snapshot_id=snapshot.snapshot_id,
                created_snapshot=created_snapshot,
                inserted_observations=inserted_observations,
                inserted_memberships=inserted_memberships,
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
