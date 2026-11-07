# Security Notes

## Threat Model

This package is a pure Python library with no I/O operations. It does not perform network requests or file system access.

- Defended: Malformed strategy configuration is caught eagerly. Parameters passed to strategy factories are validated at call time, preventing invalid states.
- Not Defended: This library does not validate the security of the actual data generated (e.g., it produces strings that are syntactically valid but potentially malicious content for injection attacks). The user is responsible for sanitizing outputs in their specific context.

## Limits

Validation of strategy arguments (e.g., `max_length < 6` for emails) happens before any example generation occurs. Calling a strategy with invalid parameters raises `PropertyStrategiesError` immediately.