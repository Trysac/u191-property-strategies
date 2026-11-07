"""Comprehensive tests for property_strategies adhering strictly to specification."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

import pytest
from hypothesis import given, settings

from property_strategies import (
    PropertyStrategiesError,
    emails,
    http_urls,
    json_values,
    rfc3339_datetimes,
    semvers,
    slugs,
)

EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9_%+-]+(\.[A-Za-z0-9_%+-]+)*@([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)
SEMVER_REGEX = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-(0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(\.(0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$"
)
RFC3339_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})$")
SLUG_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def test_validation_errors_eagerly_raised() -> None:
    with pytest.raises(PropertyStrategiesError) as exc_info:
        emails(max_length=5)
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        slugs(min_size=0)
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        slugs(min_size=10, max_size=5)
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        json_values(max_depth=-1)
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        json_values(max_leaves=0)
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        rfc3339_datetimes(min_year=2100, max_year=1970)
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        rfc3339_datetimes(min_year=0)
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        http_urls(schemes=())
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        http_urls(schemes=("ftp",))  # type: ignore[arg-type]
    assert exc_info.value.code == "invalid_argument"

    with pytest.raises(PropertyStrategiesError) as exc_info:
        http_urls(max_length=5)
    assert exc_info.value.code == "invalid_argument"


@settings(derandomize=True, database=None, max_examples=200)
@given(e=emails(max_length=254, allow_plus=True))
def test_emails_acceptance(e: str) -> None:
    assert EMAIL_REGEX.match(e) is not None
    assert len(e) <= 254
    local_part = e.split("@")[0]
    assert len(local_part) <= 64


@settings(derandomize=True, database=None, max_examples=50)
@given(e=emails(max_length=6, allow_plus=False))
def test_emails_min_length_edge_case(e: str) -> None:
    assert EMAIL_REGEX.match(e) is not None
    assert len(e) <= 6
    assert "+" not in e
    assert len(e.split("@")[0]) <= 64


@settings(derandomize=True, database=None, max_examples=100)
@given(e=emails(allow_plus=False))
def test_emails_no_plus(e: str) -> None:
    assert EMAIL_REGEX.match(e) is not None
    assert "+" not in e


@settings(derandomize=True, database=None, max_examples=200)
@given(u=http_urls())
def test_http_urls_acceptance(u: str) -> None:
    parsed = urlsplit(u)
    assert parsed.scheme in ("http", "https")
    assert parsed.hostname is not None and len(parsed.hostname) > 0
    assert len(u) <= 2048
    assert urlunsplit(parsed) == u
    assert re.match(r"^[a-zA-Z0-9-._~!$&'()*+,;=:@/?%]+$", u) is not None
    # Any '%' must be followed by two uppercase hex digits
    for i, ch in enumerate(u):
        if ch == "%":
            hex_pair = u[i + 1 : i + 3]
            assert len(hex_pair) == 2
            assert all(c in "0123456789ABCDEF" for c in hex_pair)


@settings(derandomize=True, database=None, max_examples=50)
@given(u=http_urls(schemes=("https",)))
def test_http_urls_schemes_single(u: str) -> None:
    assert urlsplit(u).scheme == "https"


@settings(derandomize=True, database=None, max_examples=200)
@given(s=semvers())
def test_semvers_acceptance(s: str) -> None:
    assert SEMVER_REGEX.match(s) is not None


@settings(derandomize=True, database=None, max_examples=100)
@given(s=semvers(prerelease=False, build=False))
def test_semvers_no_pre_no_build(s: str) -> None:
    assert SEMVER_REGEX.match(s) is not None
    assert "-" not in s
    assert "+" not in s


def _count_leaves_and_depth(v: object) -> tuple[int, int]:
    if isinstance(v, dict):
        if not v:
            return 0, 1
        total_leaves = 0
        max_child_depth = 0
        for child in v.values():
            cleaves, cdepth = _count_leaves_and_depth(child)
            total_leaves += cleaves
            max_child_depth = max(max_child_depth, cdepth)
        return total_leaves, max_child_depth + 1
    if isinstance(v, list):
        if not v:
            return 0, 1
        total_leaves = 0
        max_child_depth = 0
        for child in v:
            cleaves, cdepth = _count_leaves_and_depth(child)
            total_leaves += cleaves
            max_child_depth = max(max_child_depth, cdepth)
        return total_leaves, max_child_depth + 1
    return 1, 0


@settings(derandomize=True, database=None, max_examples=200)
@given(v=json_values(allow_floats=False))
def test_json_values_no_floats(v: object) -> None:
    encoded = json.dumps(v)
    decoded = json.loads(encoded)
    assert decoded == v

    leaves, depth = _count_leaves_and_depth(v)
    assert leaves <= 50
    assert depth <= 4

    def _check_ints(item: object) -> None:
        if isinstance(item, int) and not isinstance(item, bool):
            assert -(2**53) <= item <= 2**53
        elif isinstance(item, list):
            for sub in item:
                _check_ints(sub)
        elif isinstance(item, dict):
            for k, val in item.items():
                assert isinstance(k, str)
                _check_ints(val)

    _check_ints(v)


@settings(derandomize=True, database=None, max_examples=50)
@given(v=json_values(max_depth=0))
def test_json_values_depth_zero(v: object) -> None:
    assert not isinstance(v, (list, dict))


@settings(derandomize=True, database=None, max_examples=100)
@given(v=json_values(allow_floats=True))
def test_json_values_with_floats(v: object) -> None:
    def _check_finite(item: object) -> None:
        if isinstance(item, float):
            assert not math.isnan(item)
            assert not math.isinf(item)
        elif isinstance(item, list):
            for sub in item:
                _check_finite(sub)
        elif isinstance(item, dict):
            for val in item.values():
                _check_finite(val)

    _check_finite(v)


@settings(derandomize=True, database=None, max_examples=200)
@given(dt=rfc3339_datetimes())
def test_rfc3339_acceptance(dt: str) -> None:
    assert RFC3339_REGEX.match(dt) is not None
    parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    assert 1970 <= parsed.year <= 2100


@settings(derandomize=True, database=None, max_examples=100)
@given(dt=rfc3339_datetimes(offsets=False))
def test_rfc3339_no_offsets(dt: str) -> None:
    assert RFC3339_REGEX.match(dt) is not None
    assert dt.endswith("Z")


@settings(derandomize=True, database=None, max_examples=200)
@given(s=slugs())
def test_slugs_acceptance(s: str) -> None:
    assert SLUG_REGEX.match(s) is not None
    assert 1 <= len(s) <= 40


@settings(derandomize=True, database=None, max_examples=50)
@given(s=slugs(min_size=15, max_size=15))
def test_slugs_exact_size(s: str) -> None:
    assert SLUG_REGEX.match(s) is not None
    assert len(s) == 15


def test_determinism_under_derandomize() -> None:
    # Determinism across two test runs with derandomize=True
    slug_strat = slugs(min_size=5, max_size=15)
    run1: list[str] = []
    run2: list[str] = []

    current_run = run1

    @settings(derandomize=True, database=None, max_examples=200)
    @given(s=slug_strat)
    def _collect(s: str) -> None:
        current_run.append(s)

    _collect()
    current_run = run2
    _collect()
    assert len(run1) == 200
    assert run1 == run2
