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
from tools.fred_smoke import validate_result


class FredSmokeValidationTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 6, 6, 0, tzinfo=UTC)
        self.request = FetchRequest(
            dataset=ProviderCapability.ECONOMIC_SERIES.value,
            source_identifiers=("DGS10",),
            start_at=datetime(2026, 7, 1, tzinfo=UTC),
            end_at=self.now,
        )
        self.observation = Observation(
            observation_id=uuid4(),
            kind=ObservationKind.ECONOMIC,
            subject_id=UUID("f612b89b-8db7-5c20-9115-2af66f0fdc77"),
            observed_at=datetime(2026, 8, 5, tzinfo=UTC),
            value=Decimal("4.21"),
            unit="percent",
            quality=DataQualityState.VALID,
            freshness=FreshnessState.UNKNOWN,
            source=ProviderMetadata(
                provider="fred",
                source_identifier="DGS10",
                retrieved_at=self.now,
            ),
        )

    def failure(self, code: str) -> IngestionFailure:
        return IngestionFailure(
            run_id=uuid4(),
            code=code,
            message="safe failure",
            retryable=False,
            occurred_at=self.now,
        )

    def test_accepts_valid_observations_with_expected_warnings(self) -> None:
        result = FetchResult(
            provider="fred",
            request=self.request,
            observations=(self.observation,),
            failures=(self.failure("MISSING_VALUE"), self.failure("OUT_OF_RANGE")),
        )

        valid, codes = validate_result(result)

        self.assertTrue(valid)
        self.assertEqual(codes, ("MISSING_VALUE", "OUT_OF_RANGE"))

    def test_rejects_fatal_provider_failure_even_with_observations(self) -> None:
        result = FetchResult(
            provider="fred",
            request=self.request,
            observations=(self.observation,),
            failures=(self.failure("HTTP_500"),),
        )

        valid, codes = validate_result(result)

        self.assertFalse(valid)
        self.assertEqual(codes, ("HTTP_500",))

    def test_rejects_empty_result_with_tolerated_warning(self) -> None:
        result = FetchResult(
            provider="fred",
            request=self.request,
            failures=(self.failure("MISSING_VALUE"),),
        )

        valid, codes = validate_result(result)

        self.assertFalse(valid)
        self.assertEqual(codes, ("MISSING_VALUE",))
