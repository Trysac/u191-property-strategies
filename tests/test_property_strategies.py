"""Behavior tests for the public API of property_strategies."""

from __future__ import annotations

import property_strategies


def test_version_is_semver() -> None:
    parts = property_strategies.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
