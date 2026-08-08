from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from investment_manager.data import (
    DatasetPolicy,
    FetchRequest,
    FetchResult,
    IngestionFailure,
    IngestionFetchExecution,
    IngestionJob,
    IngestionOrchestrator,
    IngestionStatus,
)


NOW = datetime(2026, 8, 8, 9, 0, tzinfo=UTC)
RUN_ID = UUID("00000000-0000-0000-0000-000000000064")


class NeverRepository:
    def persist(self, snapshot, observations):
        raise AssertionError("repository must not be called")


def request():
    return FetchRequest(
        dataset="market_prices",
        source_identifiers=("SPY",),
        start_at=NOW - timedelta(days=10),
        end_at=NOW,
    )


def policy():
    return DatasetPolicy(
        dataset="market_prices",
        expected_cadence=timedelta(days=1),
        aging_after=timedelta(days=2),
        stale_after=timedelta(days=5),
        cache_ttl=timedelta(minutes=30),
        max_attempts=3,
    )


def job():
    return IngestionJob(provider="yahoo", request=request(), policy=policy(), cutoff_at=NOW)


def test_provider_attempt_count_is_preserved_on_failed_retry_execution():
    provider_failure = IngestionFailure(
        run_id=RUN_ID,
        code="HTTP_503",
        message="provider unavailable",
        retryable=True,
        occurred_at=NOW,
    )
    result = FetchResult(provider="yahoo", request=request(), failures=(provider_failure,))

    def fetch_executor(req, pol, *, now):
        return IngestionFetchExecution(result=result, provider_attempts=3)

    execution = IngestionOrchestrator(
        fetch_executor,
        NeverRepository(),
        clock=lambda: NOW,
        run_id_factory=lambda: RUN_ID,
    ).execute(job())

    assert execution.run.status is IngestionStatus.FAILED
    assert execution.provider_attempts == 3
    assert execution.run.attempt == 3


def test_catch_all_failure_does_not_persist_raw_exception_text():
    secret_like = "postgresql://user:super-secret@db.example.invalid/postgres"

    def fetch_executor(req, pol, *, now):
        raise RuntimeError(secret_like)

    execution = IngestionOrchestrator(
        fetch_executor,
        NeverRepository(),
        clock=lambda: NOW,
        run_id_factory=lambda: RUN_ID,
    ).execute(job())

    assert execution.run.status is IngestionStatus.FAILED
    assert execution.failures[0].code == "INGESTION_EXECUTION_ERROR"
    assert "RuntimeError" in execution.failures[0].message
    assert secret_like not in execution.failures[0].message
    assert "postgresql://" not in execution.failures[0].message


def test_workflow_is_manual_and_scheduled_with_protected_secret_only():
    workflow = Path(".github/workflows/scheduled-yahoo-ingestion.yml").read_text()

    assert "workflow_dispatch:" in workflow
    assert 'cron: "45 23 * * 1-5"' in workflow
    assert "secrets.SUPABASE_DB_URL" in workflow
    assert "python -m investment_manager.jobs.scheduled_yahoo" in workflow
    assert "postgresql://" not in workflow
    assert "SUPABASE_DB_URL:" in workflow


def test_postgres_driver_is_optional_runtime_dependency():
    pyproject = Path("pyproject.toml").read_text()

    assert "[project.optional-dependencies]" in pyproject
    assert 'psycopg[binary]>=3.2,<4' in pyproject
