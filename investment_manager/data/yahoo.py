"""Yahoo chart-endpoint adapter for canonical daily market observations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import urlopen
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from .models import (
    DataQualityState,
    FreshnessState,
    IngestionFailure,
    Observation,
    ObservationKind,
    ProviderMetadata,
)
from .providers import DataProvider, FetchRequest, FetchResult, ProviderCapability

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart"


class YahooTransport(Protocol):
    def __call__(self, url: str, timeout: float) -> bytes:
        """Return the response body or raise a transport exception."""


def _default_transport(url: str, timeout: float) -> bytes:
    with urlopen(url, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS endpoint
        return response.read()


@dataclass(frozen=True, slots=True)
class YahooSymbolBinding:
    symbol: str
    subject_id: UUID
    unit: str
    kind: ObservationKind = ObservationKind.MARKET_PRICE

    def __post_init__(self) -> None:
        symbol = self.symbol.strip()
        unit = self.unit.strip().upper()
        if not symbol:
            raise ValueError("symbol must not be empty")
        if not unit:
            raise ValueError("unit must not be empty")
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "unit", unit)


class YahooProvider(DataProvider):
    """Normalize Yahoo daily chart data without leaking provider payloads."""

    def __init__(
        self,
        *,
        bindings: Mapping[str, YahooSymbolBinding],
        transport: YahooTransport = _default_transport,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        timeout: float = 15.0,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        normalized_bindings = {key.strip(): value for key, value in bindings.items()}
        if not normalized_bindings:
            raise ValueError("bindings must not be empty")
        if any(key != binding.symbol for key, binding in normalized_bindings.items()):
            raise ValueError("binding keys must match binding symbol values")
        self._bindings = normalized_bindings
        self._transport = transport
        self._clock = clock
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "yahoo"

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return frozenset({ProviderCapability.MARKET_PRICES, ProviderCapability.FX_RATES})

    def fetch(self, request: FetchRequest) -> FetchResult:
        run_id = uuid4()
        retrieved_at = self._clock().astimezone(UTC)
        observations: list[Observation] = []
        failures: list[IngestionFailure] = []

        if request.dataset not in {
            ProviderCapability.MARKET_PRICES.value,
            ProviderCapability.FX_RATES.value,
        }:
            failures.append(self._failure(run_id, "UNSUPPORTED_DATASET", request.dataset, False, retrieved_at))
            return FetchResult(provider=self.name, request=request, failures=tuple(failures))

        for requested_identifier in request.source_identifiers:
            symbol = requested_identifier.strip()
            binding = self._bindings.get(symbol)
            if binding is None:
                failures.append(self._failure(run_id, "UNKNOWN_BINDING", symbol, False, retrieved_at))
                continue
            if request.dataset == ProviderCapability.FX_RATES.value and binding.kind != ObservationKind.FX_RATE:
                failures.append(self._failure(run_id, "BINDING_KIND_MISMATCH", symbol, False, retrieved_at))
                continue
            if request.dataset == ProviderCapability.MARKET_PRICES.value and binding.kind != ObservationKind.MARKET_PRICE:
                failures.append(self._failure(run_id, "BINDING_KIND_MISMATCH", symbol, False, retrieved_at))
                continue
            try:
                payload = self._load_symbol(symbol, request)
                symbol_observations, symbol_failures = self._parse_symbol(
                    payload=payload,
                    binding=binding,
                    run_id=run_id,
                    retrieved_at=retrieved_at,
                    request=request,
                )
                observations.extend(symbol_observations)
                failures.extend(symbol_failures)
            except HTTPError as error:
                retryable = error.code == 429 or 500 <= error.code < 600
                failures.append(self._failure(run_id, f"HTTP_{error.code}", symbol, retryable, retrieved_at))
            except (URLError, TimeoutError, OSError) as error:
                failures.append(self._failure(run_id, "TRANSPORT_ERROR", f"{symbol}: {type(error).__name__}", True, retrieved_at))
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError) as error:
                failures.append(self._failure(run_id, "INVALID_PAYLOAD", f"{symbol}: {error}", False, retrieved_at))

        return FetchResult(
            provider=self.name,
            request=request,
            observations=tuple(observations),
            failures=tuple(failures),
        )

    def _load_symbol(self, symbol: str, request: FetchRequest) -> object:
        params = {
            "period1": str(int(request.start_at.timestamp())),
            "period2": str(int(request.end_at.timestamp()) + 1),
            "interval": "1d",
            "events": "div,splits",
            "includeAdjustedClose": "true",
        }
        url = f"{YAHOO_CHART_URL}/{quote(symbol, safe='')}?{urlencode(params)}"
        body = self._transport(url, self._timeout)
        return json.loads(body.decode("utf-8"))

    def _parse_symbol(
        self,
        *,
        payload: object,
        binding: YahooSymbolBinding,
        run_id: UUID,
        retrieved_at: datetime,
        request: FetchRequest,
    ) -> tuple[list[Observation], list[IngestionFailure]]:
        if not isinstance(payload, dict):
            raise ValueError("chart payload must be an object")
        chart = payload.get("chart")
        if not isinstance(chart, dict):
            raise ValueError("chart object is required")
        if chart.get("error") is not None:
            raise ValueError("chart error was returned")
        results = chart.get("result")
        if not isinstance(results, list) or len(results) != 1 or not isinstance(results[0], dict):
            raise ValueError("exactly one chart result is required")

        result = results[0]
        timestamps = result.get("timestamp")
        indicators = result.get("indicators")
        meta = result.get("meta")
        if not isinstance(timestamps, list) or not isinstance(indicators, dict) or not isinstance(meta, dict):
            raise ValueError("timestamp, indicators, and meta are required")
        quote_rows = indicators.get("quote")
        adjclose_rows = indicators.get("adjclose")
        if not isinstance(quote_rows, list) or len(quote_rows) != 1 or not isinstance(quote_rows[0], dict):
            raise ValueError("one quote row is required")
        if not isinstance(adjclose_rows, list) or len(adjclose_rows) != 1 or not isinstance(adjclose_rows[0], dict):
            raise ValueError("one adjusted-close row is required")

        quote_row = quote_rows[0]
        adjclose_row = adjclose_rows[0]
        fields = {
            "open": quote_row.get("open"),
            "high": quote_row.get("high"),
            "low": quote_row.get("low"),
            "close": quote_row.get("close"),
            "volume": quote_row.get("volume"),
            "adjclose": adjclose_row.get("adjclose"),
        }
        if any(not isinstance(values, list) for values in fields.values()):
            raise ValueError("OHLCV and adjusted-close arrays are required")
        if any(len(values) != len(timestamps) for values in fields.values()):
            raise ValueError("timestamp and indicator lengths must match")

        currency = str(meta.get("currency", binding.unit)).strip().upper()
        exchange_timezone = str(meta.get("exchangeTimezoneName", ""))
        observations: list[Observation] = []
        failures: list[IngestionFailure] = []

        for index, raw_timestamp in enumerate(timestamps):
            try:
                observed_at = datetime.fromtimestamp(int(raw_timestamp), tz=UTC)
            except (TypeError, ValueError, OverflowError):
                failures.append(self._failure(run_id, "INVALID_OBSERVATION", f"{binding.symbol}[{index}]", False, retrieved_at))
                continue
            if observed_at < request.start_at or observed_at > request.end_at:
                failures.append(self._failure(run_id, "OUT_OF_RANGE", f"{binding.symbol}:{raw_timestamp}", False, retrieved_at))
                continue

            raw_values = {name: values[index] for name, values in fields.items()}
            if any(value is None for value in raw_values.values()):
                failures.append(self._failure(run_id, "MISSING_VALUE", f"{binding.symbol}:{raw_timestamp}", False, retrieved_at))
                continue
            try:
                decimals = {name: Decimal(str(value)) for name, value in raw_values.items()}
            except (InvalidOperation, TypeError, ValueError):
                failures.append(self._failure(run_id, "INVALID_OBSERVATION", f"{binding.symbol}:{raw_timestamp}", False, retrieved_at))
                continue
            if any(not value.is_finite() for value in decimals.values()):
                failures.append(self._failure(run_id, "INVALID_OBSERVATION", f"{binding.symbol}:{raw_timestamp}", False, retrieved_at))
                continue

            source_attributes = {
                "interval": "1d",
                "currency": currency,
                "exchange_timezone": exchange_timezone,
                "open": str(decimals["open"]),
                "high": str(decimals["high"]),
                "low": str(decimals["low"]),
                "close": str(decimals["close"]),
                "adjusted_close": str(decimals["adjclose"]),
                "volume": str(decimals["volume"]),
            }
            observations.append(
                Observation(
                    observation_id=uuid5(NAMESPACE_URL, f"yahoo:{binding.symbol}:{int(raw_timestamp)}:adjclose"),
                    kind=binding.kind,
                    subject_id=binding.subject_id,
                    observed_at=observed_at,
                    value=decimals["adjclose"],
                    unit=currency or binding.unit,
                    quality=DataQualityState.VALID,
                    freshness=FreshnessState.UNKNOWN,
                    source=ProviderMetadata(
                        provider=self.name,
                        source_identifier=binding.symbol,
                        retrieved_at=retrieved_at,
                        attributes=source_attributes,
                    ),
                )
            )
        return observations, failures

    @staticmethod
    def _failure(
        run_id: UUID,
        code: str,
        reference: str,
        retryable: bool,
        occurred_at: datetime,
    ) -> IngestionFailure:
        return IngestionFailure(
            run_id=run_id,
            code=code,
            message=f"Yahoo retrieval failed: {reference}",
            retryable=retryable,
            occurred_at=occurred_at,
            provider_reference=reference,
        )
