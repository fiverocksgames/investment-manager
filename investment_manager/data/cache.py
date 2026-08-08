"""Provider-independent, provenance-preserving fetch cache executor."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .models import DatasetPolicy
from .providers import DataProvider, FetchRequest, FetchResult


def _utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class CacheExecution:
    """Result of one cache-aware provider execution."""

    result: FetchResult
    cache_hit: bool
    cached_at: datetime | None = None
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.cache_hit and (self.cached_at is None or self.expires_at is None):
            raise ValueError("cache hits require cached_at and expires_at")
        if self.cached_at is not None:
            object.__setattr__(self, "cached_at", _utc(self.cached_at, "cached_at"))
        if self.expires_at is not None:
            object.__setattr__(self, "expires_at", _utc(self.expires_at, "expires_at"))
        if self.cached_at is not None and self.expires_at is not None and self.expires_at <= self.cached_at:
            raise ValueError("expires_at must be after cached_at")


@dataclass(frozen=True, slots=True)
class _CacheKey:
    provider: str
    dataset: str
    source_identifiers: tuple[str, ...]
    start_at: datetime
    end_at: datetime


@dataclass(frozen=True, slots=True)
class _CacheEntry:
    result: FetchResult
    cached_at: datetime
    expires_at: datetime


class CacheExecutor:
    """Reuse successful canonical fetch results without mutating provenance.

    This first implementation is process-local and intentionally does not provide
    stale-on-error fallback, background refresh, persistence, or distributed
    invalidation. Expired entries are discarded before the provider is called.
    """

    def __init__(self) -> None:
        self._entries: dict[_CacheKey, _CacheEntry] = {}

    def execute(
        self,
        provider: DataProvider,
        request: FetchRequest,
        policy: DatasetPolicy,
        *,
        now: datetime,
    ) -> CacheExecution:
        current = _utc(now, "now")
        if request.dataset != policy.dataset:
            raise ValueError("request dataset must match cache policy dataset")

        provider_name = provider.name.strip().lower()
        if not provider_name:
            raise ValueError("provider name must not be empty")

        key = _CacheKey(
            provider=provider_name,
            dataset=request.dataset,
            source_identifiers=request.source_identifiers,
            start_at=request.start_at,
            end_at=request.end_at,
        )
        entry = self._entries.get(key)
        if entry is not None:
            if current < entry.expires_at:
                return CacheExecution(
                    result=entry.result,
                    cache_hit=True,
                    cached_at=entry.cached_at,
                    expires_at=entry.expires_at,
                )
            del self._entries[key]

        result = provider.fetch(request)
        if result.provider != provider_name:
            raise ValueError("fetch result provider must match provider name")

        if result.succeeded:
            expires_at = current + policy.cache_ttl
            self._entries[key] = _CacheEntry(
                result=result,
                cached_at=current,
                expires_at=expires_at,
            )
            return CacheExecution(
                result=result,
                cache_hit=False,
                cached_at=current,
                expires_at=expires_at,
            )

        return CacheExecution(result=result, cache_hit=False)

    def clear(self) -> None:
        """Drop all process-local entries without touching provider/source data."""

        self._entries.clear()
