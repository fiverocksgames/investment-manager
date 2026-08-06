from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import MappingProxyType
from unittest import TestCase
from uuid import uuid4

from investment_manager.data.models import (
    Asset,
    AssetClass,
    DataQualityState,
    DatasetPolicy,
    FreshnessState,
    Observation,
    ObservationKind,
    ProviderMetadata,
    SourceSnapshot,
)


class AssetTests(TestCase):
    def test_normalizes_symbol_currency_and_exchange(self) -> None:
        asset = Asset(uuid4(), " spy ", "SPDR S&P 500 ETF", AssetClass.ETF, "usd", "arca")
        self.assertEqual(asset.symbol, "SPY")
        self.assertEqual(asset.currency, "USD")
        self.assertEqual(asset.exchange, "ARCA")

    def test_rejects_invalid_currency(self) -> None:
        with self.assertRaises(ValueError):
            Asset(uuid4(), "SPY", "SPY", AssetClass.ETF, "US")


class ObservationTests(TestCase):
    def setUp(self) -> None:
        self.observed_at = datetime(2026, 8, 5, 20, tzinfo=UTC)
        self.source = ProviderMetadata(
            provider="Yahoo",
            source_identifier="SPY",
            retrieved_at=self.observed_at + timedelta(minutes=5),
            attributes={"timezone": "America/New_York"},
        )

    def test_requires_decimal_and_freezes_metadata(self) -> None:
        observation = Observation(
            uuid4(),
            ObservationKind.MARKET_PRICE,
            uuid4(),
            self.observed_at,
            Decimal("632.15"),
            "USD",
            DataQualityState.VALID,
            FreshnessState.FRESH,
            self.source,
        )
        self.assertEqual(observation.value, Decimal("632.15"))
        self.assertIsInstance(observation.source.attributes, MappingProxyType)
        with self.assertRaises(TypeError):
            observation.source.attributes["timezone"] = "UTC"  # type: ignore[index]

    def test_rejects_binary_float(self) -> None:
        with self.assertRaises(TypeError):
            Observation(
                uuid4(),
                ObservationKind.MARKET_PRICE,
                uuid4(),
                self.observed_at,
                632.15,  # type: ignore[arg-type]
                "USD",
                DataQualityState.VALID,
                FreshnessState.FRESH,
                self.source,
            )

    def test_rejects_naive_datetime(self) -> None:
        with self.assertRaises(ValueError):
            ProviderMetadata("yahoo", "SPY", datetime(2026, 8, 5, 20))

    def test_rejects_invalid_quality_as_observation(self) -> None:
        with self.assertRaises(ValueError):
            Observation(
                uuid4(),
                ObservationKind.MARKET_PRICE,
                uuid4(),
                self.observed_at,
                Decimal("0"),
                "USD",
                DataQualityState.INVALID,
                FreshnessState.UNKNOWN,
                self.source,
            )


class DatasetPolicyTests(TestCase):
    def test_classifies_freshness(self) -> None:
        policy = DatasetPolicy(
            "daily_prices",
            expected_cadence=timedelta(days=1),
            aging_after=timedelta(hours=30),
            stale_after=timedelta(hours=48),
            cache_ttl=timedelta(hours=6),
        )
        observed = datetime(2026, 8, 5, tzinfo=UTC)
        self.assertEqual(policy.freshness_at(observed, observed + timedelta(hours=12)), FreshnessState.FRESH)
        self.assertEqual(policy.freshness_at(observed, observed + timedelta(hours=36)), FreshnessState.AGING)
        self.assertEqual(policy.freshness_at(observed, observed + timedelta(hours=72)), FreshnessState.STALE)

    def test_rejects_inverted_thresholds(self) -> None:
        with self.assertRaises(ValueError):
            DatasetPolicy(
                "daily_prices",
                timedelta(days=1),
                timedelta(days=3),
                timedelta(days=2),
                timedelta(hours=6),
            )


class SourceSnapshotTests(TestCase):
    def test_rejects_duplicate_observations(self) -> None:
        observation_id = uuid4()
        with self.assertRaises(ValueError):
            SourceSnapshot(
                uuid4(),
                "daily_prices",
                "yahoo",
                datetime(2026, 8, 5, tzinfo=UTC),
                datetime(2026, 8, 5, 1, tzinfo=UTC),
                (observation_id, observation_id),
                "abc123",
            )
