"""Controlled live smoke test for the Yahoo daily market-data adapter."""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from uuid import UUID

from investment_manager.data.models import ObservationKind
from investment_manager.data.providers import FetchRequest, FetchResult, ProviderCapability
from investment_manager.data.retry import BoundedRetryExecutor, RetryPolicy
from investment_manager.data.yahoo import YahooProvider, YahooSymbolBinding

SYMBOL = "SPY"
SUBJECT_ID = UUID("8e41c5ad-5d7f-5d35-a43a-f54a3028a06f")
TOLERATED_FAILURE_CODES = frozenset({"MISSING_VALUE", "OUT_OF_RANGE"})


def validate_result(result: FetchResult) -> tuple[bool, tuple[str, ...]]:
    """Return whether a bounded live result proves basic connectivity."""
    codes = tuple(sorted({failure.code for failure in result.failures}))
    fatal_codes = tuple(code for code in codes if code not in TOLERATED_FAILURE_CODES)
    if not result.observations or fatal_codes:
        return False, codes
    return True, codes


def main() -> int:
    end_at = datetime.now(UTC)
    start_at = end_at - timedelta(days=14)
    provider = YahooProvider(
        bindings={
            SYMBOL: YahooSymbolBinding(
                symbol=SYMBOL,
                subject_id=SUBJECT_ID,
                unit="USD",
                kind=ObservationKind.MARKET_PRICE,
            )
        },
        timeout=15.0,
    )
    request = FetchRequest(
        dataset=ProviderCapability.MARKET_PRICES.value,
        source_identifiers=(SYMBOL,),
        start_at=start_at,
        end_at=end_at,
    )
    execution = BoundedRetryExecutor(
        policy=RetryPolicy(
            max_attempts=3,
            base_delay_seconds=5.0,
            max_delay_seconds=20.0,
            jitter_seconds=2.0,
        )
    ).execute(provider, request)
    result = execution.result
    valid, codes = validate_result(result)

    if not valid:
        rendered = ",".join(codes) if codes else "EMPTY_RESULT"
        print(
            "Yahoo smoke test failed safely: "
            f"failure_codes={rendered} attempts={execution.attempts} "
            f"retry_exhausted={str(execution.exhausted).lower()}",
            file=sys.stderr,
        )
        return 1

    first = min(result.observations, key=lambda item: item.observed_at)
    last = max(result.observations, key=lambda item: item.observed_at)
    print("Yahoo smoke test succeeded")
    print(f"provider={result.provider}")
    print(f"symbol={SYMBOL}")
    print(f"attempt_count={execution.attempts}")
    print(f"observation_count={len(result.observations)}")
    print(f"first_observed_at={first.observed_at.isoformat()}")
    print(f"last_observed_at={last.observed_at.isoformat()}")
    print(f"currency={last.unit}")
    print(f"interval={last.source.attributes.get('interval', 'unknown')}")
    if codes:
        print(f"tolerated_warning_codes={','.join(codes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
