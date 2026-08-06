"""Provider abstraction for canonical data retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol, runtime_checkable

from .models import IngestionFailure, Observation


class ProviderCapability(StrEnum):
    MARKET_PRICES = "market_prices"
    FX_RATES = "fx_rates"
    ECONOMIC_SERIES = "economic_series"


@dataclass(frozen=True, slots=True)
class FetchRequest:
    dataset: str
    source_identifiers: tuple[str, ...]
    start_at: datetime
    end_at: datetime

    def __post_init__(self) -> None:
        dataset = self.dataset.strip().lower()
        if not dataset:
            raise ValueError("dataset must not be empty")
        object.__setattr__(self, "dataset", dataset)
        identifiers = tuple(value.strip() for value in self.source_identifiers if value.strip())
        if not identifiers:
            raise ValueError("source_identifiers must not be empty")
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("source_identifiers must be unique")
        object.__setattr__(self, "source_identifiers", identifiers)
        for name in ("start_at", "end_at"):
            value = getattr(self, name)
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
            object.__setattr__(self, name, value.astimezone(UTC))
        if self.end_at < self.start_at:
            raise ValueError("end_at must not precede start_at")


@dataclass(frozen=True, slots=True)
class FetchResult:
    provider: str
    request: FetchRequest
    observations: tuple[Observation, ...] = ()
    failures: tuple[IngestionFailure, ...] = ()

    def __post_init__(self) -> None:
        provider = self.provider.strip().lower()
        if not provider:
            raise ValueError("provider must not be empty")
        object.__setattr__(self, "provider", provider)
        if not self.observations and not self.failures:
            raise ValueError("fetch result must contain observations or failures")
        if self.failures and not self.observations and not all(failure.run_id for failure in self.failures):
            raise ValueError("failures must reference an ingestion run")

    @property
    def succeeded(self) -> bool:
        return bool(self.observations) and not self.failures

    @property
    def partial(self) -> bool:
        return bool(self.observations) and bool(self.failures)


@runtime_checkable
class DataProvider(Protocol):
    """Stable provider boundary; implementations return canonical observations."""

    @property
    def name(self) -> str:
        """Return a stable lowercase provider name."""

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        """Return supported dataset capabilities."""

    def fetch(self, request: FetchRequest) -> FetchResult:
        """Fetch and normalize data without leaking provider payloads."""
