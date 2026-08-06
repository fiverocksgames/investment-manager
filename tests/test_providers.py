from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from investment_manager.data.models import (
    DataQualityState,
    FreshnessState,
    IngestionFailure,
    Observation,
    ObservationKind,
    ProviderMetadata,
)
from investment_manager.data.providers import FetchRequest, FetchResult


class FetchRequestTests(TestCase):
    def test_normalizes_time_and_identifiers(self) -> None:
        request = FetchRequest(
            " Daily_Prices ",
            ("SPY", "QQQ"),
            datetime(2026, 8, 1, tzinfo=UTC),
            datetime(2026, 8, 5, tzinfo=UTC),
        )
        self.assertEqual(request.dataset, "daily_prices")
        self.assertEqual(request.source_identifiers, ("SPY", "QQQ"))

    def test_rejects_duplicate_identifiers(self) -> None:
        with self.assertRaises(ValueError):
            FetchRequest(
                "daily_prices",
                ("SPY", "SPY"),
                datetime(2026, 8, 1, tzinfo=UTC),
                datetime(2026, 8, 5, tzinfo=UTC),
            )


class FetchResultTests(TestCase):
    def setUp(self) -> None:
        self.request = FetchRequest(
            "daily_prices",
            ("SPY",),
            datetime(2026, 8, 1, tzinfo=UTC),
            datetime(2026, 8, 5, tzinfo=UTC),
        )
        observed_at = datetime(2026, 8, 5, tzinfo=UTC)
        self.observation = Observation(
            uuid4(),
            ObservationKind.MARKET_PRICE,
            uuid4(),
            observed_at,
            Decimal("632.15"),
            "USD",
            DataQualityState.VALID,
            FreshnessState.FRESH,
            ProviderMetadata("yahoo", "SPY", observed_at + timedelta(minutes=1)),
        )
        self.failure = IngestionFailure(
            uuid4(),
            "RATE_LIMITED",
            "Provider rate limit reached",
            True,
            observed_at + timedelta(minutes=1),
        )

    def test_success_requires_observations_without_failures(self) -> None:
        result = FetchResult("yahoo", self.request, observations=(self.observation,))
        self.assertTrue(result.succeeded)
        self.assertFalse(result.partial)

    def test_partial_result_is_explicit(self) -> None:
        result = FetchResult(
            "yahoo",
            self.request,
            observations=(self.observation,),
            failures=(self.failure,),
        )
        self.assertFalse(result.succeeded)
        self.assertTrue(result.partial)

    def test_rejects_empty_result(self) -> None:
        with self.assertRaises(ValueError):
            FetchResult("yahoo", self.request)
