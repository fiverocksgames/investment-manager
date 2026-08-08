from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from investment_manager.data.cache import CacheExecutor
from investment_manager.data.models import (
    DataQualityState,
    DatasetPolicy,
    FreshnessState,
    IngestionFailure,
    Observation,
    ObservationKind,
    ProviderMetadata,
)
from investment_manager.data.providers import FetchRequest, FetchResult, ProviderCapability


OBSERVATION_ID = UUID("11111111-1111-1111-1111-111111111111")
SUBJECT_ID = UUID("22222222-2222-2222-2222-222222222222")
RUN_ID = UUID("33333333-3333-3333-3333-333333333333")
BASE_TIME = datetime(2026, 8, 8, 0, 0, tzinfo=UTC)


def _request(*, dataset: str = "market_prices", symbol: str = "SPY") -> FetchRequest:
    return FetchRequest(
        dataset=dataset,
        source_identifiers=(symbol,),
        start_at=BASE_TIME - timedelta(days=1),
        end_at=BASE_TIME,
    )


def _policy(*, dataset: str = "market_prices", ttl: timedelta = timedelta(minutes=10)) -> DatasetPolicy:
    return DatasetPolicy(
        dataset=dataset,
        expected_cadence=timedelta(days=1),
        aging_after=timedelta(days=2),
        stale_after=timedelta(days=3),
        cache_ttl=ttl,
    )


def _observation(provider: str = "test") -> Observation:
    return Observation(
        observation_id=OBSERVATION_ID,
        kind=ObservationKind.MARKET_PRICE,
        subject_id=SUBJECT_ID,
        observed_at=BASE_TIME - timedelta(hours=1),
        value=Decimal("123.45"),
        unit="USD",
        quality=DataQualityState.VALID,
        freshness=FreshnessState.FRESH,
        source=ProviderMetadata(
            provider=provider,
            source_identifier="SPY",
            retrieved_at=BASE_TIME,
            attributes={"interval": "1d"},
        ),
    )


def _success(request: FetchRequest, provider: str = "test") -> FetchResult:
    return FetchResult(provider=provider, request=request, observations=(_observation(provider),))


def _partial(request: FetchRequest, provider: str = "test") -> FetchResult:
    return FetchResult(
        provider=provider,
        request=request,
        observations=(_observation(provider),),
        failures=(
            IngestionFailure(
                run_id=RUN_ID,
                code="PARTIAL_SOURCE",
                message="bounded partial fixture",
                retryable=False,
                occurred_at=BASE_TIME,
            ),
        ),
    )


def _failure(request: FetchRequest, provider: str = "test") -> FetchResult:
    return FetchResult(
        provider=provider,
        request=request,
        failures=(
            IngestionFailure(
                run_id=RUN_ID,
                code="TRANSPORT_ERROR",
                message="bounded failure fixture",
                retryable=True,
                occurred_at=BASE_TIME,
            ),
        ),
    )


class StubProvider:
    capabilities = frozenset({ProviderCapability.MARKET_PRICES})

    def __init__(self, name: str, results: list[FetchResult]) -> None:
        self._name = name
        self._results = list(results)
        self.calls = 0

    @property
    def name(self) -> str:
        return self._name

    def fetch(self, request: FetchRequest) -> FetchResult:
        self.calls += 1
        if not self._results:
            raise AssertionError("unexpected provider call")
        result = self._results.pop(0)
        if result.request != request:
            raise AssertionError("provider received unexpected request")
        return result


class CacheExecutorTests(unittest.TestCase):
    def test_miss_then_hit_preserves_exact_result_and_provenance(self) -> None:
        request = _request()
        result = _success(request)
        provider = StubProvider("test", [result])
        cache = CacheExecutor()

        first = cache.execute(provider, request, _policy(), now=BASE_TIME)
        second = cache.execute(provider, request, _policy(), now=BASE_TIME + timedelta(minutes=5))

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertEqual(provider.calls, 1)
        self.assertIs(second.result, result)
        self.assertEqual(second.result.observations[0].observation_id, OBSERVATION_ID)
        self.assertEqual(second.result.observations[0].source.retrieved_at, BASE_TIME)
        self.assertEqual(second.result.observations[0].freshness, FreshnessState.FRESH)
        self.assertEqual(second.cached_at, BASE_TIME)
        self.assertEqual(second.expires_at, BASE_TIME + timedelta(minutes=10))

    def test_exact_expiry_triggers_provider_and_replaces_entry(self) -> None:
        request = _request()
        first_result = _success(request)
        second_result = FetchResult(
            provider="test",
            request=request,
            observations=(
                Observation(
                    observation_id=UUID("44444444-4444-4444-4444-444444444444"),
                    kind=ObservationKind.MARKET_PRICE,
                    subject_id=SUBJECT_ID,
                    observed_at=BASE_TIME,
                    value=Decimal("124.00"),
                    unit="USD",
                    quality=DataQualityState.VALID,
                    freshness=FreshnessState.FRESH,
                    source=ProviderMetadata(
                        provider="test",
                        source_identifier="SPY",
                        retrieved_at=BASE_TIME + timedelta(minutes=10),
                    ),
                ),
            ),
        )
        provider = StubProvider("test", [first_result, second_result])
        cache = CacheExecutor()
        policy = _policy()

        cache.execute(provider, request, policy, now=BASE_TIME)
        refreshed = cache.execute(provider, request, policy, now=BASE_TIME + timedelta(minutes=10))
        hit = cache.execute(provider, request, policy, now=BASE_TIME + timedelta(minutes=11))

        self.assertFalse(refreshed.cache_hit)
        self.assertTrue(hit.cache_hit)
        self.assertIs(hit.result, second_result)
        self.assertEqual(provider.calls, 2)

    def test_partial_result_is_not_cached(self) -> None:
        request = _request()
        provider = StubProvider("test", [_partial(request), _success(request)])
        cache = CacheExecutor()

        first = cache.execute(provider, request, _policy(), now=BASE_TIME)
        second = cache.execute(provider, request, _policy(), now=BASE_TIME + timedelta(minutes=1))

        self.assertTrue(first.result.partial)
        self.assertIsNone(first.cached_at)
        self.assertFalse(second.cache_hit)
        self.assertEqual(provider.calls, 2)

    def test_failure_is_not_cached_or_replaced_by_expired_success(self) -> None:
        request = _request()
        provider = StubProvider("test", [_success(request), _failure(request), _success(request)])
        cache = CacheExecutor()
        policy = _policy(ttl=timedelta(minutes=1))

        cache.execute(provider, request, policy, now=BASE_TIME)
        failed = cache.execute(provider, request, policy, now=BASE_TIME + timedelta(minutes=1))
        recovered = cache.execute(provider, request, policy, now=BASE_TIME + timedelta(minutes=2))

        self.assertFalse(failed.cache_hit)
        self.assertFalse(failed.result.succeeded)
        self.assertIsNone(failed.cached_at)
        self.assertFalse(recovered.cache_hit)
        self.assertTrue(recovered.result.succeeded)
        self.assertEqual(provider.calls, 3)

    def test_cache_key_isolates_requests(self) -> None:
        spy = _request(symbol="SPY")
        tlt = _request(symbol="TLT")
        provider = StubProvider("test", [_success(spy), _success(tlt)])
        cache = CacheExecutor()

        cache.execute(provider, spy, _policy(), now=BASE_TIME)
        second = cache.execute(provider, tlt, _policy(), now=BASE_TIME)

        self.assertFalse(second.cache_hit)
        self.assertEqual(provider.calls, 2)

    def test_cache_key_isolates_providers(self) -> None:
        request = _request()
        first = StubProvider("one", [_success(request, "one")])
        second = StubProvider("two", [_success(request, "two")])
        cache = CacheExecutor()

        cache.execute(first, request, _policy(), now=BASE_TIME)
        result = cache.execute(second, request, _policy(), now=BASE_TIME)

        self.assertFalse(result.cache_hit)
        self.assertEqual(first.calls, 1)
        self.assertEqual(second.calls, 1)

    def test_dataset_policy_must_match_request(self) -> None:
        request = _request()
        provider = StubProvider("test", [_success(request)])

        with self.assertRaisesRegex(ValueError, "request dataset must match"):
            CacheExecutor().execute(provider, request, _policy(dataset="fx_rates"), now=BASE_TIME)

        self.assertEqual(provider.calls, 0)

    def test_now_must_be_timezone_aware(self) -> None:
        request = _request()
        provider = StubProvider("test", [_success(request)])

        with self.assertRaisesRegex(ValueError, "now must be timezone-aware"):
            CacheExecutor().execute(provider, request, _policy(), now=datetime(2026, 8, 8))

        self.assertEqual(provider.calls, 0)

    def test_fetch_result_provider_must_match_provider_name(self) -> None:
        request = _request()
        provider = StubProvider("test", [_success(request, "other")])

        with self.assertRaisesRegex(ValueError, "fetch result provider must match"):
            CacheExecutor().execute(provider, request, _policy(), now=BASE_TIME)


if __name__ == "__main__":
    unittest.main()
