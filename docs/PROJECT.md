# Project Record

## Objective

Provide Hypothesis search strategies for structured data formats (emails, http URLs, semver, JSON values, RFC 3339 datetimes, and slugs) that satisfy their specifications by construction.

## Scope

- The implementation of the six public strategies defined in the public API.
- The custom `PropertyStrategiesError` type.
- Type annotations and strict validation of strategy parameters.

## Out of Scope

- Internationalized emails and domain names.
- IPv6 host support.
- Generator engines for non-testing purposes.
- Data generators for CSV exports or Faker-style realistic profile data.

## Factory run u191 (measured from API usage)

| Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|
| generation | gemini-3.8-flash | yes | 4538 | 10630 | 0 | 0 | 0.0216 |
| fix-1 | gemini-3.8-flash | no | 79080 | 3084 | 0 | 583666 | 0.1146 |
| fix-2 | gemini-3.8-flash | no | 52782 | 3335 | 0 | 275594 | 0.0728 |
| fix-3 | gemini-3.8-flash | no | 65575 | 1359 | 0 | 389917 | 0.0835 |
| fix-4 | gemini-3.8-flash | no | 56750 | 915 | 0 | 356620 | 0.0727 |
| audit | gemini-3.1-flash-lite | no | 34583 | 463 | 0 | 38614 | 0.0103 |
| docs | gemini-3.1-flash-lite | no | 178555 | 1083 | 0 | 0 | 0.0463 |

Total: $0.4219. Prices: Anthropic list prices.
