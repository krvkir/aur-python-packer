## Why

The current console output is cluttered with logging preambles (timestamps, log levels, logger names) for every message, including high-frequency INFO messages. This reduces readability and makes it harder for users to quickly scan the primary progress of the tool.

## What Changes

- Simplify console output for INFO messages by removing the preamble.
- Implement a minimal preamble (`[LEVEL] LoggerName: message`) for WARNING, ERROR, and CRITICAL messages in the console to ensure they remain distinct and noticeable.
- Maintain the full preamble (including timestamps) for all log levels in the log files to ensure complete diagnostic information is preserved.
- **BREAKING**: None. This only changes the presentation of logs in the terminal.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `system-diagnostics`: Update the terminal logging requirement to specify different formats for INFO vs WARNING+ levels.

## Impact

- `aur_python_packer/logger.py`: Implementation of a custom formatter and update to the console handler setup.
- User Experience: Cleaner terminal output while maintaining detailed file logs.
