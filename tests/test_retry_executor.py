from datetime import UTC, datetime
from decimal import Decimal
from unittest import TestCase
from uuid import UUID, uuid4

from investment_manager.data.models import (
    DataQualityState,
    FreshnessState,
    IngestionFailure,
    Observation,
    ObservationKind,
    ProviderMetadata,
)
from investment_manager.data.providers import FetchRequest, FetchResult, ProviderCapability
from investment_manager.data.retry import BoundedRetryExecutor, RetryPolicy


class StubProvider:
    name = "stub"
    capabilities = frozenset({ProviderCapability.MARKET_PRICES})

    def __init__(self, results: list[FetchResult]) -> None:
        self._results = results
        self.calls = 0

    def fetch(self, request: FetchRequest) -> FetchResult:
        result = self._results[min(self.calls, len(self._results) - 1)]
        self.calls += 1
        return result


class BoundedRetryExecutorTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 7, 3, 0, tzinfo=UTC)
        self.request = FetchRequest(
            dataset=ProviderCapability.MARKET_PRICES.value,
            source_identifiers=("SPY",),
            start_at=datetime(2026, 8, 1, tzinfo=UTC),
            end_at=self.now,
        )
        self.observation = Observation(
            observation_id=uuid4(),
            kind=ObservationKind.MARKET_PRICE,
            subject_id=UUID("8e41c5ad-5d7f-5d35-a43a-f54a3028a06f"),
            observed_at=datetime(2026, 8, 6, tzinfo=UTC),
            value=Decimal("632.14"),
            unit="USD",
            quality=DataQualityState.VALID,
            freshness=FreshnessState.UNKNOWN,
            source=ProviderMetadata(
                provider="stub",
                source_identifier="SPY",
                retrieved_at=self.now,
            ),
        )

    def failure(self, code: str, *, retryable: bool) -> IngestionFailure:
        return IngestionFailure(
            run_id=uuid4(),
            code=code,
            message="safe failure",
            retryable=retryable,
            occurred_at=self.now,
        )

    def result_failure(self, code: str, *, retryable: bool) -> FetchResult:
        return FetchResult(
            provider="stub",
            request=self.request,
            failures=(self.failure(code, retryable=retryable),),
        )

    def test_retries_retryable_failure_then_returns_success(self) -> None:
        provider = StubProvider(
            [
                self.result_failure("HTTP_429", retryable=True),
                FetchResult(provider="stub", request=self.request, observations=(self.observation,)),
            ]
        )
        slept: list[float] = []
        executor = BoundedRetryExecutor(
            policy=RetryPolicy(max_attempts=3, base_delay_seconds=2, max_delay_seconds=10, jitter_seconds=2),
            sleeper=slept.append,
            random_value=lambda: 0.5,
        )

        execution = executor.execute(provider, self.request)

        self.assertEqual(provider.calls, 2)
        self.assertEqual(execution.attempts, 2)
        self.assertEqual(execution.delays, (3.0,))
        self.assertTrue(execution.result.succeeded)
        self.assertFalse(execution.exhausted)

    def test_exhausts_retryable_failure_at_bound(self) -> None:
        provider = StubProvider([self.result_failure("HTTP_429", retryable=True)])
        slept: list[float] = []
        executor = BoundedRetryExecutor(
            policy=RetryPolicy(max_attempts=3, base_delay_seconds=2, max_delay_seconds=5, jitter_seconds=1),
            sleeper=slept.append,
            random_value=lambda: 1.0,
        )

        execution = executor.execute(provider, self.request)

        self.assertEqual(provider.calls, 3)
        self.assertEqual(execution.attempts, 3)
        self.assertEqual(execution.delays, (3.0, 5.0))
        self.assertTrue(execution.exhausted)
        self.assertEqual(execution.result.failures[0].code, "HTTP_429")

    def test_non_retryable_failure_stops_immediately(self) -> None:
        provider = StubProvider([self.result_failure("INVALID_PAYLOAD", retryable=False)])
        slept: list[float] = []
        executor = BoundedRetryExecutor(sleeper=slept.append)

        execution = executor.execute(provider, self.request)

        self.assertEqual(provider.calls, 1)
        self.assertEqual(execution.attempts, 1)
        self.assertEqual(execution.delays, ())
        self.assertFalse(execution.exhausted)

    def test_partial_result_is_not_retried(self) -> None:
        provider = StubProvider(
            [
                FetchResult(
                    provider="stub",
                    request=self.request,
                    observations=(self.observation,),
                    failures=(self.failure("HTTP_429", retryable=True),),
                )
            ]
        )
        slept: list[float] = []
        executor = BoundedRetryExecutor(sleeper=slept.append)

        execution = executor.execute(provider, self.request)

        self.assertEqual(provider.calls, 1)
        self.assertEqual(execution.attempts, 1)
        self.assertEqual(execution.delays, ())
        self.assertTrue(execution.result.partial)

    def test_success_is_not_retried(self) -> None:
        provider = StubProvider(
            [FetchResult(provider="stub", request=self.request, observations=(self.observation,))]
        )
        slept: list[float] = []
        executor = BoundedRetryExecutor(sleeper=slept.append)

        execution = executor.execute(provider, self.request)

        self.assertEqual(provider.calls, 1)
        self.assertEqual(execution.attempts, 1)
        self.assertEqual(execution.delays, ())
        self.assertTrue(execution.result.succeeded)

    def test_policy_rejects_invalid_bounds(self) -> None:
        with self.assertRaises(ValueError):
            RetryPolicy(max_attempts=0)
        with self.assertRaises(ValueError):
            RetryPolicy(base_delay_seconds=-1)
        with self.assertRaises(ValueError):
            RetryPolicy(base_delay_seconds=5, max_delay_seconds=4)
        with self.assertRaises(ValueError):
            RetryPolicy(jitter_seconds=-1)
