"""Import all models so Alembic autogenerate can detect them."""
from organic_market_agent.models.measurement import MeasurementUnit, UnitConversion
from organic_market_agent.models.sources import Source, SourceFetchProfile
from organic_market_agent.models.normalizer import NormalizerProfile, NormalizerRule
from organic_market_agent.models.products import Product, ProductAlias, ProductMerge, ProductVariant
from organic_market_agent.models.runs import IngestionRun, RawAsset, RawExtractedItem, SourceFetchRun
from organic_market_agent.models.observations import NormalizedObservation, ObservationFlag
from organic_market_agent.models.aggregates import DailyAggregate, WeeklySnapshot
from organic_market_agent.models.publishing import PublishArtifact, PublishRun
from organic_market_agent.models.catalog_scope_skip import CatalogScopeSkipRule
from organic_market_agent.models.catalog_inbox import PendingProductAlias, ProductCatalogSuggestion
from organic_market_agent.models.scheduler import PipelineAlert, SchedulerConfig
from organic_market_agent.models.users import AuditLog, LogEntry, User
from organic_market_agent.crop_book.models import (
    CropFamily,
    Crop,
    CropVariety,
    CropVarietySourceValue,
    CropConversionGroup,
    CropUnitConversion,
)

__all__ = [
    "MeasurementUnit",
    "UnitConversion",
    "Product",
    "ProductAlias",
    "ProductVariant",
    "ProductMerge",
    "Source",
    "SourceFetchProfile",
    "NormalizerProfile",
    "NormalizerRule",
    "IngestionRun",
    "SourceFetchRun",
    "RawAsset",
    "RawExtractedItem",
    "NormalizedObservation",
    "ObservationFlag",
    "DailyAggregate",
    "WeeklySnapshot",
    "PublishRun",
    "PublishArtifact",
    "User",
    "AuditLog",
    "LogEntry",
    "SchedulerConfig",
    "PipelineAlert",
    "CatalogScopeSkipRule",
    "ProductCatalogSuggestion",
    "PendingProductAlias",
    "CropFamily",
    "Crop",
    "CropVariety",
    "CropVarietySourceValue",
    "CropConversionGroup",
    "CropUnitConversion",
]
