"""Controlled live smoke test for the Bank of Korea ECOS adapter."""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime, timedelta
from uuid import UUID

from investment_manager.data.ecos import EcosProvider, EcosSeriesBinding
from investment_manager.data.providers import FetchRequest, ProviderCapability
from investment_manager.data.retry import BoundedRetryExecutor, RetryPolicy

IDENTIFIER = "bok_base_rate_daily"
SUBJECT_ID = UUID("b1f2d21e-7964-59bf-b9de-a4305a086475")
TOLERATED_FAILURE_CODES = frozenset({"MISSING_VALUE", "OUT_OF_RANGE"})


def _transport_details(result) -> tuple[str, ...]:
    details: set[str] = set()
    marker = "transport_detail="
    for failure in result.failures:
        if failure.code != "TRANSPORT_ERROR" or not failure.provider_reference:
            continue
        if marker in failure.provider_reference:
            details.add(failure.provider_reference.split(marker, 1)[1])
    return tuple(sorted(details))


def main() -> int:
    api_key = os.environ.get("ECOS_API_KEY", "").strip()
    if not api_key:
        print("ECOS smoke test failed safely: failure_codes=MISSING_SECRET attempts=0", file=sys.stderr)
        return 1

    end_at = datetime.now(UTC)
    start_at = end_at - timedelta(days=180)
    provider = EcosProvider(
        api_key=api_key,
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
        timeout=15.0,
    )
    request = FetchRequest(
        dataset=ProviderCapability.ECONOMIC_SERIES.value,
        source_identifiers=(IDENTIFIER,),
        start_at=start_at,
        end_at=end_at,
    )
    execution = BoundedRetryExecutor(
        policy=RetryPolicy(max_attempts=3, base_delay_seconds=5.0, max_delay_seconds=20.0, jitter_seconds=2.0)
    ).execute(provider, request)
    result = execution.result
    codes = tuple(sorted({failure.code for failure in result.failures}))
    fatal_codes = tuple(code for code in codes if code not in TOLERATED_FAILURE_CODES)
    transport_details = _transport_details(result)

    if not result.observations or fatal_codes:
        rendered = ",".join(codes) if codes else "NO_OBSERVATIONS"
        detail_text = f" transport_details={','.join(transport_details)}" if transport_details else ""
        print(
            "ECOS smoke test failed safely: "
            f"failure_codes={rendered} attempts={execution.attempts} retry_exhausted={str(execution.exhausted).lower()}"
            f"{detail_text}",
            file=sys.stderr,
        )
        return 1

    first = min(result.observations, key=lambda item: item.observed_at)
    last = max(result.observations, key=lambda item: item.observed_at)
    print("ECOS smoke test succeeded")
    print(f"provider={result.provider}")
    print(f"source_identifier={IDENTIFIER}")
    print(f"attempt_count={execution.attempts}")
    print(f"observation_count={len(result.observations)}")
    print(f"first_observed_at={first.observed_at.isoformat()}")
    print(f"last_observed_at={last.observed_at.isoformat()}")
    print(f"unit={last.unit}")
    print(f"cycle={last.source.attributes.get('cycle', 'unknown')}")
    if codes:
        print(f"tolerated_warning_codes={','.join(codes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
