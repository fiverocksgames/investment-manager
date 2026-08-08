import unittest
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

from investment_manager.data.analysis_inputs import (
    AnalysisInputManifestError,
    AnalysisInputManifestPublisher,
    AnalysisInputManifestRepository,
)
from investment_manager.data.versioning import DatasetVersion


AS_OF = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)
CREATED = AS_OF + timedelta(minutes=10)


def version(number: int, dataset: str, *, as_of=AS_OF - timedelta(hours=1), created_at=None, checksum=None):
    return DatasetVersion(
        version_id=UUID(int=number),
        dataset=dataset,
        as_of=as_of,
        created_at=created_at or as_of + timedelta(minutes=5),
        snapshot_ids=(UUID(int=100 + number),),
        checksum=checksum or format(number, "064x"),
    )


class AnalysisInputManifestPublisherTests(unittest.TestCase):
    def test_identity_is_stable_across_input_order_and_created_at(self):
        prices = version(1, "market_prices")
        rates = version(2, "macro_rates")
        publisher = AnalysisInputManifestPublisher()
        first = publisher.publish(as_of=AS_OF, created_at=CREATED, versions=(prices, rates))
        later = publisher.publish(as_of=AS_OF, created_at=CREATED + timedelta(hours=1), versions=(rates, prices))
        self.assertEqual(first.manifest_id, later.manifest_id)
        self.assertEqual(first.checksum, later.checksum)
        self.assertEqual(first.version_ids, later.version_ids)

    def test_normalizes_aware_boundaries_to_utc(self):
        publisher = AnalysisInputManifestPublisher()
        offset = timezone(timedelta(hours=9))
        local_as_of = AS_OF.astimezone(offset)
        local_created = CREATED.astimezone(offset)
        manifest = publisher.publish(
            as_of=local_as_of,
            created_at=local_created,
            versions=(version(1, "market_prices"),),
        )
        self.assertEqual(manifest.as_of, AS_OF)
        self.assertEqual(manifest.created_at, CREATED)

    def test_rejects_empty_duplicate_dataset_and_lookahead(self):
        publisher = AnalysisInputManifestPublisher()
        with self.assertRaisesRegex(AnalysisInputManifestError, "requires dataset versions"):
            publisher.publish(as_of=AS_OF, created_at=CREATED, versions=())
        with self.assertRaisesRegex(AnalysisInputManifestError, "one version per dataset"):
            publisher.publish(
                as_of=AS_OF,
                created_at=CREATED,
                versions=(version(1, "market_prices"), version(2, "market_prices")),
            )
        future = version(3, "macro_rates", as_of=AS_OF + timedelta(seconds=1))
        with self.assertRaisesRegex(AnalysisInputManifestError, "as_of must not exceed"):
            publisher.publish(as_of=AS_OF, created_at=CREATED, versions=(future,))

    def test_rejects_version_created_after_manifest_creation_and_naive_boundary(self):
        publisher = AnalysisInputManifestPublisher()
        late = version(
            1,
            "market_prices",
            as_of=AS_OF - timedelta(hours=1),
            created_at=CREATED + timedelta(seconds=1),
        )
        with self.assertRaisesRegex(AnalysisInputManifestError, "created_at must not exceed"):
            publisher.publish(as_of=AS_OF, created_at=CREATED, versions=(late,))
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            publisher.publish(
                as_of=datetime(2026, 8, 8, 12, 0),
                created_at=CREATED,
                versions=(version(1, "market_prices"),),
            )


class FakeCursor:
    def __init__(self, state):
        self.state = state
        self.row = None
        self.closed = False

    def execute(self, operation, parameters=()):
        compact = " ".join(operation.split())
        if compact.startswith("select dataset, as_of, created_at, checksum from dataset_versions"):
            self.row = self.state["versions"].get(parameters[0])
        elif compact.startswith("insert into analysis_input_manifests"):
            manifest_id = parameters[0]
            if manifest_id in self.state["manifests"]:
                self.row = None
            else:
                self.state["manifests"][manifest_id] = parameters[1:]
                self.row = (manifest_id,)
        elif compact.startswith("select as_of, created_at, checksum from analysis_input_manifests"):
            self.row = self.state["manifests"].get(parameters[0])
        elif compact.startswith("insert into analysis_input_manifest_versions"):
            key = (parameters[0], parameters[1])
            if key in self.state["memberships"]:
                self.row = None
            else:
                self.state["memberships"][key] = (parameters[2], parameters[3])
                self.row = (parameters[0],)
        elif compact.startswith("select dataset, version_id from analysis_input_manifest_versions"):
            self.row = self.state["memberships"].get((parameters[0], parameters[1]))
        elif compact.startswith("select count(*) from analysis_input_manifest_versions"):
            manifest_id = parameters[0]
            count = sum(1 for key in self.state["memberships"] if key[0] == manifest_id)
            self.row = (count,)
        else:
            raise AssertionError(f"unexpected SQL: {compact}")

    def fetchone(self):
        return self.row

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, state):
        self.state = state
        self.snapshot = {
            "manifests": dict(state["manifests"]),
            "memberships": dict(state["memberships"]),
        }
        self.cursor_value = FakeCursor(state)
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self.cursor_value

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True
        self.state["manifests"].clear()
        self.state["manifests"].update(self.snapshot["manifests"])
        self.state["memberships"].clear()
        self.state["memberships"].update(self.snapshot["memberships"])

    def close(self):
        self.closed = True


def persisted_version_row(item):
    return (item.dataset, item.as_of, item.created_at, item.checksum)


class AnalysisInputManifestRepositoryTests(unittest.TestCase):
    def test_repository_persists_and_replays_idempotently(self):
        prices = version(1, "market_prices")
        rates = version(2, "macro_rates")
        manifest = AnalysisInputManifestPublisher().publish(
            as_of=AS_OF, created_at=CREATED, versions=(prices, rates)
        )
        state = {
            "versions": {
                str(prices.version_id): persisted_version_row(prices),
                str(rates.version_id): persisted_version_row(rates),
            },
            "manifests": {},
            "memberships": {},
        }
        connections = []

        def factory():
            connection = FakeConnection(state)
            connections.append(connection)
            return connection

        repository = AnalysisInputManifestRepository(factory)
        first = repository.persist(manifest, (rates, prices))
        second = repository.persist(manifest, (prices, rates))
        self.assertTrue(first.created_manifest)
        self.assertEqual(first.inserted_memberships, 2)
        self.assertFalse(second.created_manifest)
        self.assertEqual(second.inserted_memberships, 0)
        self.assertTrue(all(connection.committed for connection in connections))

    def test_repository_rejects_missing_or_conflicting_version_and_rolls_back(self):
        prices = version(1, "market_prices")
        manifest = AnalysisInputManifestPublisher().publish(
            as_of=AS_OF, created_at=CREATED, versions=(prices,)
        )
        state = {"versions": {}, "manifests": {}, "memberships": {}}
        connection = FakeConnection(state)
        repository = AnalysisInputManifestRepository(lambda: connection)
        with self.assertRaisesRegex(AnalysisInputManifestError, "missing or conflicts"):
            repository.persist(manifest, (prices,))
        self.assertTrue(connection.rolled_back)
        self.assertEqual(state["manifests"], {})
        self.assertEqual(state["memberships"], {})

    def test_repository_conflicting_manifest_content_rolls_back(self):
        prices = version(1, "market_prices")
        manifest = AnalysisInputManifestPublisher().publish(
            as_of=AS_OF, created_at=CREATED, versions=(prices,)
        )
        state = {
            "versions": {str(prices.version_id): persisted_version_row(prices)},
            "manifests": {str(manifest.manifest_id): (manifest.as_of, manifest.created_at, "f" * 64)},
            "memberships": {},
        }
        connection = FakeConnection(state)
        repository = AnalysisInputManifestRepository(lambda: connection)
        with self.assertRaisesRegex(AnalysisInputManifestError, "conflicting immutable content"):
            repository.persist(manifest, (prices,))
        self.assertTrue(connection.rolled_back)
        self.assertEqual(state["memberships"], {})


if __name__ == "__main__":
    unittest.main()
