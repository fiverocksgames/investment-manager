from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

from investment_manager.data.dataset_versions import (
    DatasetVersionError,
    DatasetVersionPersistenceError,
    DatasetVersionPublisher,
    DatasetVersionRepository,
)
from investment_manager.data.models import SourceSnapshot

NOW = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)
SNAP1 = UUID("11111111-1111-5111-8111-111111111111")
SNAP2 = UUID("22222222-2222-5222-8222-222222222222")
OBS = UUID("aaaaaaaa-aaaa-5aaa-8aaa-aaaaaaaaaaaa")


def snapshot(
    snapshot_id: UUID,
    provider: str,
    *,
    dataset: str = "market_prices",
    cutoff_at: datetime | None = None,
    published_at: datetime | None = None,
    checksum_char: str = "a",
) -> SourceSnapshot:
    cutoff = cutoff_at or (NOW - timedelta(hours=2))
    published = published_at or (NOW - timedelta(hours=1))
    return SourceSnapshot(
        snapshot_id=snapshot_id,
        dataset=dataset,
        provider=provider,
        cutoff_at=cutoff,
        published_at=published,
        observation_ids=(OBS,),
        checksum=checksum_char * 64,
    )


class PublisherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.publisher = DatasetVersionPublisher()
        self.yahoo = snapshot(SNAP1, "yahoo", checksum_char="a")
        self.fred = snapshot(SNAP2, "fred", checksum_char="b")

    def test_identity_and_order_are_stable_across_caller_order(self):
        first = self.publisher.publish(
            dataset=" MARKET_PRICES ",
            as_of=NOW,
            created_at=NOW,
            snapshots=(self.yahoo, self.fred),
        )
        second = self.publisher.publish(
            dataset="market_prices",
            as_of=NOW,
            created_at=NOW + timedelta(minutes=5),
            snapshots=(self.fred, self.yahoo),
        )

        self.assertEqual(first.version_id, second.version_id)
        self.assertEqual(first.checksum, second.checksum)
        self.assertEqual(first.snapshot_ids, second.snapshot_ids)
        self.assertEqual(first.snapshot_ids, (SNAP2, SNAP1))
        self.assertEqual(first.as_of.tzinfo, UTC)

    def test_timezone_values_are_normalized_to_utc(self):
        offset = timezone(timedelta(hours=9))
        version = self.publisher.publish(
            dataset="market_prices",
            as_of=NOW.astimezone(offset),
            created_at=NOW.astimezone(offset),
            snapshots=(self.yahoo,),
        )
        self.assertEqual(version.as_of, NOW)
        self.assertEqual(version.created_at, NOW)
        self.assertEqual(version.as_of.tzinfo, UTC)

    def test_rejects_dataset_mismatch(self):
        other = snapshot(SNAP2, "fred", dataset="macro", checksum_char="b")
        with self.assertRaisesRegex(DatasetVersionError, "match the dataset"):
            self.publisher.publish(dataset="market_prices", as_of=NOW, created_at=NOW, snapshots=(other,))

    def test_rejects_duplicate_snapshot_id(self):
        with self.assertRaisesRegex(DatasetVersionError, "duplicate snapshot_id"):
            self.publisher.publish(
                dataset="market_prices",
                as_of=NOW,
                created_at=NOW,
                snapshots=(self.yahoo, self.yahoo),
            )

    def test_rejects_conflicting_provider_cutoff_identity(self):
        other = snapshot(SNAP2, "yahoo", checksum_char="b")
        with self.assertRaisesRegex(DatasetVersionError, "provider/cutoff"):
            self.publisher.publish(
                dataset="market_prices",
                as_of=NOW,
                created_at=NOW,
                snapshots=(self.yahoo, other),
            )

    def test_rejects_lookahead_cutoff(self):
        future = snapshot(SNAP2, "fred", cutoff_at=NOW + timedelta(seconds=1), published_at=NOW + timedelta(seconds=1))
        with self.assertRaisesRegex(DatasetVersionError, "cutoff"):
            self.publisher.publish(dataset="market_prices", as_of=NOW, created_at=NOW + timedelta(minutes=1), snapshots=(future,))

    def test_rejects_snapshot_published_after_version_creation(self):
        future = snapshot(SNAP2, "fred", published_at=NOW + timedelta(seconds=1))
        with self.assertRaisesRegex(DatasetVersionError, "publication"):
            self.publisher.publish(dataset="market_prices", as_of=NOW, created_at=NOW, snapshots=(future,))

    def test_rejects_naive_time(self):
        with self.assertRaisesRegex(DatasetVersionError, "timezone-aware"):
            self.publisher.publish(
                dataset="market_prices",
                as_of=NOW.replace(tzinfo=None),
                created_at=NOW,
                snapshots=(self.yahoo,),
            )


class FakeDatabase:
    def __init__(self) -> None:
        self.snapshots: dict[str, tuple[object, ...]] = {}
        self.versions: dict[str, tuple[object, ...]] = {}
        self.memberships: dict[tuple[str, int], str] = {}


class FakeCursor:
    def __init__(self, db: FakeDatabase) -> None:
        self.db = db
        self.result = None
        self.closed = False

    def execute(self, operation: str, parameters=()):
        sql = " ".join(operation.split()).lower()
        if sql.startswith("select dataset, provider, cutoff_at"):
            self.result = self.db.snapshots.get(parameters[0])
        elif sql.startswith("insert into dataset_versions"):
            key = parameters[0]
            if key in self.db.versions:
                self.result = None
            else:
                self.db.versions[key] = tuple(parameters[1:])
                self.result = (key,)
        elif sql.startswith("select dataset, as_of, created_at"):
            self.result = self.db.versions.get(parameters[0])
        elif sql.startswith("insert into dataset_version_snapshots"):
            key = (parameters[0], parameters[1])
            if key in self.db.memberships:
                self.result = None
            else:
                self.db.memberships[key] = parameters[2]
                self.result = (parameters[0],)
        elif sql.startswith("select snapshot_id from dataset_version_snapshots"):
            value = self.db.memberships.get((parameters[0], parameters[1]))
            self.result = None if value is None else (value,)
        elif sql.startswith("select count(*) from dataset_version_snapshots"):
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
        self._backup = (dict(self.db.versions), dict(self.db.memberships))
        return self.cursor_value

    def commit(self):
        self.commits += 1
        self._backup = None

    def rollback(self):
        self.rollbacks += 1
        if self._backup is not None:
            versions, memberships = self._backup
            self.db.versions = versions
            self.db.memberships = memberships

    def close(self):
        self.closed = True


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.yahoo = snapshot(SNAP1, "yahoo", checksum_char="a")
        self.fred = snapshot(SNAP2, "fred", checksum_char="b")
        self.version = DatasetVersionPublisher().publish(
            dataset="market_prices", as_of=NOW, created_at=NOW, snapshots=(self.yahoo, self.fred)
        )
        self.db = FakeDatabase()
        for item in (self.yahoo, self.fred):
            self.db.snapshots[str(item.snapshot_id)] = (
                item.dataset,
                item.provider,
                item.cutoff_at,
                item.published_at,
                item.checksum,
            )
        self.connections: list[FakeConnection] = []

        def factory():
            connection = FakeConnection(self.db)
            self.connections.append(connection)
            return connection

        self.repository = DatasetVersionRepository(factory)

    def test_persists_version_and_memberships_atomically(self):
        result = self.repository.persist(self.version, (self.yahoo, self.fred))
        self.assertTrue(result.created_version)
        self.assertEqual(result.inserted_memberships, 2)
        self.assertEqual(self.connections[-1].commits, 1)
        self.assertEqual(len(self.db.versions), 1)
        self.assertEqual(len(self.db.memberships), 2)

    def test_identical_replay_is_idempotent(self):
        self.repository.persist(self.version, (self.yahoo, self.fred))
        result = self.repository.persist(self.version, (self.fred, self.yahoo))
        self.assertFalse(result.created_version)
        self.assertEqual(result.inserted_memberships, 0)
        self.assertEqual(len(self.db.versions), 1)
        self.assertEqual(len(self.db.memberships), 2)

    def test_missing_source_snapshot_rolls_back(self):
        del self.db.snapshots[str(SNAP1)]
        with self.assertRaisesRegex(DatasetVersionPersistenceError, "must exist"):
            self.repository.persist(self.version, (self.yahoo, self.fred))
        self.assertEqual(self.connections[-1].rollbacks, 1)
        self.assertEqual(self.db.versions, {})

    def test_conflicting_existing_version_rolls_back(self):
        self.repository.persist(self.version, (self.yahoo, self.fred))
        key = str(self.version.version_id)
        stored = list(self.db.versions[key])
        stored[-1] = "f" * 64
        self.db.versions[key] = tuple(stored)
        with self.assertRaisesRegex(DatasetVersionPersistenceError, "conflicting immutable content"):
            self.repository.persist(self.version, (self.yahoo, self.fred))
        self.assertEqual(self.connections[-1].rollbacks, 1)

    def test_membership_conflict_rolls_back(self):
        self.repository.persist(self.version, (self.yahoo, self.fred))
        key = (str(self.version.version_id), 0)
        self.db.memberships[key] = str(SNAP1 if self.db.memberships[key] != str(SNAP1) else SNAP2)
        with self.assertRaisesRegex(DatasetVersionPersistenceError, "membership conflicts"):
            self.repository.persist(self.version, (self.yahoo, self.fred))
        self.assertEqual(self.connections[-1].rollbacks, 1)

    def test_input_must_exactly_match_before_connecting(self):
        with self.assertRaisesRegex(DatasetVersionPersistenceError, "exactly match"):
            self.repository.persist(self.version, (self.yahoo,))
        self.assertEqual(self.connections, [])


if __name__ == "__main__":
    unittest.main()
