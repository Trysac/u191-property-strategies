# property-strategies

Property-based tests frequently require complex inputs like URLs, emails, or version strings. Standard generators often produce inputs that fail validation logic, or they require filtering that causes tests to stall. This library provides deterministic Hypothesis strategies that generate valid data by construction.

## Installation

```bash
pip install property-strategies
```

## Usage Example

```python
from hypothesis import given
from property_strategies import emails, http_urls, semvers


@given(email=emails(), url=http_urls(), version=semvers())
def test_my_service(email: str, url: str, version: str) -> None:
    assert "@" in email
    assert url.startswith(("http://", "https://"))
    assert len(version.split(".")) == 3
```

## Public API

Exports:
- `emails(*, max_length: int = 254, allow_plus: bool = True) -> SearchStrategy[str]`
- `http_urls(*, schemes: Sequence[str] = ("http", "https"), max_length: int = 2048) -> SearchStrategy[str]`
- `semvers(*, prerelease: bool = True, build: bool = True) -> SearchStrategy[str]`
- `json_values(*, max_depth: int = 4, max_leaves: int = 50, allow_floats: bool = True) -> SearchStrategy[object]`
- `rfc3339_datetimes(*, min_year: int = 1970, max_year: int = 2100, offsets: bool = True) -> SearchStrategy[str]`
- `slugs(*, min_size: int = 1, max_size: int = 40) -> SearchStrategy[str]`
- `PropertyStrategiesError`: Raised for invalid configuration (code: "invalid_argument").

## Why not existing generators?

Standard libraries like `hypothesis.strategies.emails` often generate email formats that common validation regexes reject, or they lack constraints like maximum lengths. This library strictly enforces RFC-compliant constraints by construction, preventing stall conditions during testing.

## Security

See [docs/SECURITY.md](docs/SECURITY.md).