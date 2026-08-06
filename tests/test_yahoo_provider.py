"""Deterministic tests for the Yahoo market-data adapter."""

from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime
from decimal import Decimal
from urllib.error import HTTPError
from uuid import UUID

from investment_manager.data.models import ObservationKind
from investment_manager.data.providers import FetchRequest, ProviderCapability
from investment_manager.data.yahoo import YahooProvider, YahooSymbolBinding

NOW = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
START = datetime(2026, 8, 3, 0, 0, tzinfo=UTC)
END = datetime(2026, 8, 6, 23, 59, tzinfo=UTC)
SPY_ID = UUID("9099d56f-5795-5778-bae0-b5425562d614")
FX_ID = UUID("a15d7850-46f2-5a0b-9f94-bdc22a5b2dc1")


def payload(*, missing_second: bool = False) -> bytes:
    second_close = None if missing_second else 632.1
    second_adjclose = None if missing_second else 631.8
    body = {
        "chart": {
            "result": [
                {
                    "meta": {
                        "currency": "USD",
                        "symbol": "SPY",
                        "exchangeTimezoneName": "America/New_York",
                    },
                    "timestamp": [1754265600, 1754352000],
                    "indicators": {
                        "quote": [
                            {
                                "open": [628.1, 630.2],
                                "high": [631.5, 633.4],
                                "low": [627.8, 629.7],
                                "close": [630.8, second_close],
                                "volume": [61234567, 58765432],
                            }
                        ],
                        "adjclose": [{"adjclose": [630.5, second_adjclose]}],
                    },
                }
            ],
            "error": None,
        }
    }
    return json.dumps(body).encode("utf-8")


class YahooProviderTests(unittest.TestCase):
    def provider(self, transport) -> YahooProvider:
        return YahooProvider(
            bindings={
                "SPY": YahooSymbolBinding(symbol="SPY", subject_id=SPY_ID, unit="USD"),
                "KRW=X": YahooSymbolBinding(
                    symbol="KRW=X",
                    subject_id=FX_ID,
                    unit="KRW",
                    kind=ObservationKind.FX_RATE,
                ),
            },
            transport=transport,
            clock=lambda: NOW,
        )

    def request(self, *symbols: str, dataset: str = ProviderCapability.MARKET_PRICES.value) -> FetchRequest:
        return FetchRequest(dataset=dataset, source_identifiers=symbols, start_at=START, end_at=END)

    def test_parses_daily_adjusted_close_and_preserves_ohlcv_metadata(self) -> None:
        captured: dict[str, object] = {}

        def transport(url: str, timeout: float) -> bytes:
            captured["url"] = url
            captured["timeout"] = timeout
            return payload()

        result = self.provider(transport).fetch(self.request("SPY"))

        self.assertTrue(result.succeeded)
        self.assertEqual(len(result.observations), 2)
        first = result.observations[0]
        self.assertEqual(first.value, Decimal("630.5"))
        self.assertEqual(first.unit, "USD")
        self.assertEqual(first.source.attributes["open"], "628.1")
        self.assertEqual(first.source.attributes["high"], "631.5")
        self.assertEqual(first.source.attributes["low"], "627.8")
        self.assertEqual(first.source.attributes["close"], "630.8")
        self.assertEqual(first.source.attributes["adjusted_close"], "630.5")
        self.assertEqual(first.source.attributes["volume"], "61234567")
        self.assertIn("interval=1d", str(captured["url"]))
        self.assertIn("includeAdjustedClose=true", str(captured["url"]))

    def test_missing_row_becomes_failure_without_trusted_observation(self) -> None:
        result = self.provider(lambda _url, _timeout: payload(missing_second=True)).fetch(self.request("SPY"))

        self.assertTrue(result.partial)
        self.assertEqual(len(result.observations), 1)
        self.assertEqual({failure.code for failure in result.failures}, {"MISSING_VALUE"})

    def test_unknown_binding_and_success_produce_partial_result(self) -> None:
        result = self.provider(lambda _url, _timeout: payload()).fetch(self.request("SPY", "UNKNOWN"))

        self.assertTrue(result.partial)
        self.assertEqual(len(result.observations), 2)
        self.assertEqual({failure.code for failure in result.failures}, {"UNKNOWN_BINDING"})

    def test_http_failure_is_explicit_and_retryable_for_server_error(self) -> None:
        def transport(_url: str, _timeout: float) -> bytes:
            raise HTTPError("https://example.invalid", 503, "unavailable", {}, None)

        result = self.provider(transport).fetch(self.request("SPY"))

        self.assertFalse(result.succeeded)
        self.assertEqual(result.failures[0].code, "HTTP_503")
        self.assertTrue(result.failures[0].retryable)

    def test_binding_kind_must_match_requested_dataset(self) -> None:
        result = self.provider(lambda _url, _timeout: payload()).fetch(
            self.request("KRW=X", dataset=ProviderCapability.MARKET_PRICES.value)
        )

        self.assertEqual(result.failures[0].code, "BINDING_KIND_MISMATCH")

    def test_fx_binding_uses_fx_observation_kind(self) -> None:
        fx_body = json.loads(payload().decode("utf-8"))
        fx_body["chart"]["result"][0]["meta"]["currency"] = "KRW"
        result = self.provider(lambda _url, _timeout: json.dumps(fx_body).encode("utf-8")).fetch(
            self.request("KRW=X", dataset=ProviderCapability.FX_RATES.value)
        )

        self.assertEqual(result.observations[0].kind, ObservationKind.FX_RATE)
        self.assertEqual(result.observations[0].unit, "KRW")

    def test_malformed_payload_is_invalid_payload_failure(self) -> None:
        result = self.provider(lambda _url, _timeout: b'{"chart": {"result": []}}').fetch(self.request("SPY"))

        self.assertEqual(result.failures[0].code, "INVALID_PAYLOAD")
        self.assertFalse(result.failures[0].retryable)


if __name__ == "__main__":
    unittest.main()
