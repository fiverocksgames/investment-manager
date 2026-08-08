from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from investment_manager.data import (
    FetchRequest,
    FetchResult,
    IngestionExecution,
    IngestionFailure,
    IngestionRun,
    IngestionStatus,
    IngestionStatusRepository,
    OperationalStatusError,
)


RUN_ID = UUID("00000000-0000-0000-0000-000000000063")
NOW = datetime(2026, 8, 8, 9, 0, tzinfo=UTC)


class FakeDatabase:
    def __init__(self):
        self.runs = {}
        self.failures = {}


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.result = None

    def execute(self, operation, parameters=()):
        sql = " ".join(operation.split()).lower()
        if sql.startswith("insert into ingestion_runs"):
            key = parameters[0]
            if key in self.db.runs:
                self.result = None
            else:
                self.db.runs[key] = tuple(parameters[1:])
                self.result = (key,)
        elif sql.startswith("select provider, dataset"):
            self.result = self.db.runs.get(parameters[0])
        elif sql.startswith("insert into ingestion_failures"):
            key = (parameters[0], parameters[1])
            if key in self.db.failures:
                self.result = None
            else:
                self.db.failures[key] = tuple(parameters[2:])
                self.result = (parameters[0],)
        elif sql.startswith("select code, message"):
            self.result = self.db.failures.get((parameters[0], parameters[1]))
        elif sql.startswith("select count(*) from ingestion_failures"):
            self.result = (sum(1 for run_id, _ in self.db.failures if run_id == parameters[0]),)
        else:
            raise AssertionError(f"unexpected sql: {sql}")

    def fetchone(self):
        return self.result

    def close(self):
        pass


class FakeConnection:
    def __init__(self, db):
        self.db = db
        self.backup = None
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        self.backup = (dict(self.db.runs), dict(self.db.failures))
        return FakeCursor(self.db)

    def commit(self):
        self.commits += 1
        self.backup = None

    def rollback(self):
        self.rollbacks += 1
        if self.backup is not None:
            self.db.runs, self.db.failures = self.backup

    def close(self):
        pass


def execution(*, message="rate limited", provider_attempts=3):
    failure = IngestionFailure(
        run_id=RUN_ID,
        code="HTTP_429",
        message=message,
        retryable=True,
        occurred_at=NOW,
        provider_reference="SPY",
    )
    return IngestionExecution(
        run=IngestionRun(
            run_id=RUN_ID,
            provider="yahoo",
            dataset="market_prices",
            started_at=NOW,
            ended_at=NOW,
            status=IngestionStatus.FAILED,
            attempt=provider_attempts,
            records_received=0,
            records_accepted=0,
        ),
        failures=(failure,),
        provider_attempts=provider_attempts,
    )


def repository():
    db = FakeDatabase()
    connections = []

    def factory():
        connection = FakeConnection(db)
        connections.append(connection)
        return connection

    return IngestionStatusRepository(factory), db, connections


def test_persists_terminal_run_and_ordered_failures():
    repo, db, connections = repository()
    result = repo.persist(execution())

    assert result.created_run is True
    assert result.inserted_failures == 1
    assert len(db.runs) == 1
    assert len(db.failures) == 1
    assert connections[-1].commits == 1


def test_identical_replay_is_idempotent():
    repo, db, _ = repository()
    first = repo.persist(execution())
    second = repo.persist(execution())

    assert first.created_run is True
    assert second.created_run is False
    assert second.inserted_failures == 0
    assert len(db.runs) == 1
    assert len(db.failures) == 1


def test_conflicting_run_identity_fails_closed_and_rolls_back():
    repo, db, connections = repository()
    repo.persist(execution())
    stored = list(db.runs[str(RUN_ID)])
    stored[0] = "fred"
    db.runs[str(RUN_ID)] = tuple(stored)

    try:
        repo.persist(execution())
    except OperationalStatusError as exc:
        assert "conflicting immutable" in str(exc)
    else:
        raise AssertionError("conflicting run must fail")

    assert connections[-1].rollbacks == 1
    assert db.runs[str(RUN_ID)][0] == "fred"


def test_non_terminal_run_is_rejected_before_connecting():
    repo, _, connections = repository()
    pending = IngestionExecution(
        run=IngestionRun(
            run_id=RUN_ID,
            provider="yahoo",
            dataset="market_prices",
            started_at=NOW,
            status=IngestionStatus.RUNNING,
        ),
        failures=(),
    )

    try:
        repo.persist(pending)
    except OperationalStatusError as exc:
        assert "terminal" in str(exc)
    else:
        raise AssertionError("non-terminal run must fail")

    assert connections == []
