from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse
from uuid import UUID

from investment_manager.data.fred import FredProvider, FredSeriesBinding
from investment_manager.data.providers import DataProvider, FetchRequest


API_KEY = "a" * 32
NOW = datetime(2026, 8, 6, 3, 30, tzinfo=UTC)
SUBJECT_ID = UUID("11111111-1111-1111-1111-111111111111")


class FakeTransport:
    def __init__(self, payload: object | None = None, error: Exception | None = None) -> None:
        self.payload = payload
        self.error = error
        self.calls: list[tuple[str, float]] = []

    def __call__(self, url: str, timeout: float) -> bytes:
        self.calls.append((url, timeout))
        if self.error is not None:
            raise self.error
        return json.dumps(self.payload).encode("utf-8")


def request(*identifiers: str) -> FetchRequest:
    return FetchRequest(
        dataset="economic_series",
        source_identifiers=identifiers,
        start_at=datetime(2026, 1, 1, tzinfo=UTC),
        end_at=datetime(2026, 12, 31, 23, 59, tzinfo=UTC),
    )


def provider(transport: FakeTransport, bindings: dict[str, FredSeriesBinding] | None = None) -> FredProvider:
    return FredProvider(
        api_key=API_KEY,
        bindings=bindings or {"DGS10": FredSeriesBinding("DGS10", SUBJECT_ID, "percent")},
        transport=transport,
        clock=lambda: NOW,
        timeout=4.0,
    )


class FredProviderTests(unittest.TestCase):
    def test_implements_provider_protocol_and_builds_official_request(self) -> None:
        transport = FakeTransport({"observations": [{"date": "2026-01-02", "value": "4.25", "realtime_start": "2026-01-03", "realtime_end": "2026-01-03"}]})
        adapter = provider(transport)

        result = adapter.fetch(request("DGS10"))

        self.assertIsInstance(adapter, DataProvider)
        self.assertTrue(result.succeeded)
        self.assertEqual(result.observations[0].value.as_tuple().exponent, -2)
        parsed = urlparse(transport.calls[0][0])
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.path, "/fred/series/observations")
        self.assertEqual(query["series_id"], ["DGS10"])
        self.assertEqual(query["api_key"], [API_KEY])
        self.assertEqual(query["file_type"], ["json"])
        self.assertEqual(query["observation_start"], ["2026-01-01"])
        self.assertEqual(query["observation_end"], ["2026-12-31"])
        self.assertEqual(query["sort_order"], ["asc"])
        self.assertEqual(transport.calls[0][1], 4.0)

    def test_missing_value_produces_failure_not_observation(self) -> None:
        transport = FakeTransport({"observations": [{"date": "2026-01-02", "value": ".", "realtime_start": "2026-01-03", "realtime_end": "2026-01-03"}]})

        result = provider(transport).fetch(request("DGS10"))

        self.assertFalse(result.succeeded)
        self.assertEqual(result.observations, ())
        self.assertEqual(result.failures[0].code, "MISSING_VALUE")
        self.assertFalse(result.failures[0].retryable)

    def test_mixed_series_is_explicit_partial_result(self) -> None:
        transport = FakeTransport({"observations": [{"date": "2026-01-02", "value": "4.25", "realtime_start": "2026-01-03", "realtime_end": "2026-01-03"}]})

        result = provider(transport).fetch(request("DGS10", "UNKNOWN"))

        self.assertTrue(result.partial)
        self.assertEqual(len(result.observations), 1)
        self.assertEqual(result.failures[0].code, "UNKNOWN_BINDING")
        self.assertEqual(len(transport.calls), 1)

    def test_invalid_payload_is_classified(self) -> None:
        result = provider(FakeTransport({"not_observations": []})).fetch(request("DGS10"))

        self.assertEqual(result.failures[0].code, "INVALID_PAYLOAD")
        self.assertFalse(result.failures[0].retryable)

    def test_retryable_http_error_is_classified_without_key_exposure(self) -> None:
        error = HTTPError("https://example.invalid", 503, "down", {}, None)
        result = provider(FakeTransport(error=error)).fetch(request("DGS10"))

        self.assertEqual(result.failures[0].code, "HTTP_503")
        self.assertTrue(result.failures[0].retryable)
        self.assertNotIn(API_KEY, result.failures[0].message)
        self.assertNotIn(API_KEY, result.failures[0].provider_reference or "")

    def test_bad_api_key_and_binding_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FredProvider(api_key="bad", bindings={"DGS10": FredSeriesBinding("DGS10", SUBJECT_ID, "percent")})
        with self.assertRaises(ValueError):
            FredProvider(api_key=API_KEY, bindings={"WRONG": FredSeriesBinding("DGS10", SUBJECT_ID, "percent")})

    def test_unsupported_dataset_is_failure_without_network_call(self) -> None:
        transport = FakeTransport({"observations": []})
        result = provider(transport).fetch(
            FetchRequest(
                dataset="market_prices",
                source_identifiers=("DGS10",),
                start_at=datetime(2026, 1, 1, tzinfo=UTC),
                end_at=datetime(2026, 1, 2, tzinfo=UTC),
            )
        )

        self.assertEqual(result.failures[0].code, "UNSUPPORTED_DATASET")
        self.assertEqual(transport.calls, [])


if __name__ == "__main__":
    unittest.main()
