"""Typed errors for property_strategies."""

from __future__ import annotations

from typing import Literal


class PropertyStrategiesError(ValueError):
    """Raised eagerly when strategy parameters are invalid."""

    def __init__(
        self, message: str, code: Literal["invalid_argument"] = "invalid_argument"
    ) -> None:
        super().__init__(message)
        self.code: Literal["invalid_argument"] = code
