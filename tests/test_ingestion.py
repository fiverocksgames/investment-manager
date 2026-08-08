from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from investment_manager.data import (
    CacheExecution,
    DataQualityState,
    DatasetPolicy,
    FetchRequest,
    FetchResult,
    FreshnessState,
    IngestionFailure,
    IngestionJob,
    IngestionOrchestrator,
    IngestionStatus,
    Observation,
    ObservationKind,
    PersistenceResult,
    ProviderMetadata,
)


NOW = datetime(2026, 8, 8, 8, 0, tzinfo=UTC)
RUN_ID = UUID("00000000-0000-0000-0000-000000000061")


def policy():
    return DatasetPolicy(
        dataset="market_prices",
        expected_cadence=timedelta(days=1),
        aging_after=timedelta(days=2),
        stale_after=timedelta(days=4),
        cache_ttl=timedelta(minutes=15),
    )


def request():
    return FetchRequest(
        dataset="market_prices",
        source_identifiers=("SPY",),
        start_at=NOW - timedelta(days=2),
        end_at=NOW,
    )


def observation(*, quality=DataQualityState.VALID):
    return Observation(
        observation_id=uuid4(),
        kind=ObservationKind.MARKET_PRICE,
        subject_id=uuid4(),
        observed_at=NOW - timedelta(days=1),
        value=Decimal("531.25"),
        unit="USD",
        quality=quality,
        freshness=FreshnessState.FRESH,
        source=ProviderMetadata(
            provider="yahoo",
            source_identifier="SPY",
            retrieved_at=NOW,
        ),
    )


class Repository:
    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail

    def persist(self, snapshot, observations):
        self.calls.append((snapshot, observations))
        if self.fail:
            raise RuntimeError("database unavailable")
        return PersistenceResult(snapshot.snapshot_id, True, len(observations), len(observations))


class Clock:
    def __init__(self):
        self.value = NOW

    def __call__(self):
        value = self.value
        self.value += timedelta(seconds=1)
        return value


def execute(result, *, allow_partial=False, repository=None, cache_hit=False):
    repo = repository or Repository()

    def fetch(req, pol, *, now):
        assert req == request()
        assert pol == policy()
        assert now == NOW
        return CacheExecution(result=result, cache_hit=cache_hit, cached_at=NOW - timedelta(minutes=1) if cache_hit else None, expires_at=NOW + timedelta(minutes=14) if cache_hit else None)

    orchestrator = IngestionOrchestrator(fetch, repo, clock=Clock(), run_id_factory=lambda: RUN_ID)
    execution = orchestrator.execute(
        IngestionJob(
            provider="yahoo",
            request=request(),
            policy=policy(),
            cutoff_at=NOW,
            allow_partial_publication=allow_partial,
        )
    )
    return execution, repo


def test_success_publishes_and_persists_exact_observations():
    obs = observation()
    result = FetchResult(provider="yahoo", request=request(), observations=(obs,))
    execution, repo = execute(result)

    assert execution.run.status is IngestionStatus.SUCCEEDED
    assert execution.run.records_received == 1
    assert execution.run.records_accepted == 1
    assert execution.snapshot is not None
    assert execution.persistence is not None
    assert repo.calls[0][1] == (obs,)
    assert execution.failures == ()


def test_failed_fetch_publishes_nothing():
    failure = IngestionFailure(RUN_ID, "HTTP_429", "rate limited", True, NOW)
    result = FetchResult(provider="yahoo", request=request(), failures=(failure,))
    execution, repo = execute(result)

    assert execution.run.status is IngestionStatus.FAILED
    assert execution.snapshot is None
    assert execution.persistence is None
    assert repo.calls == []
    assert execution.failures[0].run_id == RUN_ID


def test_partial_is_visible_and_denied_by_default():
    obs = observation()
    failure = IngestionFailure(uuid4(), "MISSING_ROW", "one row missing", False, NOW)
    result = FetchResult(provider="yahoo", request=request(), observations=(obs,), failures=(failure,))
    execution, repo = execute(result)

    assert execution.run.status is IngestionStatus.PARTIAL
    assert execution.run.records_received == 1
    assert execution.run.records_accepted == 0
    assert execution.snapshot is None
    assert repo.calls == []
    assert {item.code for item in execution.failures} == {"MISSING_ROW", "PARTIAL_PUBLICATION_DENIED"}


def test_partial_can_be_explicitly_published_without_becoming_success():
    obs = observation(quality=DataQualityState.PARTIAL)
    failure = IngestionFailure(uuid4(), "MISSING_ROW", "one row missing", False, NOW)
    result = FetchResult(provider="yahoo", request=request(), observations=(obs,), failures=(failure,))
    execution, repo = execute(result, allow_partial=True)

    assert execution.run.status is IngestionStatus.PARTIAL
    assert execution.run.records_accepted == 1
    assert execution.snapshot is not None
    assert execution.persistence is not None
    assert repo.calls[0][1] == (obs,)


def test_persistence_failure_is_failed_and_does_not_claim_persistence():
    obs = observation()
    result = FetchResult(provider="yahoo", request=request(), observations=(obs,))
    execution, _ = execute(result, repository=Repository(fail=True))

    assert execution.run.status is IngestionStatus.FAILED
    assert execution.persistence is None
    assert execution.snapshot is None
    assert execution.failures[0].code == "INGESTION_EXECUTION_ERROR"


def test_cache_hit_is_operational_evidence_only():
    obs = observation()
    result = FetchResult(provider="yahoo", request=request(), observations=(obs,))
    execution, _ = execute(result, cache_hit=True)

    assert execution.cache_hit is True
    assert execution.run.status is IngestionStatus.SUCCEEDED
    assert obs.source.retrieved_at == NOW


def test_job_rejects_naive_cutoff():
    try:
        IngestionJob(
            provider="yahoo",
            request=request(),
            policy=policy(),
            cutoff_at=datetime(2026, 8, 8, 8, 0),
        )
    except ValueError as exc:
        assert "timezone-aware" in str(exc)
    else:
        raise AssertionError("naive cutoff must be rejected")
