"""Deterministic tests for provider-independent FX normalization."""

from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from investment_manager.data.fx import FxNormalizationBinding, FxNormalizationError, FxNormalizer, FxPair
from investment_manager.data.models import (
    DataQualityState,
    FreshnessState,
    Observation,
    ObservationKind,
    ProviderMetadata,
)
from investment_manager.data.providers import FetchRequest, ProviderCapability
from investment_manager.data.yahoo import YahooProvider, YahooSymbolBinding

PAIR_ID = UUID("a15d7850-46f2-5a0b-9f94-bdc22a5b2dc1")
OTHER_PAIR_ID = UUID("b360769e-35ea-5a82-88f5-e8fd556def62")
OBSERVED_AT = datetime(2025, 8, 4, 0, 0, tzinfo=UTC)
RETRIEVED_AT = datetime(2026, 8, 7, 12, 0, tzinfo=UTC)


def yahoo_fx_payload() -> bytes:
    body = {
        "chart": {
            "result": [
                {
                    "meta": {
                        "currency": "KRW",
                        "symbol": "KRW=X",
                        "exchangeTimezoneName": "Europe/London",
                    },
                    "timestamp": [1754265600],
                    "indicators": {
                        "quote": [
                            {
                                "open": [1380.0],
                                "high": [1390.0],
                                "low": [1375.0],
                                "close": [1385.0],
                                "volume": [0],
                            }
                        ],
                        "adjclose": [{"adjclose": [1385.25]}],
                    },
                }
            ],
            "error": None,
        }
    }
    return json.dumps(body).encode("utf-8")


def source_observation(
    *,
    value: Decimal,
    kind: ObservationKind = ObservationKind.FX_RATE,
    subject_id: UUID = PAIR_ID,
    unit: str = "USD",
) -> Observation:
    return Observation(
        observation_id=uuid4(),
        kind=kind,
        subject_id=subject_id,
        observed_at=OBSERVED_AT,
        value=value,
        unit=unit,
        quality=DataQualityState.VALID,
        freshness=FreshnessState.UNKNOWN,
        source=ProviderMetadata(
            provider="fixture",
            source_identifier="fixture-rate",
            retrieved_at=RETRIEVED_AT,
            revision="r1",
            attributes={"fixture": "preserved"},
        ),
    )


class FxPairTests(unittest.TestCase):
    def test_pair_normalizes_currency_codes_and_exposes_directional_unit(self) -> None:
        pair = FxPair(pair_id=PAIR_ID, base_currency="usd", quote_currency="krw")
        self.assertEqual(pair.base_currency, "USD")
        self.assertEqual(pair.quote_currency, "KRW")
        self.assertEqual(pair.unit, "KRW_per_USD")

    def test_pair_rejects_identical_or_invalid_currency_codes(self) -> None:
        with self.assertRaises(ValueError):
            FxPair(pair_id=PAIR_ID, base_currency="USD", quote_currency="USD")
        with self.assertRaises(ValueError):
            FxPair(pair_id=PAIR_ID, base_currency="US", quote_currency="KRW")


class FxNormalizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pair = FxPair(pair_id=PAIR_ID, base_currency="USD", quote_currency="KRW")
        self.normalizer = FxNormalizer()

    def test_yahoo_krw_fixture_normalizes_as_krw_per_usd_without_guessing(self) -> None:
        provider = YahooProvider(
            bindings={
                "KRW=X": YahooSymbolBinding(
                    symbol="KRW=X",
                    subject_id=PAIR_ID,
                    unit="KRW",
                    kind=ObservationKind.FX_RATE,
                )
            },
            transport=lambda _url, _timeout: yahoo_fx_payload(),
            clock=lambda: RETRIEVED_AT,
        )
        result = provider.fetch(
            FetchRequest(
                dataset=ProviderCapability.FX_RATES.value,
                source_identifiers=("KRW=X",),
                start_at=datetime(2025, 8, 3, tzinfo=UTC),
                end_at=datetime(2025, 8, 6, 23, 59, tzinfo=UTC),
            )
        )
        self.assertTrue(result.succeeded)

        normalized = self.normalizer.normalize(
            result.observations[0],
            FxNormalizationBinding(
                pair=self.pair,
                source_base_currency="USD",
                source_quote_currency="KRW",
            ),
        )

        self.assertEqual(normalized.value, Decimal("1385.25"))
        self.assertEqual(normalized.unit, "KRW_per_USD")
        self.assertEqual(normalized.subject_id, PAIR_ID)
        self.assertEqual(normalized.source.provider, "yahoo")
        self.assertEqual(normalized.source.source_identifier, "KRW=X")
        self.assertEqual(normalized.source.attributes["canonical_fx_base_currency"], "USD")
        self.assertEqual(normalized.source.attributes["canonical_fx_quote_currency"], "KRW")
        self.assertEqual(normalized.source.attributes["source_fx_base_currency"], "USD")
        self.assertEqual(normalized.source.attributes["source_fx_quote_currency"], "KRW")
        self.assertEqual(normalized.source.attributes["fx_normalization"], "identity")
        self.assertEqual(normalized.source.attributes["source_rate_unit"], "KRW")
        self.assertEqual(normalized.source.attributes["adjusted_close"], "1385.25")

    def test_inverse_source_direction_uses_decimal_reciprocal(self) -> None:
        normalized = self.normalizer.normalize(
            source_observation(value=Decimal("0.25")),
            FxNormalizationBinding(
                pair=self.pair,
                source_base_currency="KRW",
                source_quote_currency="USD",
            ),
        )
        self.assertEqual(normalized.value, Decimal("4"))
        self.assertEqual(normalized.unit, "KRW_per_USD")
        self.assertEqual(normalized.source.attributes["fx_normalization"], "reciprocal")

    def test_normalization_identifier_is_deterministic_for_same_source_identity(self) -> None:
        observation = source_observation(value=Decimal("1400"))
        binding = FxNormalizationBinding(pair=self.pair, source_base_currency="USD", source_quote_currency="KRW")
        first = self.normalizer.normalize(observation, binding)
        second = self.normalizer.normalize(observation, binding)
        self.assertEqual(first.observation_id, second.observation_id)

    def test_zero_and_negative_rates_are_rejected_explicitly(self) -> None:
        binding = FxNormalizationBinding(pair=self.pair, source_base_currency="USD", source_quote_currency="KRW")
        for value in (Decimal("0"), Decimal("-1")):
            with self.subTest(value=value):
                with self.assertRaises(FxNormalizationError) as raised:
                    self.normalizer.normalize(source_observation(value=value), binding)
                self.assertEqual(raised.exception.code, "INVALID_RATE")

    def test_non_fx_observation_is_rejected_explicitly(self) -> None:
        binding = FxNormalizationBinding(pair=self.pair, source_base_currency="USD", source_quote_currency="KRW")
        with self.assertRaises(FxNormalizationError) as raised:
            self.normalizer.normalize(
                source_observation(value=Decimal("1400"), kind=ObservationKind.MARKET_PRICE),
                binding,
            )
        self.assertEqual(raised.exception.code, "NON_FX_OBSERVATION")

    def test_subject_mismatch_is_rejected_explicitly(self) -> None:
        binding = FxNormalizationBinding(pair=self.pair, source_base_currency="USD", source_quote_currency="KRW")
        with self.assertRaises(FxNormalizationError) as raised:
            self.normalizer.normalize(
                source_observation(value=Decimal("1400"), subject_id=OTHER_PAIR_ID),
                binding,
            )
        self.assertEqual(raised.exception.code, "SUBJECT_MISMATCH")

    def test_unrelated_source_currencies_are_rejected_at_binding_time(self) -> None:
        with self.assertRaises(ValueError):
            FxNormalizationBinding(
                pair=self.pair,
                source_base_currency="EUR",
                source_quote_currency="KRW",
            )

    def test_source_provenance_and_quality_are_preserved(self) -> None:
        source = source_observation(value=Decimal("1400"))
        normalized = self.normalizer.normalize(
            source,
            FxNormalizationBinding(pair=self.pair, source_base_currency="USD", source_quote_currency="KRW"),
        )
        self.assertEqual(normalized.observed_at, source.observed_at)
        self.assertEqual(normalized.quality, source.quality)
        self.assertEqual(normalized.freshness, source.freshness)
        self.assertEqual(normalized.source.retrieved_at, source.source.retrieved_at)
        self.assertEqual(normalized.source.revision, "r1")
        self.assertEqual(normalized.source.attributes["fixture"], "preserved")


if __name__ == "__main__":
    unittest.main()
