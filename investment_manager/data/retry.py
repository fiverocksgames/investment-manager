"""Provider-independent bounded retry execution."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable

from .providers import DataProvider, FetchRequest, FetchResult


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded exponential-backoff policy for retryable provider failures."""

    max_attempts: int = 3
    base_delay_seconds: float = 5.0
    max_delay_seconds: float = 30.0
    jitter_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds must not be negative")
        if self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError("max_delay_seconds must be at least base_delay_seconds")
        if self.jitter_seconds < 0:
            raise ValueError("jitter_seconds must not be negative")


@dataclass(frozen=True, slots=True)
class RetryExecution:
    """Final provider result plus bounded retry evidence."""

    result: FetchResult
    attempts: int
    max_attempts: int
    delays: tuple[float, ...]

    @property
    def exhausted(self) -> bool:
        """Return whether a retryable result consumed the full attempt budget."""
        return (
            self.attempts == self.max_attempts
            and not self.result.observations
            and bool(self.result.failures)
            and all(failure.retryable for failure in self.result.failures)
        )


class BoundedRetryExecutor:
    """Retry whole provider requests only when doing so is unambiguously safe."""

    def __init__(
        self,
        *,
        policy: RetryPolicy = RetryPolicy(),
        sleeper: Callable[[float], None] = time.sleep,
        random_value: Callable[[], float] = random.random,
    ) -> None:
        self._policy = policy
        self._sleeper = sleeper
        self._random_value = random_value

    def execute(self, provider: DataProvider, request: FetchRequest) -> RetryExecution:
        delays: list[float] = []
        for attempt in range(1, self._policy.max_attempts + 1):
            result = provider.fetch(request)
            if not self._should_retry(result) or attempt == self._policy.max_attempts:
                return RetryExecution(
                    result=result,
                    attempts=attempt,
                    max_attempts=self._policy.max_attempts,
                    delays=tuple(delays),
                )

            delay = self._delay_for(attempt)
            delays.append(delay)
            self._sleeper(delay)

        raise AssertionError("bounded retry loop must return within max_attempts")

    @staticmethod
    def _should_retry(result: FetchResult) -> bool:
        if result.observations or not result.failures:
            return False
        return all(failure.retryable for failure in result.failures)

    def _delay_for(self, failed_attempt: int) -> float:
        jitter_factor = self._random_value()
        if not 0.0 <= jitter_factor <= 1.0:
            raise ValueError("random_value must return a value between 0 and 1")
        exponential = self._policy.base_delay_seconds * (2 ** (failed_attempt - 1))
        return min(
            self._policy.max_delay_seconds,
            exponential + self._policy.jitter_seconds * jitter_factor,
        )
