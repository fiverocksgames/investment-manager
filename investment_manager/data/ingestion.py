"""Provider-independent ingestion orchestration with explicit operational evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable, Protocol
from uuid import UUID, uuid4

from .cache import CacheExecution
from .models import DatasetPolicy, IngestionFailure, IngestionRun, IngestionStatus, SourceSnapshot
from .persistence import PersistenceResult
from .providers import FetchRequest, FetchResult
from .snapshots import SnapshotPublicationPolicy, SourceSnapshotPublisher


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


class FetchExecutor(Protocol):
    def __call__(self, request: FetchRequest, policy: DatasetPolicy, *, now: datetime) -> CacheExecution: ...


class SnapshotPersister(Protocol):
    def persist(self, snapshot: SourceSnapshot, observations: tuple) -> PersistenceResult: ...


@dataclass(frozen=True, slots=True)
class IngestionJob:
    provider: str
    request: FetchRequest
    policy: DatasetPolicy
    cutoff_at: datetime
    allow_partial_publication: bool = False

    def __post_init__(self) -> None:
        provider = self.provider.strip().lower()
        if not provider:
            raise ValueError("provider must not be empty")
        object.__setattr__(self, "provider", provider)
        if self.request.dataset != self.policy.dataset:
            raise ValueError("request dataset must match policy dataset")
        object.__setattr__(self, "cutoff_at", _utc(self.cutoff_at, "cutoff_at"))


@dataclass(frozen=True, slots=True)
class IngestionExecution:
    run: IngestionRun
    failures: tuple[IngestionFailure, ...]
    snapshot: SourceSnapshot | None = None
    persistence: PersistenceResult | None = None
    cache_hit: bool = False


class IngestionOrchestrator:
    """Compose fetch, publication, and persistence without hiding failures."""

    def __init__(
        self,
        fetch_executor: FetchExecutor,
        repository: SnapshotPersister,
        *,
        clock: Callable[[], datetime],
        run_id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._fetch_executor = fetch_executor
        self._repository = repository
        self._clock = clock
        self._run_id_factory = run_id_factory

    def execute(self, job: IngestionJob) -> IngestionExecution:
        run_id = self._run_id_factory()
        started = _utc(self._clock(), "started_at")
        try:
            cache_execution = self._fetch_executor(job.request, job.policy, now=started)
            result = cache_execution.result
            if result.provider != job.provider:
                raise ValueError("fetch result provider must match ingestion job provider")
            if result.request != job.request:
                raise ValueError("fetch result request must match ingestion job request")

            received = len(result.observations)
            failures = self._rebind_failures(result, run_id)
            if not result.observations:
                return self._terminal(
                    run_id=run_id,
                    job=job,
                    started=started,
                    status=IngestionStatus.FAILED,
                    records_received=0,
                    records_accepted=0,
                    failures=failures,
                    cache_hit=cache_execution.cache_hit,
                )

            if result.partial and not job.allow_partial_publication:
                denied = IngestionFailure(
                    run_id=run_id,
                    code="PARTIAL_PUBLICATION_DENIED",
                    message="partial provider result is not publishable by ingestion policy",
                    retryable=False,
                    occurred_at=_utc(self._clock(), "failure_at"),
                )
                return self._terminal(
                    run_id=run_id,
                    job=job,
                    started=started,
                    status=IngestionStatus.PARTIAL,
                    records_received=received,
                    records_accepted=0,
                    failures=failures + (denied,),
                    cache_hit=cache_execution.cache_hit,
                )

            publisher = SourceSnapshotPublisher(
                SnapshotPublicationPolicy(allow_partial_quality=job.allow_partial_publication)
            )
            published_at = _utc(self._clock(), "published_at")
            snapshot = publisher.publish(
                dataset=job.request.dataset,
                provider=job.provider,
                cutoff_at=job.cutoff_at,
                published_at=published_at,
                observations=result.observations,
            )
            eligible = tuple(
                observation
                for observation in result.observations
                if observation.observation_id in set(snapshot.observation_ids)
            )
            persistence = self._repository.persist(snapshot, eligible)
            status = IngestionStatus.PARTIAL if result.partial else IngestionStatus.SUCCEEDED
            return self._terminal(
                run_id=run_id,
                job=job,
                started=started,
                status=status,
                records_received=received,
                records_accepted=len(eligible),
                failures=failures,
                snapshot=snapshot,
                persistence=persistence,
                cache_hit=cache_execution.cache_hit,
            )
        except Exception as exc:
            failure = IngestionFailure(
                run_id=run_id,
                code="INGESTION_EXECUTION_ERROR",
                message=f"{type(exc).__name__}: {exc}",
                retryable=False,
                occurred_at=_utc(self._clock(), "failure_at"),
            )
            return self._terminal(
                run_id=run_id,
                job=job,
                started=started,
                status=IngestionStatus.FAILED,
                records_received=0,
                records_accepted=0,
                failures=(failure,),
            )

    def _terminal(
        self,
        *,
        run_id: UUID,
        job: IngestionJob,
        started: datetime,
        status: IngestionStatus,
        records_received: int,
        records_accepted: int,
        failures: tuple[IngestionFailure, ...],
        snapshot: SourceSnapshot | None = None,
        persistence: PersistenceResult | None = None,
        cache_hit: bool = False,
    ) -> IngestionExecution:
        ended = _utc(self._clock(), "ended_at")
        run = IngestionRun(
            run_id=run_id,
            provider=job.provider,
            dataset=job.request.dataset,
            started_at=started,
            ended_at=ended,
            status=status,
            records_received=records_received,
            records_accepted=records_accepted,
        )
        return IngestionExecution(
            run=run,
            failures=failures,
            snapshot=snapshot,
            persistence=persistence,
            cache_hit=cache_hit,
        )

    @staticmethod
    def _rebind_failures(result: FetchResult, run_id: UUID) -> tuple[IngestionFailure, ...]:
        return tuple(
            IngestionFailure(
                run_id=run_id,
                code=failure.code,
                message=failure.message,
                retryable=failure.retryable,
                occurred_at=failure.occurred_at,
                provider_reference=failure.provider_reference,
            )
            for failure in result.failures
        )
