"""Provider-independent foreign-exchange normalization."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from uuid import NAMESPACE_URL, UUID, uuid5

from .models import Observation, ObservationKind, ProviderMetadata

FX_RECIPROCAL_PRECISION = 34


def _currency(value: str, name: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError(f"{name} must be a three-letter alphabetic currency code")
    return normalized


@dataclass(frozen=True, slots=True)
class FxPair:
    """Canonical currency-pair identity expressed as quote currency per base currency."""

    pair_id: UUID
    base_currency: str
    quote_currency: str

    def __post_init__(self) -> None:
        base = _currency(self.base_currency, "base_currency")
        quote = _currency(self.quote_currency, "quote_currency")
        if base == quote:
            raise ValueError("base_currency and quote_currency must differ")
        object.__setattr__(self, "base_currency", base)
        object.__setattr__(self, "quote_currency", quote)

    @property
    def unit(self) -> str:
        return f"{self.quote_currency}_per_{self.base_currency}"


@dataclass(frozen=True, slots=True)
class FxNormalizationBinding:
    """Explicitly describe a source FX direction relative to one canonical pair."""

    pair: FxPair
    source_base_currency: str
    source_quote_currency: str

    def __post_init__(self) -> None:
        source_base = _currency(self.source_base_currency, "source_base_currency")
        source_quote = _currency(self.source_quote_currency, "source_quote_currency")
        if source_base == source_quote:
            raise ValueError("source_base_currency and source_quote_currency must differ")
        canonical = {self.pair.base_currency, self.pair.quote_currency}
        if {source_base, source_quote} != canonical:
            raise ValueError("source currencies must match the canonical pair")
        object.__setattr__(self, "source_base_currency", source_base)
        object.__setattr__(self, "source_quote_currency", source_quote)

    @property
    def inverted(self) -> bool:
        return self.source_base_currency == self.pair.quote_currency


class FxNormalizationError(ValueError):
    """Stable normalization error that callers can classify without parsing text."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code.strip().upper()


class FxNormalizer:
    """Normalize a trusted source FX observation into an explicit canonical direction."""

    def normalize(self, observation: Observation, binding: FxNormalizationBinding) -> Observation:
        if observation.kind is not ObservationKind.FX_RATE:
            raise FxNormalizationError("NON_FX_OBSERVATION", "observation must be an FX rate")
        if observation.subject_id != binding.pair.pair_id:
            raise FxNormalizationError("SUBJECT_MISMATCH", "observation subject does not match canonical FX pair")
        if observation.value <= Decimal("0"):
            raise FxNormalizationError("INVALID_RATE", "FX rate must be positive")

        if binding.inverted:
            with localcontext() as context:
                context.prec = FX_RECIPROCAL_PRECISION
                context.rounding = ROUND_HALF_EVEN
                normalized_value = Decimal("1") / observation.value
            transformation = "reciprocal"
        else:
            normalized_value = observation.value
            transformation = "identity"

        attributes = dict(observation.source.attributes)
        attributes.update(
            {
                "canonical_fx_base_currency": binding.pair.base_currency,
                "canonical_fx_quote_currency": binding.pair.quote_currency,
                "source_fx_base_currency": binding.source_base_currency,
                "source_fx_quote_currency": binding.source_quote_currency,
                "fx_normalization": transformation,
                "source_rate_unit": observation.unit,
            }
        )
        source = ProviderMetadata(
            provider=observation.source.provider,
            source_identifier=observation.source.source_identifier,
            retrieved_at=observation.source.retrieved_at,
            revision=observation.source.revision,
            attributes=attributes,
        )
        identity = ":".join(
            [
                "fx-normalized",
                str(binding.pair.pair_id),
                source.provider,
                source.source_identifier,
                observation.observed_at.isoformat(),
                source.revision or "",
            ]
        )
        return Observation(
            observation_id=uuid5(NAMESPACE_URL, identity),
            kind=ObservationKind.FX_RATE,
            subject_id=binding.pair.pair_id,
            observed_at=observation.observed_at,
            value=normalized_value,
            unit=binding.pair.unit,
            quality=observation.quality,
            freshness=observation.freshness,
            source=source,
        )
