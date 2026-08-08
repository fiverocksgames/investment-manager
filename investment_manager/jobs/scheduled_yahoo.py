"""Scheduled Yahoo SPY daily ingestion entrypoint.

This module intentionally logs operational metadata only. Database credentials and
provider payloads are never printed.
"""

from __future__ import annotations

import os
import socket
import ssl
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

from investment_manager.data import (
    DatasetPolicy,
    FetchRequest,
    IngestionFetchExecution,
    IngestionJob,
    IngestionOrchestrator,
    IngestionStatus,
    RetryPolicy,
    SnapshotRepository,
    YahooProvider,
    YahooSymbolBinding,
)
from investment_manager.data.operational_status import IngestionStatusRepository
from investment_manager.data.retry import BoundedRetryExecutor


SPY_SUBJECT_ID = uuid5(NAMESPACE_URL, "investment-manager:asset:SPY")


def _connection_factory(database_url: str):
    def connect():
        import psycopg

        return psycopg.connect(database_url, connect_timeout=10)

    return connect


def _safe_database_failure_category(exc: BaseException) -> str:
    """Classify connection failures without inspecting or logging secret-bearing text."""

    if isinstance(exc, TimeoutError):
        return "timeout"
    if isinstance(exc, socket.gaierror):
        return "dns"
    if isinstance(exc, ssl.SSLError):
        return "tls"
    if isinstance(exc, ConnectionError):
        return "connection"

    name = type(exc).__name__.lower()
    if "timeout" in name:
        return "timeout"
    if "authentication" in name or "invalidpassword" in name:
        return "authentication"
    if "operational" in name:
        return "operational"
    return "database"


def _build_execution(database_url: str, now: datetime):
    provider = YahooProvider(
        bindings={
            "SPY": YahooSymbolBinding(
                symbol="SPY",
                subject_id=SPY_SUBJECT_ID,
                unit="USD",
            )
        }
    )
    policy = DatasetPolicy(
        dataset="market_prices",
        expected_cadence=timedelta(days=1),
        aging_after=timedelta(days=2),
        stale_after=timedelta(days=5),
        cache_ttl=timedelta(minutes=30),
        max_attempts=3,
    )
    request = FetchRequest(
        dataset="market_prices",
        source_identifiers=("SPY",),
        start_at=now - timedelta(days=10),
        end_at=now,
    )
    retry = BoundedRetryExecutor(
        policy=RetryPolicy(
            max_attempts=policy.max_attempts,
            base_delay_seconds=5.0,
            max_delay_seconds=30.0,
            jitter_seconds=1.0,
        )
    )

    def fetch_executor(fetch_request, fetch_policy, *, now):
        if fetch_policy != policy:
            raise ValueError("unexpected dataset policy")
        retry_execution = retry.execute(provider, fetch_request)
        return IngestionFetchExecution(
            result=retry_execution.result,
            cache_hit=False,
            provider_attempts=retry_execution.attempts,
        )

    connection_factory = _connection_factory(database_url)
    orchestrator = IngestionOrchestrator(
        fetch_executor,
        SnapshotRepository(connection_factory),
        clock=lambda: datetime.now(UTC),
    )
    execution = orchestrator.execute(
        IngestionJob(
            provider="yahoo",
            request=request,
            policy=policy,
            cutoff_at=now,
            allow_partial_publication=False,
        )
    )
    IngestionStatusRepository(connection_factory).persist(execution)
    return execution


def main() -> int:
    database_url = os.environ.get("SUPABASE_DB_URL", "").strip()
    if not database_url:
        print("scheduled_ingestion_error=missing_SUPABASE_DB_URL")
        return 1

    now = datetime.now(UTC)
    try:
        execution = _build_execution(database_url, now)
    except Exception as exc:
        print(
            " ".join(
                (
                    f"scheduled_ingestion_error={type(exc).__name__}",
                    f"database_failure_category={_safe_database_failure_category(exc)}",
                )
            )
        )
        return 1

    snapshot_id = str(execution.snapshot.snapshot_id) if execution.snapshot is not None else "none"
    print(
        " ".join(
            (
                f"run_id={execution.run.run_id}",
                f"provider={execution.run.provider}",
                f"dataset={execution.run.dataset}",
                f"status={execution.run.status.value}",
                f"provider_attempts={execution.provider_attempts}",
                f"records_received={execution.run.records_received}",
                f"records_accepted={execution.run.records_accepted}",
                f"snapshot_id={snapshot_id}",
            )
        )
    )
    if execution.run.status is IngestionStatus.SUCCEEDED:
        return 0
    if execution.run.status is IngestionStatus.PARTIAL:
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
