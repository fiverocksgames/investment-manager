import unittest
from datetime import UTC, datetime, timedelta
from uuid import UUID

from investment_manager.data import (
    DatasetVersionError,
    DatasetVersionPublisher,
    DatasetVersionRepository,
    SourceSnapshot,
)


AS_OF = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)
CREATED = AS_OF + timedelta(seconds=1)


def snapshot(number: int, *, dataset="market_prices", provider="yahoo", cutoff=None, checksum=None, published_at=None):
    cutoff = cutoff or (AS_OF - timedelta(days=number))
    return SourceSnapshot(
        snapshot_id=UUID(f"00000000-0000-0000-0000-{number:012d}"),
        dataset=dataset,
        provider=provider,
        cutoff_at=cutoff,
        published_at=published_at or (cutoff + timedelta(seconds=1)),
        observation_ids=(UUID(f"10000000-0000-0000-0000-{number:012d}"),),
        checksum=checksum or (f"{number:064x}"[-64:]),
    )


class DatasetVersionPublisherTests(unittest.TestCase):
    def test_identity_is_stable_across_input_order(self):
        one = snapshot(1, provider="fred")
        two = snapshot(2, provider="yahoo")
        publisher = DatasetVersionPublisher()

        left = publisher.publish(dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(one, two))
        right = publisher.publish(
            dataset="market_prices",
            as_of=AS_OF,
            created_at=CREATED + timedelta(minutes=5),
            snapshots=(two, one),
        )

        self.assertEqual(left.version_id, right.version_id)
        self.assertEqual(left.checksum, right.checksum)
        self.assertEqual(left.snapshot_ids, right.snapshot_ids)

    def test_created_at_is_not_part_of_identity(self):
        item = snapshot(1)
        publisher = DatasetVersionPublisher()
        first = publisher.publish(dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(item,))
        later = publisher.publish(
            dataset="market_prices",
            as_of=AS_OF,
            created_at=CREATED + timedelta(hours=1),
            snapshots=(item,),
        )
        self.assertEqual(first.version_id, later.version_id)
        self.assertEqual(first.checksum, later.checksum)

    def test_rejects_dataset_mismatch_duplicate_and_future_cutoff(self):
        publisher = DatasetVersionPublisher()
        item = snapshot(1)
        with self.assertRaisesRegex(DatasetVersionError, "dataset must match"):
            publisher.publish(dataset="fx_rates", as_of=AS_OF, created_at=CREATED, snapshots=(item,))
        with self.assertRaisesRegex(DatasetVersionError, "duplicate snapshot_id"):
            publisher.publish(dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(item, item))
        future = snapshot(3, cutoff=AS_OF + timedelta(seconds=1))
        with self.assertRaisesRegex(DatasetVersionError, "cutoff must not exceed"):
            publisher.publish(dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(future,))

    def test_rejects_snapshot_published_after_version_creation(self):
        publisher = DatasetVersionPublisher()
        item = snapshot(1, published_at=CREATED + timedelta(seconds=1))
        with self.assertRaisesRegex(DatasetVersionError, "published_at must not exceed"):
            publisher.publish(dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(item,))

    def test_rejects_conflicting_same_provider_cutoff_boundary(self):
        publisher = DatasetVersionPublisher()
        one = snapshot(1, provider="yahoo", cutoff=AS_OF - timedelta(days=1), checksum="1" * 64)
        two = snapshot(2, provider="yahoo", cutoff=AS_OF - timedelta(days=1), checksum="2" * 64)
        with self.assertRaisesRegex(DatasetVersionError, "conflicting snapshots"):
            publisher.publish(dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(one, two))

    def test_rejects_naive_times(self):
        publisher = DatasetVersionPublisher()
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            publisher.publish(
                dataset="market_prices",
                as_of=datetime(2026, 8, 8, 12, 0),
                created_at=CREATED,
                snapshots=(snapshot(1),),
            )


class FakeCursor:
    def __init__(self, state):
        self.state = state
        self.row = None

    def execute(self, operation, parameters=()):
        compact = " ".join(operation.split()).lower()
        self.row = None
        if compact.startswith("select dataset, provider, cutoff_at, published_at, checksum from source_snapshots"):
            self.row = self.state["snapshots"].get(parameters[0])
        elif compact.startswith("insert into dataset_versions"):
            version_id = parameters[0]
            if version_id not in self.state["versions"]:
                self.state["versions"][version_id] = tuple(parameters[1:])
                self.row = (version_id,)
        elif compact.startswith("select dataset, as_of, created_at, checksum from dataset_versions"):
            self.row = self.state["versions"].get(parameters[0])
        elif compact.startswith("insert into dataset_version_snapshots"):
            key = (parameters[0], parameters[1])
            if key not in self.state["memberships"]:
                self.state["memberships"][key] = parameters[2]
                self.row = (parameters[0],)
        elif compact.startswith("select snapshot_id from dataset_version_snapshots"):
            value = self.state["memberships"].get((parameters[0], parameters[1]))
            self.row = None if value is None else (value,)
        elif compact.startswith("select count(*) from dataset_version_snapshots"):
            self.row = (sum(1 for key in self.state["memberships"] if key[0] == parameters[0]),)
        else:
            raise AssertionError(f"unexpected SQL: {compact}")

    def fetchone(self):
        return self.row

    def close(self):
        pass


class FakeConnection:
    def __init__(self, state):
        self.state = state
        self.committed = False
        self.rolled_back = False
        self._backup = None

    def cursor(self):
        self._backup = (
            dict(self.state["versions"]),
            dict(self.state["memberships"]),
        )
        return FakeCursor(self.state)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True
        if self._backup is not None:
            self.state["versions"].clear()
            self.state["versions"].update(self._backup[0])
            self.state["memberships"].clear()
            self.state["memberships"].update(self._backup[1])

    def close(self):
        pass


def persisted_snapshot_row(item):
    return (item.dataset, item.provider, item.cutoff_at, item.published_at, item.checksum)


class DatasetVersionRepositoryTests(unittest.TestCase):
    def test_repository_persists_and_replays_idempotently(self):
        one = snapshot(1, provider="fred")
        two = snapshot(2, provider="yahoo")
        version = DatasetVersionPublisher().publish(
            dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(one, two)
        )
        state = {
            "snapshots": {
                str(one.snapshot_id): persisted_snapshot_row(one),
                str(two.snapshot_id): persisted_snapshot_row(two),
            },
            "versions": {},
            "memberships": {},
        }
        connections = []

        def factory():
            connection = FakeConnection(state)
            connections.append(connection)
            return connection

        repository = DatasetVersionRepository(factory)
        first = repository.persist(version, (two, one))
        second = repository.persist(version, (one, two))

        self.assertTrue(first.created_version)
        self.assertEqual(first.inserted_memberships, 2)
        self.assertFalse(second.created_version)
        self.assertEqual(second.inserted_memberships, 0)
        self.assertTrue(connections[0].committed and connections[1].committed)

    def test_repository_conflict_rolls_back(self):
        item = snapshot(1)
        version = DatasetVersionPublisher().publish(
            dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(item,)
        )
        state = {
            "snapshots": {str(item.snapshot_id): persisted_snapshot_row(item)},
            "versions": {str(version.version_id): (version.dataset, version.as_of, version.created_at, "f" * 64)},
            "memberships": {},
        }
        connection = FakeConnection(state)
        repository = DatasetVersionRepository(lambda: connection)

        with self.assertRaisesRegex(DatasetVersionError, "conflicting immutable content"):
            repository.persist(version, (item,))

        self.assertTrue(connection.rolled_back)
        self.assertEqual(state["memberships"], {})

    def test_repository_rejects_persisted_snapshot_publication_conflict(self):
        item = snapshot(1)
        version = DatasetVersionPublisher().publish(
            dataset="market_prices", as_of=AS_OF, created_at=CREATED, snapshots=(item,)
        )
        persisted = list(persisted_snapshot_row(item))
        persisted[3] = item.published_at + timedelta(minutes=1)
        state = {
            "snapshots": {str(item.snapshot_id): tuple(persisted)},
            "versions": {},
            "memberships": {},
        }
        connection = FakeConnection(state)
        repository = DatasetVersionRepository(lambda: connection)

        with self.assertRaisesRegex(DatasetVersionError, "missing or conflicts"):
            repository.persist(version, (item,))

        self.assertTrue(connection.rolled_back)
        self.assertEqual(state["versions"], {})
        self.assertEqual(state["memberships"], {})


if __name__ == "__main__":
    unittest.main()
