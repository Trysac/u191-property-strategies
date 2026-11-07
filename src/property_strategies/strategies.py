"""Hypothesis search strategies for structured data."""

from __future__ import annotations

import calendar
import string
from collections.abc import Sequence
from typing import Any

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from property_strategies.errors import PropertyStrategiesError

_LOCAL_CHARS_PLUS = string.ascii_letters + string.digits + "_%+-"
_LOCAL_CHARS_NO_PLUS = string.ascii_letters + string.digits + "_%-"
_LOWER_ALPHANUM = string.ascii_lowercase + string.digits
_HEX_UPPER = "0123456789ABCDEF"


def _validate_length(value: int, name: str, min_val: int) -> None:
    if value < min_val:
        raise PropertyStrategiesError(
            f"{name} must be at least {min_val}, got {value}",
            code="invalid_argument",
        )


def emails(*, max_length: int = 254, allow_plus: bool = True) -> SearchStrategy[str]:
    r"""Generate valid email addresses by construction without stalling.

    Matches regex:
    ^[A-Za-z0-9_%+-]+(\.[A-Za-z0-9_%+-]+)*@([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$
    Local part <= 64 characters, total length <= max_length (default 254, min 6).
    """
    _validate_length(max_length, "max_length", 6)

    allowed_chars = _LOCAL_CHARS_PLUS if allow_plus else _LOCAL_CHARS_NO_PLUS

    @st.composite
    def _domain_label(draw: st.DrawFn, max_chars: int) -> str:
        if max_chars < 1:
            return draw(st.text(_LOWER_ALPHANUM, min_size=1, max_size=1))
        cap = min(63, max_chars)
        size = draw(st.integers(min_value=1, max_value=cap))
        if size == 1:
            return draw(st.sampled_from(list(_LOWER_ALPHANUM)))
        if size == 2:
            c1 = draw(st.sampled_from(list(_LOWER_ALPHANUM)))
            c2 = draw(st.sampled_from(list(_LOWER_ALPHANUM)))
            return c1 + c2
        c_start = draw(st.sampled_from(list(_LOWER_ALPHANUM)))
        mid_chars = _LOWER_ALPHANUM + "-"
        mid = draw(st.text(mid_chars, min_size=size - 2, max_size=size - 2))
        c_end = draw(st.sampled_from(list(_LOWER_ALPHANUM)))
        return f"{c_start}{mid}{c_end}"

    @st.composite
    def _email(draw: st.DrawFn) -> str:
        # Local part: 1..64 chars
        max_local_budget = min(64, max_length - 5)  # min domain is a.bc (4 chars) + @ (1 char) = 5
        local_len = draw(st.integers(min_value=1, max_value=max_local_budget))

        # Build dotted atoms that sum to local_len including dots
        atoms: list[str] = []
        remaining = local_len
        while remaining > 0:
            # We can stop anytime if remaining is consumed
            is_last = draw(st.booleans()) if remaining > 2 else True
            if is_last:
                atom_len = remaining
            else:
                atom_len = draw(st.integers(min_value=1, max_value=max(1, remaining - 2)))
            atoms.append(draw(st.text(allowed_chars, min_size=atom_len, max_size=atom_len)))
            remaining -= atom_len
            if remaining > 0:
                remaining -= 1  # for the dot
        local_part = ".".join(atoms)

        # Remaining budget for domain: max_length - len(local_part) - 1 ('@')
        domain_budget = max_length - len(local_part) - 1
        # TLD: 2..min(63, domain_budget - 2) (since at least one sub-label + '.' >= 2 chars)
        max_tld_len = min(63, domain_budget - 2)
        tld_len = draw(st.integers(min_value=2, max_value=max_tld_len))
        tld = draw(st.text(string.ascii_lowercase, min_size=tld_len, max_size=tld_len))
        subdomain_budget = domain_budget - tld_len - 1  # 1 for dot before TLD

        # Build 1 or more sublabels within subdomain_budget
        sublabels: list[str] = []
        rem_sub = subdomain_budget
        while rem_sub > 0:
            is_last = draw(st.booleans()) if rem_sub > 2 else True
            if is_last:
                lbl_len = draw(st.integers(min_value=1, max_value=min(63, rem_sub)))
                lbl = draw(_domain_label(lbl_len))
                sublabels.append(lbl)
                break
            else:
                lbl_len = draw(st.integers(min_value=1, max_value=min(63, rem_sub - 2)))
                lbl = draw(_domain_label(lbl_len))
                sublabels.append(lbl)
                rem_sub -= len(lbl) + 1  # label + dot

        domain_part = ".".join(sublabels) + "." + tld
        return f"{local_part}@{domain_part}"

    return _email()


def http_urls(
    *,
    schemes: Sequence[str] = ("http", "https"),
    max_length: int = 2048,
) -> SearchStrategy[str]:
    """Generate valid HTTP/HTTPS URLs satisfying RFC 3986 and standard split/unsplit round-trip."""
    valid_schemes = ("http", "https")
    if not schemes:
        raise PropertyStrategiesError("schemes must not be empty", code="invalid_argument")
    for s in schemes:
        if s not in valid_schemes:
            raise PropertyStrategiesError(
                f"invalid scheme {s!r}; must be subset of ('http', 'https')",
                code="invalid_argument",
            )
    _validate_length(max_length, "max_length", 16)

    # Unreserved: ALPHA / DIGIT / "-" / "." / "_" / "~"
    unreserved = string.ascii_letters + string.digits + "-._~"
    # Sub-delims
    sub_delims = "!$&'()*+,;="
    pchar_allowed = unreserved + sub_delims + ":@"
    query_allowed = pchar_allowed + "/?"

    pct_strat = st.sampled_from([f"%{a}{b}" for a in _HEX_UPPER for b in _HEX_UPPER])

    pchar_token_strat = st.one_of(st.sampled_from(list(pchar_allowed)), pct_strat)
    query_token_strat = st.one_of(st.sampled_from(list(query_allowed)), pct_strat)

    ipv4_strat = st.tuples(
        st.integers(0, 255),
        st.integers(0, 255),
        st.integers(0, 255),
        st.integers(0, 255),
    ).map(lambda octets: ".".join(str(o) for o in octets))

    @st.composite
    def _named_host(draw: st.DrawFn) -> str:
        num_labels = draw(st.integers(min_value=1, max_value=3))
        labels: list[str] = []
        for _ in range(num_labels):
            sz = draw(st.integers(min_value=1, max_value=10))
            if sz == 1:
                labels.append(draw(st.sampled_from(list(_LOWER_ALPHANUM))))
            else:
                c_start = draw(st.sampled_from(list(_LOWER_ALPHANUM)))
                c_end = draw(st.sampled_from(list(_LOWER_ALPHANUM)))
                mid = (
                    draw(st.text(_LOWER_ALPHANUM + "-", min_size=sz - 2, max_size=sz - 2))
                    if sz > 2
                    else ""
                )
                labels.append(f"{c_start}{mid}{c_end}")
        tld = draw(st.text(string.ascii_lowercase, min_size=2, max_size=6))
        labels.append(tld)
        return ".".join(labels)

    host_strat = st.one_of(_named_host(), ipv4_strat)

    @st.composite
    def _url(draw: st.DrawFn) -> str:
        scheme = draw(st.sampled_from(list(schemes)))
        host = draw(host_strat)
        has_port = draw(st.booleans())
        port_str = f":{draw(st.integers(1, 65535))}" if has_port else ""
        prefix = f"{scheme}://{host}{port_str}"

        budget = max_length - len(prefix)
        if budget < 0:
            # Host/prefix exceeded length, shrink host
            host = "example.com"
            prefix = f"{scheme}://{host}"
            budget = max_length - len(prefix)

        # Optional path segments
        num_segments = draw(st.integers(min_value=0, max_value=4))
        segments: list[str] = []
        cur_len = 0
        for _ in range(num_segments):
            seg_len = draw(st.integers(min_value=0, max_value=8))
            tokens = [draw(pchar_token_strat) for _ in range(seg_len)]
            seg = "".join(tokens)
            if cur_len + len(seg) + 1 > budget:
                break
            segments.append(seg)
            cur_len += len(seg) + 1

        path = "/" + "/".join(segments) if segments else ("/" if draw(st.booleans()) else "")
        budget_after_path = max_length - len(prefix) - len(path)

        has_query = draw(st.booleans()) and budget_after_path > 1
        if has_query:
            max_q_tokens = min(10, (budget_after_path - 1) // 3)
            num_q_tokens = draw(st.integers(min_value=1, max_value=max(1, max_q_tokens)))
            q_tokens = [draw(query_token_strat) for _ in range(num_q_tokens)]
            q_str = "".join(q_tokens)
            query = f"?{q_str}" if len(q_str) + 1 <= budget_after_path else ""
        else:
            query = ""

        res = f"{prefix}{path}{query}"
        return res[:max_length] if len(res) > max_length else res

    return _url()


def semvers(*, prerelease: bool = True, build: bool = True) -> SearchStrategy[str]:
    """Generate semantic version strings per SemVer 2.0.0 specification."""
    # Numeric identifiers must not contain leading zeros
    num_id_strat = st.integers(min_value=0, max_value=9999).map(str)

    # Prerelease identifier: numeric (no leading zero) or non-numeric (contains letter/hyphen)
    alpha_num_hyphen = string.ascii_letters + string.digits + "-"
    non_numeric_token = st.text(alpha_num_hyphen, min_size=1, max_size=10).filter(
        lambda s: not s.isdigit()
    )
    pre_id = st.one_of(num_id_strat, non_numeric_token)

    # Build identifier: [0-9A-Za-z-]+ (leading zeros allowed for build identifiers)
    build_id = st.text(alpha_num_hyphen, min_size=1, max_size=10)

    @st.composite
    def _semver(draw: st.DrawFn) -> str:
        major = draw(num_id_strat)
        minor = draw(num_id_strat)
        patch = draw(num_id_strat)
        core = f"{major}.{minor}.{patch}"

        pre_part = ""
        if prerelease and draw(st.booleans()):
            num_pre = draw(st.integers(min_value=1, max_value=3))
            pre_ids = [draw(pre_id) for _ in range(num_pre)]
            pre_part = f"-{'.'.join(pre_ids)}"

        build_part = ""
        if build and draw(st.booleans()):
            num_b = draw(st.integers(min_value=1, max_value=3))
            b_ids = [draw(build_id) for _ in range(num_b)]
            build_part = f"+{'.'.join(b_ids)}"

        return f"{core}{pre_part}{build_part}"

    return _semver()


def json_values(
    *,
    max_depth: int = 4,
    max_leaves: int = 50,
    allow_floats: bool = True,
) -> SearchStrategy[object]:
    """Generate JSON serializable values respecting depth and leaf constraints."""
    _validate_length(max_depth, "max_depth", 0)
    _validate_length(max_leaves, "max_leaves", 1)

    max_int = 2**53
    min_int = -(2**53)

    scalars: list[SearchStrategy[Any]] = [
        st.none(),
        st.booleans(),
        st.integers(min_value=min_int, max_value=max_int),
        st.text(min_size=0, max_size=50),
    ]
    if allow_floats:
        scalars.append(st.floats(allow_nan=False, allow_infinity=False, width=64))

    scalar_strat = st.one_of(scalars)

    if max_depth == 0:
        return scalar_strat

    @st.composite
    def _bounded_json(draw: st.DrawFn) -> object:
        leaves_left = max_leaves

        def _gen(cur_depth: int) -> object:
            nonlocal leaves_left
            if cur_depth >= max_depth or leaves_left <= 1:
                leaves_left = max(0, leaves_left - 1)
                return draw(scalar_strat)

            # Choose scalar, list, or dict
            kind = draw(st.sampled_from(["scalar", "list", "dict"]))
            if kind == "scalar":
                leaves_left = max(0, leaves_left - 1)
                return draw(scalar_strat)

            if kind == "list":
                count = draw(st.integers(min_value=0, max_value=min(5, leaves_left)))
                res_list: list[object] = []
                for _ in range(count):
                    if leaves_left <= 0:
                        break
                    res_list.append(_gen(cur_depth + 1))
                return res_list

            # kind == "dict"
            count = draw(st.integers(min_value=0, max_value=min(5, leaves_left)))
            res_dict: dict[str, object] = {}
            for _ in range(count):
                if leaves_left <= 0:
                    break
                key = draw(st.text(min_size=0, max_size=15))
                res_dict[key] = _gen(cur_depth + 1)
            return res_dict

        return _gen(0)

    return _bounded_json()


def rfc3339_datetimes(
    *,
    min_year: int = 1970,
    max_year: int = 2100,
    offsets: bool = True,
) -> SearchStrategy[str]:
    """Generate RFC 3339 compliant ISO datetime strings."""
    if min_year > max_year:
        raise PropertyStrategiesError(
            f"min_year ({min_year}) must be <= max_year ({max_year})",
            code="invalid_argument",
        )
    _validate_length(min_year, "min_year", 1)

    @st.composite
    def _dt(draw: st.DrawFn) -> str:
        year = draw(st.integers(min_value=min_year, max_value=max_year))
        month = draw(st.integers(min_value=1, max_value=12))
        max_days = calendar.monthrange(year, month)[1]
        day = draw(st.integers(min_value=1, max_value=max_days))

        hour = draw(st.integers(min_value=0, max_value=23))
        minute = draw(st.integers(min_value=0, max_value=59))
        second = draw(st.integers(min_value=0, max_value=59))

        has_frac = draw(st.booleans())
        if has_frac:
            num_digits = draw(st.integers(min_value=1, max_value=6))
            frac_digits = draw(st.text(string.digits, min_size=num_digits, max_size=num_digits))
            frac_part = f".{frac_digits}"
        else:
            frac_part = ""

        if offsets and draw(st.booleans()):
            offset_sign = draw(st.sampled_from(["+", "-"]))
            off_hour = draw(st.integers(min_value=0, max_value=23))
            off_min = draw(st.integers(min_value=0, max_value=59))
            tz_part = f"{offset_sign}{off_hour:02d}:{off_min:02d}"
        else:
            tz_part = "Z"

        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        return f"{date_str}T{time_str}{frac_part}{tz_part}"

    return _dt()


def slugs(*, min_size: int = 1, max_size: int = 40) -> SearchStrategy[str]:
    """Generate URL slug strings matching ^[a-z0-9]+(-[a-z0-9]+)*$."""
    _validate_length(min_size, "min_size", 1)
    if max_size < min_size:
        raise PropertyStrategiesError(
            f"max_size ({max_size}) must be >= min_size ({min_size})",
            code="invalid_argument",
        )

    @st.composite
    def _slug(draw: st.DrawFn) -> str:
        target_len = draw(st.integers(min_value=min_size, max_value=max_size))
        # We build alternating words separated by single '-'
        # Each word is 1 or more chars from [a-z0-9]
        words: list[str] = []
        rem = target_len
        while rem > 0:
            if rem == 1:
                words.append(draw(st.sampled_from(list(_LOWER_ALPHANUM))))
                break
            if rem == 2:
                # 2 chars in one word; two words impossible (need >= 3 chars: word + '-' + word)
                words.append(draw(st.text(_LOWER_ALPHANUM, min_size=2, max_size=2)))
                break
            # rem >= 3
            is_last = draw(st.booleans())
            if is_last:
                words.append(draw(st.text(_LOWER_ALPHANUM, min_size=rem, max_size=rem)))
                break
            else:
                # If not last, next word needs at least 1 char and 1 separator (2 chars reserved)
                w_len = draw(st.integers(min_value=1, max_value=rem - 2))
                words.append(draw(st.text(_LOWER_ALPHANUM, min_size=w_len, max_size=w_len)))
                rem -= w_len + 1
        return "-".join(words)

    return _slug()
