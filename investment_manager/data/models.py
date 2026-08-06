"""Canonical, provider-independent data-platform value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping
from uuid import UUID


class AssetClass(StrEnum):
    ETF = "etf"
    BOND = "bond"
    GOLD = "gold"
    CRYPTO = "crypto"
    CASH = "cash"
    INDEX = "index"


class ObservationKind(StrEnum):
    MARKET_PRICE = "market_price"
    FX_RATE = "fx_rate"
    ECONOMIC = "economic"


class DataQualityState(StrEnum):
    VALID = "valid"
    STALE = "stale"
    PARTIAL = "partial"
    REVISED = "revised"
    ESTIMATED = "estimated"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"


class FreshnessState(StrEnum):
    FRESH = "fresh"
    AGING = "aging"
    STALE = "stale"
    UNKNOWN = "unknown"


class IngestionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"


def _required(value: str, name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must not be empty")
    return normalized


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _metadata(value: Mapping[str, str]) -> Mapping[str, str]:
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class Asset:
    asset_id: UUID
    symbol: str
    name: str
    asset_class: AssetClass
    currency: str
    exchange: str | None = None
    active: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", _required(self.symbol, "symbol").upper())
        object.__setattr__(self, "name", _required(self.name, "name"))
        object.__setattr__(self, "currency", _required(self.currency, "currency").upper())
        if len(self.currency) != 3:
            raise ValueError("currency must be a three-letter code")
        if self.exchange is not None:
            object.__setattr__(self, "exchange", _required(self.exchange, "exchange").upper())


@dataclass(frozen=True, slots=True)
class AssetAlias:
    asset_id: UUID
    provider: str
    provider_symbol: str
    effective_from: datetime
    effective_to: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider", _required(self.provider, "provider").lower())
        object.__setattr__(self, "provider_symbol", _required(self.provider_symbol, "provider_symbol"))
        start = _utc(self.effective_from, "effective_from")
        object.__setattr__(self, "effective_from", start)
        if self.effective_to is not None:
            end = _utc(self.effective_to, "effective_to")
            if end <= start:
                raise ValueError("effective_to must be after effective_from")
            object.__setattr__(self, "effective_to", end)


@dataclass(frozen=True, slots=True)
class EconomicSeries:
    series_id: UUID
    canonical_code: str
    name: str
    frequency: str
    unit: str
    seasonal_adjustment: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "canonical_code", _required(self.canonical_code, "canonical_code").upper())
        object.__setattr__(self, "name", _required(self.name, "name"))
        object.__setattr__(self, "frequency", _required(self.frequency, "frequency").lower())
        object.__setattr__(self, "unit", _required(self.unit, "unit"))


@dataclass(frozen=True, slots=True)
class ProviderMetadata:
    provider: str
    source_identifier: str
    retrieved_at: datetime
    revision: str | None = None
    attributes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider", _required(self.provider, "provider").lower())
        object.__setattr__(self, "source_identifier", _required(self.source_identifier, "source_identifier"))
        object.__setattr__(self, "retrieved_at", _utc(self.retrieved_at, "retrieved_at"))
        object.__setattr__(self, "attributes", _metadata(self.attributes))


@dataclass(frozen=True, slots=True)
class Observation:
    observation_id: UUID
    kind: ObservationKind
    subject_id: UUID
    observed_at: datetime
    value: Decimal
    unit: str
    quality: DataQualityState
    freshness: FreshnessState
    source: ProviderMetadata

    def __post_init__(self) -> None:
        object.__setattr__(self, "observed_at", _utc(self.observed_at, "observed_at"))
        if not isinstance(self.value, Decimal):
            raise TypeError("value must be Decimal")
        if not self.value.is_finite():
            raise ValueError("value must be finite")
        object.__setattr__(self, "unit", _required(self.unit, "unit"))
        if self.source.retrieved_at < self.observed_at:
            raise ValueError("retrieved_at must not precede observed_at")
        if self.quality in {DataQualityState.INVALID, DataQualityState.UNAVAILABLE}:
            raise ValueError("invalid or unavailable data must not be represented as an Observation")


@dataclass(frozen=True, slots=True)
class DatasetPolicy:
    dataset: str
    expected_cadence: timedelta
    aging_after: timedelta
    stale_after: timedelta
    cache_ttl: timedelta
    max_attempts: int = 3

    def __post_init__(self) -> None:
        object.__setattr__(self, "dataset", _required(self.dataset, "dataset").lower())
        durations = (self.expected_cadence, self.aging_after, self.stale_after, self.cache_ttl)
        if any(value <= timedelta(0) for value in durations):
            raise ValueError("policy durations must be positive")
        if self.aging_after > self.stale_after:
            raise ValueError("aging_after must not exceed stale_after")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least one")

    def freshness_at(self, observed_at: datetime, now: datetime) -> FreshnessState:
        observed = _utc(observed_at, "observed_at")
        current = _utc(now, "now")
        age = current - observed
        if age < timedelta(0):
            return FreshnessState.UNKNOWN
        if age <= self.aging_after:
            return FreshnessState.FRESH
        if age <= self.stale_after:
            return FreshnessState.AGING
        return FreshnessState.STALE


@dataclass(frozen=True, slots=True)
class IngestionRun:
    run_id: UUID
    provider: str
    dataset: str
    started_at: datetime
    status: IngestionStatus
    attempt: int = 1
    ended_at: datetime | None = None
    records_received: int = 0
    records_accepted: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider", _required(self.provider, "provider").lower())
        object.__setattr__(self, "dataset", _required(self.dataset, "dataset").lower())
        start = _utc(self.started_at, "started_at")
        object.__setattr__(self, "started_at", start)
        if self.attempt < 1:
            raise ValueError("attempt must be at least one")
        if min(self.records_received, self.records_accepted) < 0:
            raise ValueError("record counts must be non-negative")
        if self.records_accepted > self.records_received:
            raise ValueError("records_accepted must not exceed records_received")
        if self.ended_at is not None:
            end = _utc(self.ended_at, "ended_at")
            if end < start:
                raise ValueError("ended_at must not precede started_at")
            object.__setattr__(self, "ended_at", end)
        if self.status in {IngestionStatus.SUCCEEDED, IngestionStatus.PARTIAL, IngestionStatus.FAILED} and self.ended_at is None:
            raise ValueError("terminal ingestion status requires ended_at")


@dataclass(frozen=True, slots=True)
class IngestionFailure:
    run_id: UUID
    code: str
    message: str
    retryable: bool
    occurred_at: datetime
    provider_reference: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", _required(self.code, "code").upper())
        object.__setattr__(self, "message", _required(self.message, "message"))
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at, "occurred_at"))


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    snapshot_id: UUID
    dataset: str
    provider: str
    cutoff_at: datetime
    published_at: datetime
    observation_ids: tuple[UUID, ...]
    checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "dataset", _required(self.dataset, "dataset").lower())
        object.__setattr__(self, "provider", _required(self.provider, "provider").lower())
        cutoff = _utc(self.cutoff_at, "cutoff_at")
        published = _utc(self.published_at, "published_at")
        object.__setattr__(self, "cutoff_at", cutoff)
        object.__setattr__(self, "published_at", published)
        if published < cutoff:
            raise ValueError("published_at must not precede cutoff_at")
        if not self.observation_ids:
            raise ValueError("source snapshot must contain observations")
        if len(set(self.observation_ids)) != len(self.observation_ids):
            raise ValueError("source snapshot observation_ids must be unique")
        object.__setattr__(self, "checksum", _required(self.checksum, "checksum").lower())
