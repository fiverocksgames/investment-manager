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


@dataclass(frozen=True, slots=True)
class IngestionFetchExecution:
    """Canonical fetch result plus operational attempt/cache evidence."""

    result: FetchResult
    cache_hit: bool = False
    provider_attempts: int = 1

    def __post_init__(self) -> None:
        if self.provider_attempts < 0:
            raise ValueError("provider_attempts must not be negative")
        if not self.cache_hit and self.provider_attempts < 1:
            raise ValueError("non-cache fetch execution requires at least one provider attempt")


class FetchExecutor(Protocol):
    def __call__(
        self,
        request: FetchRequest,
        policy: DatasetPolicy,
        *,
        now: datetime,
    ) -> IngestionFetchExecution | CacheExecution: ...


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
    provider_attempts: int = 1

    def __post_init__(self) -> None:
        if self.provider_attempts < 0:
            raise ValueError("provider_attempts must not be negative")


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
        provider_attempts = 1
        cache_hit = False
        try:
            raw_execution = self._fetch_executor(job.request, job.policy, now=started)
            if isinstance(raw_execution, CacheExecution):
                result = raw_execution.result
                cache_hit = raw_execution.cache_hit
                provider_attempts = 0 if cache_hit else 1
            else:
                result = raw_execution.result
                cache_hit = raw_execution.cache_hit
                provider_attempts = raw_execution.provider_attempts

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
                    cache_hit=cache_hit,
                    provider_attempts=provider_attempts,
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
                    cache_hit=cache_hit,
                    provider_attempts=provider_attempts,
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
            eligible_ids = set(snapshot.observation_ids)
            eligible = tuple(
                observation for observation in result.observations if observation.observation_id in eligible_ids
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
                cache_hit=cache_hit,
                provider_attempts=provider_attempts,
            )
        except Exception as exc:
            failure = IngestionFailure(
                run_id=run_id,
                code="INGESTION_EXECUTION_ERROR",
                message=f"ingestion execution failed: {type(exc).__name__}",
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
                cache_hit=cache_hit,
                provider_attempts=provider_attempts,
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
        provider_attempts: int = 1,
    ) -> IngestionExecution:
        ended = _utc(self._clock(), "ended_at")
        run = IngestionRun(
            run_id=run_id,
            provider=job.provider,
            dataset=job.request.dataset,
            started_at=started,
            ended_at=ended,
            status=status,
            attempt=max(1, provider_attempts),
            records_received=records_received,
            records_accepted=records_accepted,
        )
        return IngestionExecution(
            run=run,
            failures=failures,
            snapshot=snapshot,
            persistence=persistence,
            cache_hit=cache_hit,
            provider_attempts=provider_attempts,
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
