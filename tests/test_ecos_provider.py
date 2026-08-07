"""Deterministic tests for the ECOS economic-series adapter."""

from __future__ import annotations

import json
import socket
import ssl
import unittest
from datetime import UTC, datetime
from decimal import Decimal
from urllib.error import HTTPError, URLError
from uuid import UUID

from investment_manager.data.ecos import EcosProvider, EcosSeriesBinding
from investment_manager.data.providers import FetchRequest, ProviderCapability

NOW = datetime(2026, 8, 7, 12, 0, tzinfo=UTC)
START = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
END = datetime(2026, 8, 7, 23, 59, tzinfo=UTC)
SUBJECT_ID = UUID("b1f2d21e-7964-59bf-b9de-a4305a086475")
IDENTIFIER = "bok_base_rate_daily"


def payload(*, second_value: object = "2.50", second_time: str = "20260514") -> bytes:
    body = {
        "StatisticSearch": {
            "list_total_count": 2,
            "row": [
                {
                    "STAT_CODE": "722Y001",
                    "STAT_NAME": "한국은행 기준금리 및 여수신금리",
                    "ITEM_CODE1": "0101000",
                    "ITEM_NAME1": "한국은행 기준금리",
                    "UNIT_NAME": "연%",
                    "TIME": "20260225",
                    "DATA_VALUE": "2.75",
                },
                {
                    "STAT_CODE": "722Y001",
                    "STAT_NAME": "한국은행 기준금리 및 여수신금리",
                    "ITEM_CODE1": "0101000",
                    "ITEM_NAME1": "한국은행 기준금리",
                    "UNIT_NAME": "연%",
                    "TIME": second_time,
                    "DATA_VALUE": second_value,
                },
            ],
        }
    }
    return json.dumps(body, ensure_ascii=False).encode("utf-8")


class EcosProviderTests(unittest.TestCase):
    def provider(self, transport) -> EcosProvider:
        return EcosProvider(
            api_key="fixture-key",
            bindings={
                IDENTIFIER: EcosSeriesBinding(
                    source_identifier=IDENTIFIER,
                    statistic_code="722Y001",
                    item_code1="0101000",
                    cycle="D",
                    subject_id=SUBJECT_ID,
                    unit="percent_per_annum",
                )
            },
            transport=transport,
            clock=lambda: NOW,
        )

    def request(self, *identifiers: str) -> FetchRequest:
        return FetchRequest(
            dataset=ProviderCapability.ECONOMIC_SERIES.value,
            source_identifiers=identifiers,
            start_at=START,
            end_at=END,
        )

    def test_parses_decimal_utc_and_preserves_source_metadata(self) -> None:
        captured: dict[str, object] = {}

        def transport(url: str, timeout: float) -> bytes:
            captured["url"] = url
            captured["timeout"] = timeout
            return payload()

        result = self.provider(transport).fetch(self.request(IDENTIFIER))

        self.assertTrue(result.succeeded)
        self.assertEqual(len(result.observations), 2)
        first = result.observations[0]
        self.assertEqual(first.value, Decimal("2.75"))
        self.assertEqual(first.observed_at, datetime(2026, 2, 25, tzinfo=UTC))
        self.assertEqual(first.unit, "percent_per_annum")
        self.assertEqual(first.source.attributes["statistic_code"], "722Y001")
        self.assertEqual(first.source.attributes["item_code1"], "0101000")
        self.assertEqual(first.source.attributes["cycle"], "D")
        self.assertEqual(first.source.attributes["source_unit"], "연%")
        self.assertIn("/StatisticSearch/fixture-key/json/kr/1/100/722Y001/D/20260101/20260807/0101000", str(captured["url"]))
        self.assertEqual(captured["timeout"], 15.0)

    def test_missing_value_is_explicit_partial_failure(self) -> None:
        result = self.provider(lambda _url, _timeout: payload(second_value="-")).fetch(self.request(IDENTIFIER))
        self.assertTrue(result.partial)
        self.assertEqual(len(result.observations), 1)
        self.assertEqual({failure.code for failure in result.failures}, {"MISSING_VALUE"})

    def test_invalid_period_is_explicit_failure(self) -> None:
        result = self.provider(lambda _url, _timeout: payload(second_time="20261340")).fetch(self.request(IDENTIFIER))
        self.assertTrue(result.partial)
        self.assertEqual({failure.code for failure in result.failures}, {"INVALID_OBSERVATION"})

    def test_unknown_binding_and_success_produce_partial_result(self) -> None:
        result = self.provider(lambda _url, _timeout: payload()).fetch(self.request(IDENTIFIER, "unknown"))
        self.assertTrue(result.partial)
        self.assertEqual(len(result.observations), 2)
        self.assertEqual({failure.code for failure in result.failures}, {"UNKNOWN_BINDING"})

    def test_http_server_failure_is_retryable(self) -> None:
        def transport(_url: str, _timeout: float) -> bytes:
            raise HTTPError("https://example.invalid", 503, "unavailable", {}, None)

        result = self.provider(transport).fetch(self.request(IDENTIFIER))
        self.assertEqual(result.failures[0].code, "HTTP_503")
        self.assertTrue(result.failures[0].retryable)

    def test_http_authentication_failure_is_not_retryable(self) -> None:
        def transport(_url: str, _timeout: float) -> bytes:
            raise HTTPError("https://example.invalid", 403, "forbidden", {}, None)

        result = self.provider(transport).fetch(self.request(IDENTIFIER))
        self.assertEqual(result.failures[0].code, "AUTH_ERROR")
        self.assertFalse(result.failures[0].retryable)

    def test_timeout_transport_failure_is_sanitized(self) -> None:
        def transport(_url: str, _timeout: float) -> bytes:
            raise TimeoutError("secret-bearing details must not be logged")

        failure = self.provider(transport).fetch(self.request(IDENTIFIER)).failures[0]
        self.assertEqual(failure.code, "TRANSPORT_ERROR")
        self.assertTrue(failure.retryable)
        self.assertEqual(failure.provider_reference, f"{IDENTIFIER}:transport_detail=timeout")
        self.assertNotIn("secret-bearing", failure.message)

    def test_dns_urlerror_transport_failure_is_sanitized(self) -> None:
        def transport(_url: str, _timeout: float) -> bytes:
            raise URLError(socket.gaierror(-2, "name lookup details"))

        failure = self.provider(transport).fetch(self.request(IDENTIFIER)).failures[0]
        self.assertEqual(failure.provider_reference, f"{IDENTIFIER}:transport_detail=dns")

    def test_tls_urlerror_transport_failure_is_sanitized(self) -> None:
        def transport(_url: str, _timeout: float) -> bytes:
            raise URLError(ssl.SSLError("certificate details"))

        failure = self.provider(transport).fetch(self.request(IDENTIFIER)).failures[0]
        self.assertEqual(failure.provider_reference, f"{IDENTIFIER}:transport_detail=tls")

    def test_connection_transport_failure_is_sanitized(self) -> None:
        def transport(_url: str, _timeout: float) -> bytes:
            raise ConnectionResetError("peer details")

        failure = self.provider(transport).fetch(self.request(IDENTIFIER)).failures[0]
        self.assertEqual(failure.provider_reference, f"{IDENTIFIER}:transport_detail=connection")

    def test_malformed_payload_is_invalid_payload_failure(self) -> None:
        result = self.provider(lambda _url, _timeout: b'{"StatisticSearch": {}}').fetch(self.request(IDENTIFIER))
        self.assertEqual(result.failures[0].code, "INVALID_PAYLOAD")
        self.assertFalse(result.failures[0].retryable)

    def test_out_of_range_period_is_rejected(self) -> None:
        result = self.provider(lambda _url, _timeout: payload(second_time="20251231")).fetch(self.request(IDENTIFIER))
        self.assertTrue(result.partial)
        self.assertEqual({failure.code for failure in result.failures}, {"OUT_OF_RANGE"})

    def test_quarterly_period_is_mapped_to_period_start_utc(self) -> None:
        provider = EcosProvider(
            api_key="fixture-key",
            bindings={
                "quarterly": EcosSeriesBinding(
                    source_identifier="quarterly",
                    statistic_code="200Y001",
                    item_code1="10111",
                    cycle="Q",
                    subject_id=SUBJECT_ID,
                    unit="index",
                )
            },
            transport=lambda _url, _timeout: json.dumps(
                {
                    "StatisticSearch": {
                        "row": [
                            {
                                "STAT_CODE": "200Y001",
                                "ITEM_CODE1": "10111",
                                "UNIT_NAME": "십억원",
                                "TIME": "2026Q2",
                                "DATA_VALUE": "123.4",
                            }
                        ]
                    }
                }
            ).encode(),
            clock=lambda: NOW,
        )
        result = provider.fetch(self.request("quarterly"))
        self.assertEqual(result.observations[0].observed_at, datetime(2026, 4, 1, tzinfo=UTC))


if __name__ == "__main__":
    unittest.main()
