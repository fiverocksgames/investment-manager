"""Provider-independent data-platform contracts."""

from .fred import FredProvider, FredSeriesBinding
from .models import (
    Asset,
    AssetAlias,
    AssetClass,
    DataQualityState,
    DatasetPolicy,
    EconomicSeries,
    FreshnessState,
    IngestionFailure,
    IngestionRun,
    IngestionStatus,
    Observation,
    ObservationKind,
    ProviderMetadata,
    SourceSnapshot,
)
from .providers import DataProvider, FetchRequest, FetchResult, ProviderCapability
from .yahoo import YahooProvider, YahooSymbolBinding

__all__ = [
    "Asset",
    "AssetAlias",
    "AssetClass",
    "DataProvider",
    "DataQualityState",
    "DatasetPolicy",
    "EconomicSeries",
    "FetchRequest",
    "FetchResult",
    "FredProvider",
    "FredSeriesBinding",
    "FreshnessState",
    "IngestionFailure",
    "IngestionRun",
    "IngestionStatus",
    "Observation",
    "ObservationKind",
    "ProviderCapability",
    "ProviderMetadata",
    "SourceSnapshot",
    "YahooProvider",
    "YahooSymbolBinding",
]
