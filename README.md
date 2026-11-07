# property-strategies

[![PyPI version](https://img.shields.io/pypi/v/trysac-property-strategies)](https://pypi.org/project/trysac-property-strategies/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-property-strategies)](LICENSE)
[![CI](https://github.com/Trysac/u191-property-strategies/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u191-property-strategies/actions/workflows/ci.yml)

Hypothesis strategies for common data that always satisfy their format: emails, http URLs, semver, JSON values, RFC 3339 datetimes and slugs

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-property-strategies
# or
uv add trysac-property-strategies
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import property_strategies

# normalize() trims surrounding whitespace and lower-cases the text.
print(property_strategies.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    property_strategies.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
