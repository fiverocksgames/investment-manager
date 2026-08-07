from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from investment_manager.data.models import (
    DataQualityState,
    FreshnessState,
    Observation,
    ObservationKind,
    ProviderMetadata,
)
from investment_manager.data.persistence import PersistenceError, SnapshotRepository
from investment_manager.data.snapshots import SourceSnapshotPublisher

SUBJECT = UUID("9099d56f-5795-5778-bae0-b5425562d614")
OBS1 = UUID("11111111-1111-5111-8111-111111111111")
OBS2 = UUID("22222222-2222-5222-8222-222222222222")
NOW = datetime(2026, 8, 8, 0, 0, tzinfo=UTC)


class FakeDatabase:
    def __init__(self) -> None:
        self.observations: dict[str, tuple[object, ...]] = {}
        self.snapshots: dict[str, tuple[object, ...]] = {}
        self.memberships: dict[tuple[str, int], str] = {}


class FakeCursor:
    def __init__(self, db: FakeDatabase) -> None:
        self.db = db
        self.result = None
        self.closed = False

    def execute(self, operation: str, parameters=()):
        sql = " ".join(operation.split()).lower()
        if sql.startswith("insert into data_observations"):
            key = parameters[0]
            if key in self.db.observations:
                self.result = None
            else:
                self.db.observations[key] = tuple(parameters[1:])
                self.result = (key,)
        elif sql.startswith("select kind, subject_id"):
            self.result = self.db.observations.get(parameters[0])
        elif sql.startswith("insert into source_snapshots"):
            key = parameters[0]
            if key in self.db.snapshots:
                self.result = None
            else:
                self.db.snapshots[key] = tuple(parameters[1:])
                self.result = (key,)
        elif sql.startswith("select dataset, provider"):
            self.result = self.db.snapshots.get(parameters[0])
        elif sql.startswith("insert into source_snapshot_observations"):
            key = (parameters[0], parameters[1])
            if key in self.db.memberships:
                self.result = None
            else:
                self.db.memberships[key] = parameters[2]
                self.result = (parameters[0],)
        elif sql.startswith("select observation_id from source_snapshot_observations"):
            value = self.db.memberships.get((parameters[0], parameters[1]))
            self.result = None if value is None else (value,)
        elif sql.startswith("select count(*) from source_snapshot_observations"):
            self.result = (sum(1 for key in self.db.memberships if key[0] == parameters[0]),)
        else:
            raise AssertionError(f"unexpected SQL: {sql}")

    def fetchone(self):
        return self.result

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, db: FakeDatabase) -> None:
        self.db = db
        self.cursor_value = FakeCursor(db)
        self.commits = 0
        self.rollbacks = 0
        self.closed = False
        self._backup = None

    def cursor(self):
        self._backup = (
            dict(self.db.observations),
            dict(self.db.snapshots),
            dict(self.db.memberships),
        )
        return self.cursor_value

    def commit(self):
        self.commits += 1
        self._backup = None

    def rollback(self):
        self.rollbacks += 1
        if self._backup is not None:
            observations, snapshots, memberships = self._backup
            self.db.observations = observations
            self.db.snapshots = snapshots
            self.db.memberships = memberships

    def close(self):
        self.closed = True


def observation(observation_id: UUID, value: str = "1350.25") -> Observation:
    return Observation(
        observation_id=observation_id,
        kind=ObservationKind.FX_RATE,
        subject_id=SUBJECT,
        observed_at=NOW - timedelta(days=1),
        value=Decimal(value),
        unit="KRW_per_USD",
        quality=DataQualityState.VALID,
        freshness=FreshnessState.FRESH,
        source=ProviderMetadata(
            provider="yahoo",
            source_identifier="KRW=X",
            retrieved_at=NOW,
            revision=None,
            attributes={"source_base": "USD", "source_quote": "KRW"},
        ),
    )


def snapshot_for(*observations: Observation):
    return SourceSnapshotPublisher().publish(
        dataset="fx_rates",
        provider="yahoo",
        cutoff_at=NOW,
        published_at=NOW,
        observations=tuple(observations),
    )


class PersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = FakeDatabase()
        self.connections: list[FakeConnection] = []

        def factory():
            connection = FakeConnection(self.db)
            self.connections.append(connection)
            return connection

        self.repository = SnapshotRepository(factory)

    def test_persists_snapshot_observations_and_memberships_atomically(self):
        first, second = observation(OBS1), observation(OBS2, "1351.75")
        snapshot = snapshot_for(first, second)

        result = self.repository.persist(snapshot, (second, first))

        self.assertTrue(result.created_snapshot)
        self.assertEqual(result.inserted_observations, 2)
        self.assertEqual(result.inserted_memberships, 2)
        self.assertEqual(self.connections[-1].commits, 1)
        stored = self.db.observations[str(first.observation_id)]
        self.assertIsInstance(stored[3], Decimal)
        self.assertEqual(stored[3], Decimal("1350.25"))
        self.assertEqual(stored[2].tzinfo, UTC)
        self.assertEqual(json.loads(stored[11])["source_base"], "USD")

    def test_identical_replay_is_idempotent(self):
        first, second = observation(OBS1), observation(OBS2, "1351.75")
        snapshot = snapshot_for(first, second)
        self.repository.persist(snapshot, (first, second))

        result = self.repository.persist(snapshot, (second, first))

        self.assertFalse(result.created_snapshot)
        self.assertEqual(result.inserted_observations, 0)
        self.assertEqual(result.inserted_memberships, 0)
        self.assertEqual(len(self.db.observations), 2)
        self.assertEqual(len(self.db.snapshots), 1)
        self.assertEqual(len(self.db.memberships), 2)

    def test_conflicting_existing_observation_rolls_back(self):
        first = observation(OBS1)
        snapshot = snapshot_for(first)
        self.repository.persist(snapshot, (first,))
        stored = list(self.db.observations[str(OBS1)])
        stored[3] = Decimal("9999")
        self.db.observations[str(OBS1)] = tuple(stored)

        with self.assertRaisesRegex(PersistenceError, "conflicting immutable content"):
            self.repository.persist(snapshot, (first,))

        self.assertEqual(self.connections[-1].rollbacks, 1)
        self.assertEqual(self.db.observations[str(OBS1)][3], Decimal("9999"))

    def test_input_must_exactly_match_snapshot_membership_before_connecting(self):
        first, second = observation(OBS1), observation(OBS2)
        snapshot = snapshot_for(first, second)

        with self.assertRaisesRegex(PersistenceError, "exactly match"):
            self.repository.persist(snapshot, (first,))

        self.assertEqual(self.connections, [])

    def test_membership_conflict_rolls_back_transaction(self):
        first = observation(OBS1)
        snapshot = snapshot_for(first)
        self.repository.persist(snapshot, (first,))
        key = (str(snapshot.snapshot_id), 0)
        self.db.memberships[key] = str(OBS2)

        with self.assertRaisesRegex(PersistenceError, "membership conflicts"):
            self.repository.persist(snapshot, (first,))

        self.assertEqual(self.connections[-1].rollbacks, 1)
        self.assertEqual(self.db.memberships[key], str(OBS2))


if __name__ == "__main__":
    unittest.main()
