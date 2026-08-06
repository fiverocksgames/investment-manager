"""FRED economic-series adapter using the official observations API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
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

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


class FredTransport(Protocol):
    def __call__(self, url: str, timeout: float) -> bytes:
        """Return the response body or raise a transport exception."""


def _default_transport(url: str, timeout: float) -> bytes:
    with urlopen(url, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS endpoint
        return response.read()


@dataclass(frozen=True, slots=True)
class FredSeriesBinding:
    series_id: str
    subject_id: UUID
    unit: str

    def __post_init__(self) -> None:
        series_id = self.series_id.strip().upper()
        unit = self.unit.strip()
        if not series_id:
            raise ValueError("series_id must not be empty")
        if not unit:
            raise ValueError("unit must not be empty")
        object.__setattr__(self, "series_id", series_id)
        object.__setattr__(self, "unit", unit)


class FredProvider(DataProvider):
    """Normalize FRED observations without leaking provider payloads."""

    def __init__(
        self,
        *,
        api_key: str,
        bindings: Mapping[str, FredSeriesBinding],
        transport: FredTransport = _default_transport,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        timeout: float = 15.0,
    ) -> None:
        normalized_key = api_key.strip()
        if len(normalized_key) != 32 or not normalized_key.isalnum() or normalized_key.lower() != normalized_key:
            raise ValueError("FRED api_key must be a 32-character lowercase alphanumeric string")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        normalized_bindings = {key.strip().upper(): value for key, value in bindings.items()}
        if not normalized_bindings:
            raise ValueError("bindings must not be empty")
        if any(key != binding.series_id for key, binding in normalized_bindings.items()):
            raise ValueError("binding keys must match binding series_id values")
        self._api_key = normalized_key
        self._bindings = normalized_bindings
        self._transport = transport
        self._clock = clock
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "fred"

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return frozenset({ProviderCapability.ECONOMIC_SERIES})

    def fetch(self, request: FetchRequest) -> FetchResult:
        run_id = uuid4()
        retrieved_at = self._clock().astimezone(UTC)
        observations: list[Observation] = []
        failures: list[IngestionFailure] = []

        if request.dataset != ProviderCapability.ECONOMIC_SERIES.value:
            failures.append(self._failure(run_id, "UNSUPPORTED_DATASET", request.dataset, False, retrieved_at))
            return FetchResult(provider=self.name, request=request, failures=tuple(failures))

        for requested_identifier in request.source_identifiers:
            series_id = requested_identifier.strip().upper()
            binding = self._bindings.get(series_id)
            if binding is None:
                failures.append(self._failure(run_id, "UNKNOWN_BINDING", series_id, False, retrieved_at))
                continue
            try:
                payload = self._load_series(series_id, request)
                series_observations, series_failures = self._parse_series(
                    payload=payload,
                    binding=binding,
                    run_id=run_id,
                    retrieved_at=retrieved_at,
                    request=request,
                )
                observations.extend(series_observations)
                failures.extend(series_failures)
            except HTTPError as error:
                retryable = error.code == 429 or 500 <= error.code < 600
                failures.append(self._failure(run_id, f"HTTP_{error.code}", series_id, retryable, retrieved_at))
            except (URLError, TimeoutError, OSError) as error:
                failures.append(self._failure(run_id, "TRANSPORT_ERROR", f"{series_id}: {type(error).__name__}", True, retrieved_at))
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError) as error:
                failures.append(self._failure(run_id, "INVALID_PAYLOAD", f"{series_id}: {error}", False, retrieved_at))

        return FetchResult(
            provider=self.name,
            request=request,
            observations=tuple(observations),
            failures=tuple(failures),
        )

    def _load_series(self, series_id: str, request: FetchRequest) -> object:
        params = {
            "series_id": series_id,
            "api_key": self._api_key,
            "file_type": "json",
            "observation_start": request.start_at.date().isoformat(),
            "observation_end": request.end_at.date().isoformat(),
            "sort_order": "asc",
        }
        body = self._transport(f"{FRED_OBSERVATIONS_URL}?{urlencode(params)}", self._timeout)
        return json.loads(body.decode("utf-8"))

    def _parse_series(
        self,
        *,
        payload: object,
        binding: FredSeriesBinding,
        run_id: UUID,
        retrieved_at: datetime,
        request: FetchRequest,
    ) -> tuple[list[Observation], list[IngestionFailure]]:
        if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
            raise ValueError("observations array is required")

        observations: list[Observation] = []
        failures: list[IngestionFailure] = []
        for index, item in enumerate(payload["observations"]):
            if not isinstance(item, dict):
                failures.append(self._failure(run_id, "INVALID_OBSERVATION", f"{binding.series_id}[{index}]", False, retrieved_at))
                continue
            raw_value = item.get("value")
            raw_date = item.get("date")
            if raw_value == ".":
                failures.append(self._failure(run_id, "MISSING_VALUE", f"{binding.series_id}:{raw_date}", False, retrieved_at))
                continue
            try:
                value = Decimal(str(raw_value))
                observed_date = date.fromisoformat(str(raw_date))
                observed_at = datetime(observed_date.year, observed_date.month, observed_date.day, tzinfo=UTC)
            except (InvalidOperation, ValueError, TypeError):
                failures.append(self._failure(run_id, "INVALID_OBSERVATION", f"{binding.series_id}:{raw_date}", False, retrieved_at))
                continue
            if observed_at < request.start_at or observed_at > request.end_at:
                failures.append(self._failure(run_id, "OUT_OF_RANGE", f"{binding.series_id}:{raw_date}", False, retrieved_at))
                continue
            realtime_start = str(item.get("realtime_start", ""))
            realtime_end = str(item.get("realtime_end", ""))
            revision = f"{realtime_start}/{realtime_end}" if realtime_start or realtime_end else None
            quality = DataQualityState.REVISED if realtime_start and realtime_end and realtime_start != realtime_end else DataQualityState.VALID
            observations.append(
                Observation(
                    observation_id=uuid5(NAMESPACE_URL, f"fred:{binding.series_id}:{raw_date}:{revision}"),
                    kind=ObservationKind.ECONOMIC,
                    subject_id=binding.subject_id,
                    observed_at=observed_at,
                    value=value,
                    unit=binding.unit,
                    quality=quality,
                    freshness=FreshnessState.UNKNOWN,
                    source=ProviderMetadata(
                        provider=self.name,
                        source_identifier=binding.series_id,
                        retrieved_at=retrieved_at,
                        revision=revision,
                        attributes={"realtime_start": realtime_start, "realtime_end": realtime_end},
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
            message=f"FRED retrieval failed: {reference}",
            retryable=retryable,
            occurred_at=occurred_at,
            provider_reference=reference,
        )
