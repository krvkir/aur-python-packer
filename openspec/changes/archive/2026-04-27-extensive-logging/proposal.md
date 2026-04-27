## Why

Currently, the tool relies on simple `print` statements and direct `subprocess.run` calls, making it difficult to debug failures, especially in complex dependency chains or long-running builds. We need a systematic way to capture internal decisions and external command execution details (outputs, exit codes, environment) in a persistent log file while maintaining a clean, informative terminal interface.

## What Changes

- **Extensive Logging**: Implement a dual-output logging system using the standard `logging` module.
- **Detailed Log Files**: Every run generates a timestamped log file in a `logs/` subdirectory of the work directory, capturing `DEBUG` level messages and above.
- **Terminal Progress**: High-level progress (`INFO` level and above) is streamed to the terminal.
- **Command Instrumentation**: All external command executions (pacman, makepkg, git, etc.) are wrapped to log their full invocation details and merged stdout/stderr output.
- **Decision Tracking**: Key architectural decisions (dependency resolution paths, build tier selection, OS detection) are explicitly logged.

## Capabilities

### New Capabilities
- `logging-system`: Provides the infrastructure for dual-output logging, directory management, and standardized log formatting.
- `command-execution-logging`: A robust wrapper for external commands that captures merged output, logs environment overrides, and tracks execution state.

### Modified Capabilities
- `cli-interface`: Update to initialize the logging system and report the log file location to the user.
- `chroot-builder`: Update to use the new command execution wrapper for build tools.

## Impact

- All modules (`main.py`, `builder.py`, `resolver.py`, `generator.py`, `repo.py`) will be refactored to use `logging` instead of `print`.
- Subprocess management will be centralized to ensure consistent logging of external actions.
- A new `logs/` directory will be created in the user's working directory.
