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
from tools.yahoo_smoke import validate_result


class YahooSmokeValidationTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 7, 0, 0, tzinfo=UTC)
        self.request = FetchRequest(
            dataset=ProviderCapability.MARKET_PRICES.value,
            source_identifiers=("SPY",),
            start_at=datetime(2026, 7, 24, tzinfo=UTC),
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
                provider="yahoo",
                source_identifier="SPY",
                retrieved_at=self.now,
                attributes={"interval": "1d", "currency": "USD"},
            ),
        )

    def failure(self, code: str, *, retryable: bool = False) -> IngestionFailure:
        return IngestionFailure(
            run_id=uuid4(),
            code=code,
            message="safe failure",
            retryable=retryable,
            occurred_at=self.now,
        )

    def test_accepts_observations_with_expected_row_warnings(self) -> None:
        result = FetchResult(
            provider="yahoo",
            request=self.request,
            observations=(self.observation,),
            failures=(self.failure("MISSING_VALUE"), self.failure("OUT_OF_RANGE")),
        )

        valid, codes = validate_result(result)

        self.assertTrue(valid)
        self.assertEqual(codes, ("MISSING_VALUE", "OUT_OF_RANGE"))

    def test_rejects_rate_limit_even_with_observations(self) -> None:
        result = FetchResult(
            provider="yahoo",
            request=self.request,
            observations=(self.observation,),
            failures=(self.failure("HTTP_429", retryable=True),),
        )

        valid, codes = validate_result(result)

        self.assertFalse(valid)
        self.assertEqual(codes, ("HTTP_429",))

    def test_rejects_schema_or_payload_failure(self) -> None:
        result = FetchResult(
            provider="yahoo",
            request=self.request,
            failures=(self.failure("INVALID_PAYLOAD"),),
        )

        valid, codes = validate_result(result)

        self.assertFalse(valid)
        self.assertEqual(codes, ("INVALID_PAYLOAD",))

    def test_rejects_no_observations_with_only_tolerated_warning(self) -> None:
        result = FetchResult(
            provider="yahoo",
            request=self.request,
            failures=(self.failure("MISSING_VALUE"),),
        )

        valid, codes = validate_result(result)

        self.assertFalse(valid)
        self.assertEqual(codes, ("MISSING_VALUE",))
