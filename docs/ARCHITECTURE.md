# Architecture

`property_strategies` provides production-grade `hypothesis.strategies.SearchStrategy` generators for standard data types commonly encountered in web services, APIs, and systems engineering.

## Goals

- **Correctness by Construction**: Never rely on naive regular expression filtering that causes Hypothesis generation to stall or exhaust drawing attempts.
- **Spec Conformance**: Guarantee that generated values satisfy published standards (RFC 3986, RFC 3339, SemVer 2.0.0, RFC 5322 / HTML5 email subset).
- **Strict Validation**: Fail eagerly at strategy instantiation time with `PropertyStrategiesError` (code: `invalid_argument`) if parameters are out of range or contradictory.

## Strategies Overview

1. `emails(*, max_length: int = 254, allow_plus: bool = True) -> SearchStrategy[str]`:
   Constructs local atoms joined by single dots, bounded domain labels not starting or ending with hyphens, and a 2-63 character ASCII top-level domain.
2. `http_urls(*, schemes: Sequence[str] = ('http', 'https'), max_length: int = 2048) -> SearchStrategy[str]`:
   Builds standard RFC 3986 URLs round-trippable via Python's standard `urllib.parse.urlsplit` and `urlunsplit`.
3. `semvers(*, prerelease: bool = True, build: bool = True) -> SearchStrategy[str]`:
   Follows Semantic Versioning 2.0.0, ensuring numeric components do not have leading zeros.
4. `json_values(*, max_depth: int = 4, max_leaves: int = 50, allow_floats: bool = True) -> SearchStrategy[object]`:
   Recursively constructs JSON structures with finite floats and integers within IEEE-754 53-bit safe integer bounds.
5. `rfc3339_datetimes(*, min_year: int = 1970, max_year: int = 2100, offsets: bool = True) -> SearchStrategy[str]`:
   Constructs valid calendar dates, accounting for leap years and month boundaries.
6. `slugs(*, min_size: int = 1, max_size: int = 40) -> SearchStrategy[str]`:
   Generates non-empty lower-case alphanumeric tokens joined by single hyphens.
