"""Bank of Korea ECOS StatisticSearch adapter for canonical economic observations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
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

ECOS_API_ROOT = "https://ecos.bok.or.kr/api/StatisticSearch"
SUPPORTED_CYCLES = frozenset({"A", "Q", "M", "D"})


class EcosTransport(Protocol):
    def __call__(self, url: str, timeout: float) -> bytes:
        """Return the response body or raise a transport exception."""


def _default_transport(url: str, timeout: float) -> bytes:
    with urlopen(url, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS endpoint
        return response.read()


@dataclass(frozen=True, slots=True)
class EcosSeriesBinding:
    source_identifier: str
    statistic_code: str
    item_code1: str
    cycle: str
    subject_id: UUID
    unit: str
    item_code2: str = ""
    item_code3: str = ""
    item_code4: str = ""

    def __post_init__(self) -> None:
        source_identifier = self.source_identifier.strip()
        statistic_code = self.statistic_code.strip().upper()
        item_code1 = self.item_code1.strip()
        cycle = self.cycle.strip().upper()
        unit = self.unit.strip()
        if not source_identifier:
            raise ValueError("source_identifier must not be empty")
        if not statistic_code:
            raise ValueError("statistic_code must not be empty")
        if not item_code1:
            raise ValueError("item_code1 must not be empty")
        if cycle not in SUPPORTED_CYCLES:
            raise ValueError(f"cycle must be one of {sorted(SUPPORTED_CYCLES)}")
        if not unit:
            raise ValueError("unit must not be empty")
        object.__setattr__(self, "source_identifier", source_identifier)
        object.__setattr__(self, "statistic_code", statistic_code)
        object.__setattr__(self, "item_code1", item_code1)
        object.__setattr__(self, "cycle", cycle)
        object.__setattr__(self, "unit", unit)
        object.__setattr__(self, "item_code2", self.item_code2.strip())
        object.__setattr__(self, "item_code3", self.item_code3.strip())
        object.__setattr__(self, "item_code4", self.item_code4.strip())


class EcosProvider(DataProvider):
    """Normalize ECOS StatisticSearch rows without exposing secret-bearing URLs."""

    def __init__(
        self,
        *,
        api_key: str,
        bindings: Mapping[str, EcosSeriesBinding],
        transport: EcosTransport = _default_transport,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        timeout: float = 15.0,
        page_size: int = 100,
    ) -> None:
        normalized_key = api_key.strip()
        if not normalized_key:
            raise ValueError("ECOS api_key must not be empty")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if page_size < 1 or page_size > 1000:
            raise ValueError("page_size must be between 1 and 1000")
        normalized_bindings = {key.strip(): value for key, value in bindings.items()}
        if not normalized_bindings:
            raise ValueError("bindings must not be empty")
        if any(key != binding.source_identifier for key, binding in normalized_bindings.items()):
            raise ValueError("binding keys must match binding source_identifier values")
        self._api_key = normalized_key
        self._bindings = normalized_bindings
        self._transport = transport
        self._clock = clock
        self._timeout = timeout
        self._page_size = page_size

    @property
    def name(self) -> str:
        return "ecos"

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
            source_identifier = requested_identifier.strip()
            binding = self._bindings.get(source_identifier)
            if binding is None:
                failures.append(self._failure(run_id, "UNKNOWN_BINDING", source_identifier, False, retrieved_at))
                continue
            try:
                payload = self._load_series(binding, request)
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
                code = "AUTH_ERROR" if error.code in {401, 403} else f"HTTP_{error.code}"
                failures.append(self._failure(run_id, code, source_identifier, retryable, retrieved_at))
            except (URLError, TimeoutError, OSError) as error:
                failures.append(
                    self._failure(
                        run_id,
                        "TRANSPORT_ERROR",
                        f"{source_identifier}: {type(error).__name__}",
                        True,
                        retrieved_at,
                    )
                )
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError) as error:
                failures.append(
                    self._failure(run_id, "INVALID_PAYLOAD", f"{source_identifier}: {error}", False, retrieved_at)
                )

        return FetchResult(
            provider=self.name,
            request=request,
            observations=tuple(observations),
            failures=tuple(failures),
        )

    def _load_series(self, binding: EcosSeriesBinding, request: FetchRequest) -> object:
        start_period = _format_period(request.start_at, binding.cycle)
        end_period = _format_period(request.end_at, binding.cycle)
        segments = [
            ECOS_API_ROOT,
            quote(self._api_key, safe=""),
            "json",
            "kr",
            "1",
            str(self._page_size),
            quote(binding.statistic_code, safe=""),
            binding.cycle,
            start_period,
            end_period,
            quote(binding.item_code1, safe=""),
        ]
        for item_code in (binding.item_code2, binding.item_code3, binding.item_code4):
            if item_code:
                segments.append(quote(item_code, safe=""))
        body = self._transport("/".join(segments), self._timeout)
        return json.loads(body.decode("utf-8"))

    def _parse_series(
        self,
        *,
        payload: object,
        binding: EcosSeriesBinding,
        run_id: UUID,
        retrieved_at: datetime,
        request: FetchRequest,
    ) -> tuple[list[Observation], list[IngestionFailure]]:
        if not isinstance(payload, dict):
            raise ValueError("ECOS payload must be an object")
        top_result = payload.get("RESULT")
        if isinstance(top_result, dict):
            code = str(top_result.get("CODE", ""))
            message = str(top_result.get("MESSAGE", ""))
            raise ValueError(f"ECOS RESULT {code}: {message}".strip())
        service = payload.get("StatisticSearch")
        if not isinstance(service, dict):
            raise ValueError("StatisticSearch object is required")
        service_result = service.get("RESULT")
        if isinstance(service_result, dict):
            code = str(service_result.get("CODE", ""))
            if code and code != "INFO-000":
                raise ValueError(f"ECOS RESULT {code}")
        rows = service.get("row")
        if not isinstance(rows, list):
            raise ValueError("StatisticSearch row array is required")

        observations: list[Observation] = []
        failures: list[IngestionFailure] = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                failures.append(
                    self._failure(run_id, "INVALID_OBSERVATION", f"{binding.source_identifier}[{index}]", False, retrieved_at)
                )
                continue
            raw_period = str(row.get("TIME", "")).strip()
            raw_value = row.get("DATA_VALUE")
            if raw_value is None or str(raw_value).strip() in {"", ".", "-"}:
                failures.append(
                    self._failure(run_id, "MISSING_VALUE", f"{binding.source_identifier}:{raw_period}", False, retrieved_at)
                )
                continue
            try:
                value = Decimal(str(raw_value).replace(",", "").strip())
                if not value.is_finite():
                    raise InvalidOperation
                observed_at = _parse_period(raw_period, binding.cycle)
            except (InvalidOperation, ValueError, TypeError):
                failures.append(
                    self._failure(run_id, "INVALID_OBSERVATION", f"{binding.source_identifier}:{raw_period}", False, retrieved_at)
                )
                continue
            if observed_at < request.start_at or observed_at > request.end_at:
                failures.append(
                    self._failure(run_id, "OUT_OF_RANGE", f"{binding.source_identifier}:{raw_period}", False, retrieved_at)
                )
                continue

            source_unit = str(row.get("UNIT_NAME", "")).strip()
            attributes = {
                "statistic_code": str(row.get("STAT_CODE", binding.statistic_code)).strip(),
                "statistic_name": str(row.get("STAT_NAME", "")).strip(),
                "item_code1": str(row.get("ITEM_CODE1", binding.item_code1)).strip(),
                "item_name1": str(row.get("ITEM_NAME1", "")).strip(),
                "item_code2": str(row.get("ITEM_CODE2", binding.item_code2)).strip(),
                "item_name2": str(row.get("ITEM_NAME2", "")).strip(),
                "item_code3": str(row.get("ITEM_CODE3", binding.item_code3)).strip(),
                "item_name3": str(row.get("ITEM_NAME3", "")).strip(),
                "item_code4": str(row.get("ITEM_CODE4", binding.item_code4)).strip(),
                "item_name4": str(row.get("ITEM_NAME4", "")).strip(),
                "cycle": binding.cycle,
                "source_period": raw_period,
                "source_unit": source_unit,
            }
            identity = ":".join(
                [
                    "ecos",
                    binding.statistic_code,
                    binding.item_code1,
                    binding.item_code2,
                    binding.item_code3,
                    binding.item_code4,
                    binding.cycle,
                    raw_period,
                ]
            )
            observations.append(
                Observation(
                    observation_id=uuid5(NAMESPACE_URL, identity),
                    kind=ObservationKind.ECONOMIC,
                    subject_id=binding.subject_id,
                    observed_at=observed_at,
                    value=value,
                    unit=binding.unit,
                    quality=DataQualityState.VALID,
                    freshness=FreshnessState.UNKNOWN,
                    source=ProviderMetadata(
                        provider=self.name,
                        source_identifier=binding.source_identifier,
                        retrieved_at=retrieved_at,
                        attributes=attributes,
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
            message=f"ECOS retrieval failed: {reference}",
            retryable=retryable,
            occurred_at=occurred_at,
            provider_reference=reference,
        )


def _format_period(value: datetime, cycle: str) -> str:
    normalized = value.astimezone(UTC)
    if cycle == "A":
        return f"{normalized.year:04d}"
    if cycle == "Q":
        quarter = (normalized.month - 1) // 3 + 1
        return f"{normalized.year:04d}Q{quarter}"
    if cycle == "M":
        return f"{normalized.year:04d}{normalized.month:02d}"
    if cycle == "D":
        return f"{normalized.year:04d}{normalized.month:02d}{normalized.day:02d}"
    raise ValueError(f"unsupported ECOS cycle: {cycle}")


def _parse_period(raw_period: str, cycle: str) -> datetime:
    if cycle == "A":
        if len(raw_period) != 4 or not raw_period.isdigit():
            raise ValueError("invalid annual period")
        return datetime(int(raw_period), 1, 1, tzinfo=UTC)
    if cycle == "Q":
        if len(raw_period) != 6 or raw_period[4] != "Q" or raw_period[5] not in "1234":
            raise ValueError("invalid quarterly period")
        month = (int(raw_period[5]) - 1) * 3 + 1
        return datetime(int(raw_period[:4]), month, 1, tzinfo=UTC)
    if cycle == "M":
        if len(raw_period) != 6 or not raw_period.isdigit():
            raise ValueError("invalid monthly period")
        return datetime(int(raw_period[:4]), int(raw_period[4:6]), 1, tzinfo=UTC)
    if cycle == "D":
        if len(raw_period) != 8 or not raw_period.isdigit():
            raise ValueError("invalid daily period")
        return datetime(int(raw_period[:4]), int(raw_period[4:6]), int(raw_period[6:8]), tzinfo=UTC)
    raise ValueError(f"unsupported ECOS cycle: {cycle}")
