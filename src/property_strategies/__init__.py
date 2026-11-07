"""Hypothesis strategies for common structured data formats."""

from __future__ import annotations

from property_strategies.errors import PropertyStrategiesError
from property_strategies.strategies import (
    emails,
    http_urls,
    json_values,
    rfc3339_datetimes,
    semvers,
    slugs,
)

__version__ = "0.1.0"

__all__ = [
    "PropertyStrategiesError",
    "__version__",
    "emails",
    "http_urls",
    "json_values",
    "rfc3339_datetimes",
    "semvers",
    "slugs",
]
