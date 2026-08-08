"""Durable persistence for ingestion-run and failure evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from uuid import UUID

from .ingestion import IngestionExecution
from .persistence import Connection


class OperationalStatusError(RuntimeError):
    """Raised when durable operational evidence conflicts with an existing run."""


@dataclass(frozen=True, slots=True)
class OperationalStatusResult:
    run_id: UUID
    created_run: bool
    inserted_failures: int


_INSERT_RUN = """
insert into ingestion_runs (
    run_id, provider, dataset, started_at, ended_at, status, attempt,
    provider_attempts, records_received, records_accepted, cache_hit, snapshot_id
) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
on conflict (run_id) do nothing
returning run_id
"""

_SELECT_RUN = """
select provider, dataset, started_at, ended_at, status, attempt,
       provider_attempts, records_received, records_accepted, cache_hit, snapshot_id
from ingestion_runs where run_id = %s
"""

_INSERT_FAILURE = """
insert into ingestion_failures (
    run_id, position, code, message, retryable, occurred_at, provider_reference
) values (%s, %s, %s, %s, %s, %s, %s)
on conflict (run_id, position) do nothing
returning run_id
"""

_SELECT_FAILURE = """
select code, message, retryable, occurred_at, provider_reference
from ingestion_failures where run_id = %s and position = %s
"""

_COUNT_FAILURES = """
select count(*) from ingestion_failures where run_id = %s
"""


def _run_values(execution: IngestionExecution) -> tuple[Any, ...]:
    run = execution.run
    return (
        run.provider,
        run.dataset,
        run.started_at,
        run.ended_at,
        run.status.value,
        run.attempt,
        execution.provider_attempts,
        run.records_received,
        run.records_accepted,
        execution.cache_hit,
        str(execution.snapshot.snapshot_id) if execution.snapshot is not None else None,
    )


def _failure_values(failure) -> tuple[Any, ...]:
    return (
        failure.code,
        failure.message,
        failure.retryable,
        failure.occurred_at,
        failure.provider_reference,
    )


class IngestionStatusRepository:
    """Persist one terminal ingestion execution atomically and idempotently."""

    def __init__(self, connection_factory: Callable[[], Connection]) -> None:
        self._connection_factory = connection_factory

    def persist(self, execution: IngestionExecution) -> OperationalStatusResult:
        if execution.run.ended_at is None:
            raise OperationalStatusError("only terminal ingestion runs may be persisted")
        if any(failure.run_id != execution.run.run_id for failure in execution.failures):
            raise OperationalStatusError("all failures must reference the persisted ingestion run")

        connection = self._connection_factory()
        cursor = connection.cursor()
        inserted_failures = 0
        created_run = False
        try:
            run_id = str(execution.run.run_id)
            expected_run = _run_values(execution)
            cursor.execute(_INSERT_RUN, (run_id,) + expected_run)
            if cursor.fetchone() is not None:
                created_run = True
            else:
                cursor.execute(_SELECT_RUN, (run_id,))
                row = cursor.fetchone()
                if row is None or tuple(str(value) if index == 10 and value is not None else value for index, value in enumerate(row)) != expected_run:
                    raise OperationalStatusError("existing run_id has conflicting immutable operational content")

            for position, failure in enumerate(execution.failures):
                expected_failure = _failure_values(failure)
                cursor.execute(_INSERT_FAILURE, (run_id, position) + expected_failure)
                if cursor.fetchone() is not None:
                    inserted_failures += 1
                else:
                    cursor.execute(_SELECT_FAILURE, (run_id, position))
                    row = cursor.fetchone()
                    if row is None or tuple(row) != expected_failure:
                        raise OperationalStatusError("existing ingestion failure conflicts with immutable order/content")

            cursor.execute(_COUNT_FAILURES, (run_id,))
            count = cursor.fetchone()
            if count is None or int(count[0]) != len(execution.failures):
                raise OperationalStatusError("persisted ingestion failure count does not match execution")

            connection.commit()
            return OperationalStatusResult(
                run_id=execution.run.run_id,
                created_run=created_run,
                inserted_failures=inserted_failures,
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
