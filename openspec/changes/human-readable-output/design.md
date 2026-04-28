## Context

The system uses Python's standard `logging` module. Currently, both file and console handlers share the same `logging.Formatter` instance, which includes timestamps and metadata. While useful for log files, this makes terminal output verbose and less readable for standard progress updates.

## Goals / Non-Goals

**Goals:**
- Implement level-dependent formatting for the console handler.
- Simplify console output for INFO messages to improve user experience.
- Maintain detailed metadata for WARNING and higher levels in the console.
- Ensure file logs remain detailed for all levels.

**Non-Goals:**
- Changing the logging levels themselves.
- Changing the structure of file logs.

## Decisions

### Custom Formatter for Console
We will implement a `HumanReadableFormatter` class in `aur_python_packer/logger.py` that inherits from `logging.Formatter`.

- **Rationale**: Standard `logging.Formatter` does not support level-dependent formatting out of the box for a single handler. A custom formatter allows us to dynamically choose the format string based on the `record.levelno`.
- **Alternatives**: 
    - Using separate handlers for INFO and WARNING+: This would be more complex to manage and might lead to duplicated messages if not handled carefully with filters.
    - Modifying the record in a filter: Possible, but less "correct" than a custom formatter.

### Formatter Implementation Detail
The `HumanReadableFormatter` will hold two internal `logging.Formatter` instances: one for INFO and one for WARNING+. The `format()` method will delegate to the appropriate internal formatter based on the record level.

## Risks / Trade-offs

- **[Risk]** Complexity of custom formatter → **Mitigation**: Keep the implementation simple and well-tested. Use delegation to standard formatters to ensure stability.
