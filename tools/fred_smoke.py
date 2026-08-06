"""Protected live smoke test for the FRED adapter."""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime, timedelta
from uuid import UUID

from investment_manager.data.fred import FredProvider, FredSeriesBinding
from investment_manager.data.providers import FetchRequest, FetchResult, ProviderCapability

SERIES_ID = "DGS10"
SUBJECT_ID = UUID("f612b89b-8db7-5c20-9115-2af66f0fdc77")
TOLERATED_FAILURE_CODES = frozenset({"MISSING_VALUE", "OUT_OF_RANGE"})


def validate_result(result: FetchResult) -> tuple[bool, tuple[str, ...]]:
    """Return whether a live result proves connectivity and its warning/error codes."""
    codes = tuple(sorted({failure.code for failure in result.failures}))
    fatal_codes = tuple(code for code in codes if code not in TOLERATED_FAILURE_CODES)
    if not result.observations or fatal_codes:
        return False, codes
    return True, codes


def main() -> int:
    api_key = os.environ.get("FRED_API_KEY", "").strip()
    if not api_key:
        print("FRED smoke test failed: repository secret FRED_API_KEY is not configured.", file=sys.stderr)
        return 2

    end_at = datetime.now(UTC)
    start_at = end_at - timedelta(days=45)
    provider = FredProvider(
        api_key=api_key,
        bindings={
            SERIES_ID: FredSeriesBinding(
                series_id=SERIES_ID,
                subject_id=SUBJECT_ID,
                unit="percent",
            )
        },
    )
    request = FetchRequest(
        dataset=ProviderCapability.ECONOMIC_SERIES.value,
        source_identifiers=(SERIES_ID,),
        start_at=start_at,
        end_at=end_at,
    )
    result = provider.fetch(request)
    valid, codes = validate_result(result)

    if not valid:
        rendered = ",".join(codes) if codes else "EMPTY_RESULT"
        print(f"FRED smoke test failed safely: failure_codes={rendered}", file=sys.stderr)
        return 1

    first = min(result.observations, key=lambda item: item.observed_at)
    last = max(result.observations, key=lambda item: item.observed_at)
    print("FRED smoke test succeeded")
    print(f"provider={result.provider}")
    print(f"series={SERIES_ID}")
    print(f"observation_count={len(result.observations)}")
    print(f"first_observed_at={first.observed_at.isoformat()}")
    print(f"last_observed_at={last.observed_at.isoformat()}")
    print(f"last_quality={last.quality.value}")
    print(f"last_freshness={last.freshness.value}")
    if codes:
        print(f"tolerated_warning_codes={','.join(codes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
