# Testing

## Existing Tests

- `tests/test_property_strategies.py`: Verifies package versioning and ensures the library version is exposed correctly.
- `tests/test_strategies.py`: Covers the full behavioral testing of the six strategies. It includes tests for validation error handling (e.g., ensuring `PropertyStrategiesError` is raised for invalid inputs) and property checks to ensure outputs adhere to specific regex patterns and standard library parsing (e.g., `datetime.fromisoformat` or `urlsplit`).