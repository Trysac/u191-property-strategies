# Strategy generation by construction over post-filtering

Status: accepted (generated, pending human review)

## Context

Hypothesis strategies configured with heavy post-generation filtering (`.filter(...)`) frequently trigger health check warnings (`HypothesisWarning: Could not find any valid examples`) and stall when searching for constrained formats like maximum-length emails, calendar-valid datetimes, or bounded JSON values.

## Decision

Construct all structured string types (emails, URLs, slugs, datetimes, semvers) directly from composited sub-generators that enforce structural constraints and length boundaries during generation.

## Consequences

Zero filter-stall during test runs; deterministic execution and reliable test coverage across arbitrary seed parameters.
