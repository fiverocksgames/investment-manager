"""Deterministic tests for immutable source snapshot publication."""

from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from investment_manager.data.models import (
    DataQualityState,
    FreshnessState,
    Observation,
    ObservationKind,
    ProviderMetadata,
)
from investment_manager.data.snapshots import (
    SnapshotPublicationError,
    SnapshotPublicationPolicy,
    SourceSnapshotPublisher,
)

PROVIDER = "yahoo"
DATASET = "fx_rates"
SUBJECT_ID = UUID("a15d7850-46f2-5a0b-9f94-bdc22a5b2dc1")
OBS_1_ID = UUID("11111111-1111-5111-8111-111111111111")
OBS_2_ID = UUID("22222222-2222-5222-8222-222222222222")
OBS_3_ID = UUID("33333333-3333-5333-8333-333333333333")
CUTOFF = datetime(2026, 8, 6, 23, 59, tzinfo=UTC)
PUBLISHED = datetime(2026, 8, 7, 0, 5, tzinfo=UTC)


def observation(
    observation_id: UUID,
    observed_at: datetime,
    *,
    provider: str = PROVIDER,
    quality: DataQualityState = DataQualityState.VALID,
    freshness: FreshnessState = FreshnessState.FRESH,
    value: Decimal = Decimal("1380.25"),
) -> Observation:
    return Observation(
        observation_id=observation_id,
        kind=ObservationKind.FX_RATE,
        subject_id=SUBJECT_ID,
        observed_at=observed_at,
        value=value,
        unit="KRW_per_USD",
        quality=quality,
        freshness=freshness,
        source=ProviderMetadata(
            provider=provider,
            source_identifier="KRW=X",
            retrieved_at=datetime(2026, 8, 7, 0, 0, tzinfo=UTC),
            revision="fixture-v1",
            attributes={"source_base": "USD", "source_quote": "KRW"},
        ),
    )


class SourceSnapshotPublisherTests(unittest.TestCase):
    def test_same_logical_input_in_any_order_has_same_identity(self) -> None:
        first = observation(OBS_1_ID, datetime(2026, 8, 5, tzinfo=UTC))
        second = observation(OBS_2_ID, datetime(2026, 8, 6, tzinfo=UTC), value=Decimal("1381.50"))
        publisher = SourceSnapshotPublisher()

        left = publisher.publish(
            dataset=DATASET,
            provider=PROVIDER,
            cutoff_at=CUTOFF,
            published_at=PUBLISHED,
            observations=(first, second),
        )
        right = publisher.publish(
            dataset=DATASET,
            provider=PROVIDER,
            cutoff_at=CUTOFF,
            published_at=PUBLISHED,
            observations=(second, first),
        )

        self.assertEqual(left.snapshot_id, right.snapshot_id)
        self.assertEqual(left.checksum, right.checksum)
        self.assertEqual(left.observation_ids, right.observation_ids)

    def test_cutoff_excludes_future_observations(self) -> None:
        eligible = observation(OBS_1_ID, datetime(2026, 8, 6, tzinfo=UTC))
        future = observation(OBS_2_ID, datetime(2026, 8, 7, tzinfo=UTC))

        snapshot = SourceSnapshotPublisher().publish(
            dataset=DATASET,
            provider=PROVIDER,
            cutoff_at=CUTOFF,
            published_at=PUBLISHED,
            observations=(eligible, future),
        )

        self.assertEqual(snapshot.observation_ids, (OBS_1_ID,))

    def test_duplicate_observation_ids_fail_closed(self) -> None:
        first = observation(OBS_1_ID, datetime(2026, 8, 5, tzinfo=UTC))
        duplicate = observation(OBS_1_ID, datetime(2026, 8, 6, tzinfo=UTC))

        with self.assertRaisesRegex(SnapshotPublicationError, "duplicate observation_id"):
            SourceSnapshotPublisher().publish(
                dataset=DATASET,
                provider=PROVIDER,
                cutoff_at=CUTOFF,
                published_at=PUBLISHED,
                observations=(first, duplicate),
            )

    def test_provider_mismatch_fails_closed(self) -> None:
        mismatched = observation(OBS_1_ID, datetime(2026, 8, 6, tzinfo=UTC), provider="fred")

        with self.assertRaisesRegex(SnapshotPublicationError, "snapshot provider"):
            SourceSnapshotPublisher().publish(
                dataset=DATASET,
                provider=PROVIDER,
                cutoff_at=CUTOFF,
                published_at=PUBLISHED,
                observations=(mismatched,),
            )

    def test_partial_quality_is_rejected_by_default(self) -> None:
        partial = observation(
            OBS_1_ID,
            datetime(2026, 8, 6, tzinfo=UTC),
            quality=DataQualityState.PARTIAL,
        )

        with self.assertRaisesRegex(SnapshotPublicationError, "partial-quality"):
            SourceSnapshotPublisher().publish(
                dataset=DATASET,
                provider=PROVIDER,
                cutoff_at=CUTOFF,
                published_at=PUBLISHED,
                observations=(partial,),
            )

    def test_partial_quality_can_be_explicitly_allowed(self) -> None:
        partial = observation(
            OBS_1_ID,
            datetime(2026, 8, 6, tzinfo=UTC),
            quality=DataQualityState.PARTIAL,
            freshness=FreshnessState.AGING,
        )
        publisher = SourceSnapshotPublisher(SnapshotPublicationPolicy(allow_partial_quality=True))

        snapshot = publisher.publish(
            dataset=DATASET,
            provider=PROVIDER,
            cutoff_at=CUTOFF,
            published_at=PUBLISHED,
            observations=(partial,),
        )

        self.assertEqual(snapshot.observation_ids, (OBS_1_ID,))
        self.assertEqual(partial.freshness, FreshnessState.AGING)
        self.assertEqual(partial.source.provider, PROVIDER)

    def test_no_eligible_observations_fail_closed(self) -> None:
        future = observation(OBS_1_ID, datetime(2026, 8, 7, tzinfo=UTC))

        with self.assertRaisesRegex(SnapshotPublicationError, "no observations are eligible"):
            SourceSnapshotPublisher().publish(
                dataset=DATASET,
                provider=PROVIDER,
                cutoff_at=CUTOFF,
                published_at=PUBLISHED,
                observations=(future,),
            )

    def test_publication_time_must_not_precede_cutoff(self) -> None:
        valid = observation(OBS_1_ID, datetime(2026, 8, 5, tzinfo=UTC))

        with self.assertRaisesRegex(SnapshotPublicationError, "must not precede"):
            SourceSnapshotPublisher().publish(
                dataset=DATASET,
                provider=PROVIDER,
                cutoff_at=CUTOFF,
                published_at=CUTOFF - timedelta(seconds=1),
                observations=(valid,),
            )

    def test_timezone_aware_values_are_normalized_to_utc(self) -> None:
        kst = timezone(timedelta(hours=9))
        cutoff_kst = datetime(2026, 8, 7, 8, 59, tzinfo=kst)
        published_kst = datetime(2026, 8, 7, 9, 5, tzinfo=kst)
        valid = observation(OBS_3_ID, datetime(2026, 8, 6, 23, 0, tzinfo=UTC))

        snapshot = SourceSnapshotPublisher().publish(
            dataset=" FX_RATES ",
            provider=" YAHOO ",
            cutoff_at=cutoff_kst,
            published_at=published_kst,
            observations=(valid,),
        )

        self.assertEqual(snapshot.dataset, DATASET)
        self.assertEqual(snapshot.provider, PROVIDER)
        self.assertEqual(snapshot.cutoff_at, CUTOFF)
        self.assertEqual(snapshot.published_at, PUBLISHED)


if __name__ == "__main__":
    unittest.main()
